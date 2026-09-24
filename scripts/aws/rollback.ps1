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
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^sha256:[a-fA-F0-9]{64}$')]
    [string]$PreviousBackendImageDigest,
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^sha256:[a-fA-F0-9]{64}$')]
    [string]$PreviousFrontendImageDigest,
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9]{12}\.dkr\.ecr\.us-east-1\.amazonaws\.com$')]
    [string]$EcrRegistryUri,
    [Parameter(Mandatory = $true)]
    [string]$PrivateKeyPath,
    [switch]$ExecuteRollback,
    [switch]$ConfirmRollback
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'common.ps1')

try {
    if ($ConfirmRollback -and -not $ExecuteRollback) { throw 'ConfirmRollback applies only to ExecuteRollback.' }
    if ($ExecuteRollback -and -not $ConfirmRollback) { throw 'Rollback requires -ExecuteRollback and -ConfirmRollback.' }
    if (-not (Test-Path -LiteralPath $PrivateKeyPath -PathType Leaf)) { throw 'SSH private key file is missing.' }
    Import-M7AwsEnvironment
    $identity = Assert-M7AwsSession
    if ($EcrRegistryUri.Split('.')[0] -ne [string]$identity.Account) { throw 'ECR registry account differs from STS.' }
    $instances = Invoke-M7AwsJson -Arguments @('ec2','describe-instances','--instance-ids',$InstanceId)
    $instance = @($instances.Reservations.Instances)[0]
    if (-not $instance -or $instance.State.Name -ne 'running' -or -not $instance.PublicIpAddress -or -not $instance.KeyName) { throw 'Target must be a running, public EC2 with a key pair.' }
    $repos = Invoke-M7AwsJson -Arguments @('ecr','describe-repositories','--repository-names','m7-g05-backend','m7-g05-frontend')
    if (@($repos.Repositories).Count -ne 2 -or @($repos.Repositories | Where-Object { $_.ImageTagMutability -ne 'IMMUTABLE' }).Count) { throw 'Rollback repositories must enforce immutable tags.' }
    foreach ($item in @(@{Name='m7-g05-backend';Tag=$PreviousBackendImageTag;Digest=$PreviousBackendImageDigest},@{Name='m7-g05-frontend';Tag=$PreviousFrontendImageTag;Digest=$PreviousFrontendImageDigest})) {
        $images = Invoke-M7AwsJson -Arguments @('ecr','describe-images','--repository-name',$item.Name,'--image-ids',"imageTag=$($item.Tag)")
        if (@($images.ImageDetails).Count -ne 1 -or $images.ImageDetails[0].ImageDigest -ne $item.Digest) { throw "Rollback tag/digest mismatch in $($item.Name)." }
    }
    Write-Output 'Read-only rollback preflight passed: target running, SSH key assigned, immutable ECR tags/digests match.'
    if (-not $ExecuteRollback) { Write-Output 'No remote command executed.'; return }
    $ssh = Get-Command ssh -ErrorAction SilentlyContinue
    if (-not $ssh) { throw 'OpenSSH client is required.' }
    $target = 'ubuntu@' + $instance.PublicIpAddress
    if ($PSCmdlet.ShouldProcess($target, 'Run m7-rollback over SSH')) {
        & $ssh.Source -i $PrivateKeyPath -o BatchMode=yes -o StrictHostKeyChecking=yes $target "sudo /usr/local/bin/m7-rollback $PreviousBackendImageTag $PreviousFrontendImageTag"
        if ($LASTEXITCODE -ne 0) { throw 'SSH rollback failed. Inspect target via SSH.' }
        Write-Output 'Rollback command completed. Verify /health and both container health states.'
    }
} catch {
    if ($_.Exception.Message -eq 'CREDENTIALS_EXPIRED') { Write-Error 'STATUS: CREDENCIAIS_EXPIRADAS.'; exit 3 }
    Write-Error $_.Exception.Message
    exit 1
}
