[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^i-[a-fA-F0-9]{8,17}$')]
    [string]$InstanceId,
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-fA-F0-9]{40}$')]
    [string]$PreviousBackendImageTag,
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-fA-F0-9]{40}$')]
    [string]$PreviousFrontendImageTag,
    [string]$EcrRegistryUri,
    [switch]$ExecuteRollback,
    [switch]$ConfirmRollback
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'common.ps1')

try {
    if ($ConfirmRollback -and -not $ExecuteRollback) {
        throw 'ConfirmRollback is valid only with ExecuteRollback.'
    }
    if ($ExecuteRollback -and -not $ConfirmRollback) {
        throw 'Rollback is guarded: pass both -ExecuteRollback and -ConfirmRollback.'
    }
    if ($ExecuteRollback -and [string]::IsNullOrWhiteSpace($EcrRegistryUri)) {
        throw 'EcrRegistryUri is required when executing rollback.'
    }

    Import-M7AwsEnvironment
    $null = Assert-M7AwsSession
    Write-Output 'AWS STS: valid; region: us-east-1.'

    $managed = Invoke-M7AwsJson -Arguments @(
        'ssm', 'describe-instance-information', '--filters', "Key=InstanceIds,Values=$InstanceId"
    )
    $managedInstance = @($managed.InstanceInformationList | Where-Object {
        $_.InstanceId -eq $InstanceId -and $_.PingStatus -eq 'Online'
    })
    if ($managedInstance.Count -ne 1) {
        throw 'The target EC2 instance is not an online SSM managed node.'
    }

    if ($EcrRegistryUri) {
        if ($EcrRegistryUri -notmatch '^[0-9]{12}\.dkr\.ecr\.us-east-1\.amazonaws\.com$') {
            throw 'EcrRegistryUri must be a private us-east-1 registry URI.'
        }
        $repositories = @('m7-g05-backend', 'm7-g05-frontend')
        $null = Invoke-M7AwsJson -Arguments (@('ecr', 'describe-repositories', '--repository-names') + $repositories)
        foreach ($pair in @(
            @{ Name = 'm7-g05-backend'; Tag = $PreviousBackendImageTag },
            @{ Name = 'm7-g05-frontend'; Tag = $PreviousFrontendImageTag }
        )) {
            $images = Invoke-M7AwsJson -Arguments @(
                'ecr', 'describe-images', '--repository-name', $pair.Name,
                '--image-ids', "imageTag=$($pair.Tag)"
            )
            if (@($images.ImageDetails).Count -ne 1) {
                throw "Previous immutable tag is missing from ECR repository $($pair.Name)."
            }
        }
    }

    Write-Output 'SSM target and previous immutable image tag: valid.'
    if ($ExecuteRollback -and $PSCmdlet.ShouldProcess("EC2 $InstanceId", 'Rollback backend and frontend image tags')) {
        $parameterPath = Join-Path ([IO.Path]::GetTempPath()) ("m7-g05-ssm-{0}.json" -f [guid]::NewGuid().ToString('N'))
        try {
            $parameters = @{
                commands = @("/usr/local/bin/m7-rollback $PreviousBackendImageTag $PreviousFrontendImageTag")
            } | ConvertTo-Json -Compress
            [IO.File]::WriteAllText($parameterPath, $parameters, [Text.UTF8Encoding]::new($false))
            $parameterUri = 'file://' + $parameterPath.Replace('\', '/')
            $result = Invoke-M7AwsJson -Arguments @(
                'ssm', 'send-command', '--instance-ids', $InstanceId,
                '--document-name', 'AWS-RunShellScript',
                '--comment', 'M7/g05 image rollback',
                '--parameters', $parameterUri,
                '--timeout-seconds', '600'
            )
            Write-Output "SSM rollback command submitted: $($result.Command.CommandId)."
        } finally {
            if (Test-Path -LiteralPath $parameterPath) {
                Remove-Item -LiteralPath $parameterPath -Force
            }
        }
    } else {
        Write-Output 'Read-only rollback preflight complete; no SSM command was submitted.'
    }
} catch {
    if ($_.Exception.Message -eq 'CREDENTIALS_EXPIRED') {
        Write-Error 'STATUS: CREDENCIAIS_EXPIRADAS. No further AWS operations were attempted.'
        exit 3
    }
    if ($_.Exception.Message -eq 'AWS_ACCESS_DENIED') {
        Write-Error 'AWS_ACCESS_DENIED: the current identity lacks permission for a read-only preflight action.'
        exit 4
    }
    Write-Error $_.Exception.Message
    exit 1
}
