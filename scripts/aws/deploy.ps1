[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [ValidateSet('Preflight', 'CreateChangeSet', 'InspectChangeSet', 'ExecuteChangeSet')]
    [string]$Action = 'Preflight',
    [string]$StackName = 'm7-g05-mvp',
    [string]$ChangeSetName,
    [string]$VpcId,
    [string]$SubnetId,
    [string]$AmiId,
    [ValidateSet('t3.large', 't3.xlarge')]
    [string]$InstanceType = 't3.large',
    [ValidateRange(50, 100)]
    [int]$RootVolumeSize = 50,
    [string]$InstanceProfileName,
    [ValidatePattern('^[0-9]{12}\.dkr\.ecr\.us-east-1\.amazonaws\.com$')]
    [string]$EcrRegistryUri,
    [ValidatePattern('^[a-fA-F0-9]{40}$')]
    [string]$BackendImageTag,
    [ValidatePattern('^[a-fA-F0-9]{40}$')]
    [string]$FrontendImageTag,
    [ValidatePattern('^sha256:[a-fA-F0-9]{64}$')]
    [string]$BackendImageDigest,
    [ValidatePattern('^sha256:[a-fA-F0-9]{64}$')]
    [string]$FrontendImageDigest,
    [string]$KeyPairName,
    [ValidatePattern('^((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])/32$')]
    [string]$OperatorSshCidr,
    [switch]$ConfirmExecution
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'common.ps1')

function Invoke-LocalGate {
    param([string]$Program, [string[]]$Arguments, [string]$Failure)
    $output = & $Program @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) { throw $Failure }
    return $output
}

function Assert-Inputs {
    if ($StackName -ne 'm7-g05-mvp') { throw 'Only the existing m7-g05-mvp stack is supported.' }
    if ($Action -in @('InspectChangeSet','ExecuteChangeSet')) {
        if ($ChangeSetName -notmatch '^m7-g05-ssh-[a-f0-9]{32}$') { throw 'Supply the exact generated ChangeSetName.' }
        return
    }
    foreach ($name in @('VpcId','SubnetId','AmiId','InstanceProfileName','EcrRegistryUri','BackendImageTag','FrontendImageTag','BackendImageDigest','FrontendImageDigest','KeyPairName','OperatorSshCidr')) {
        if ([string]::IsNullOrWhiteSpace((Get-Variable -Name $name -ValueOnly))) { throw "$name is required." }
    }
    if ($OperatorSshCidr -notmatch '^((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])/32$') { throw 'OperatorSshCidr must be IPv4 /32.' }
    $currentIp = ([string](Invoke-RestMethod -Uri 'https://checkip.amazonaws.com' -TimeoutSec 10)).Trim()
    if ($currentIp -notmatch '^((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$' -or "$currentIp/32" -ne $OperatorSshCidr) { throw 'OperatorSshCidr does not match the current public operator IPv4 /32.' }
    if ($BackendImageDigest -notmatch '^sha256:[a-fA-F0-9]{64}$' -or $FrontendImageDigest -notmatch '^sha256:[a-fA-F0-9]{64}$') { throw 'Both expected ECR digests are required.' }
}

function Assert-ChangeSet {
    param([Parameter(Mandatory = $true)][string]$ExpectedStackId)

    $change = Invoke-M7AwsJson -Arguments @('cloudformation','describe-change-set','--stack-name',$StackName,'--change-set-name',$ChangeSetName)
    if ($change.ChangeSetName -ne $ChangeSetName -or $change.StackName -ne $StackName -or $change.StackId -ne $ExpectedStackId -or $change.Status -ne 'CREATE_COMPLETE' -or $change.ExecutionStatus -ne 'AVAILABLE') { throw 'Change set is not available for the expected stack.' }
    $sshCidr = @($change.Parameters | Where-Object { $_.ParameterKey -eq 'OperatorSshCidr' })
    if ($sshCidr.Count -ne 1 -or $sshCidr[0].ParameterValue -notmatch '^((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])/32$') { throw 'Change set has no explicit valid OperatorSshCidr /32.' }
    $currentIp = ([string](Invoke-RestMethod -Uri 'https://checkip.amazonaws.com' -TimeoutSec 10)).Trim()
    if ("$currentIp/32" -ne $sshCidr[0].ParameterValue) { throw 'STALE_OPERATOR_SSH_CIDR: public operator IPv4 changed since change set creation. Stop and create a new change set.' }
    $changes = @($change.Changes)
    $unexpected = @($changes | Where-Object { $_.ResourceChange.LogicalResourceId -notin @('ApplicationInstance','ApplicationSecurityGroup') })
    if ($changes.Count -ne 2 -or $unexpected.Count) { throw 'Change set contains missing or unexpected resources.' }
    $instance = @($changes | Where-Object { $_.ResourceChange.LogicalResourceId -eq 'ApplicationInstance' })
    if ($instance.Count -ne 1 -or $instance[0].ResourceChange.Action -ne 'Modify' -or $instance[0].ResourceChange.Replacement -ne 'True') { throw 'Expected EC2 replacement is absent.' }
    if (-not @($instance[0].ResourceChange.Details | Where-Object { $_.Target.Name -eq 'KeyName' }).Count) { throw 'KeyName is not listed as the EC2 replacement cause.' }
    $securityGroup = @($changes | Where-Object { $_.ResourceChange.LogicalResourceId -eq 'ApplicationSecurityGroup' })
    if ($securityGroup.Count -ne 1 -or $securityGroup[0].ResourceChange.Action -ne 'Modify' -or $securityGroup[0].ResourceChange.Replacement -ne 'False') { throw 'Security Group change is missing or may replace the existing group.' }
    $securityGroupDetails = @($securityGroup[0].ResourceChange.Details | ForEach-Object { $_.Target.Name })
    if ($securityGroupDetails -contains 'GroupDescription' -or $securityGroupDetails -notcontains 'SecurityGroupIngress' -or $securityGroupDetails -notcontains 'SecurityGroupEgress') { throw 'Security Group change does not match the expected in-place ingress and egress update.' }
    return $change
}

function Assert-AwsInputs {
    param([string]$AccountId)

    if ($EcrRegistryUri.Split('.')[0] -ne $AccountId) {
        throw 'EcrRegistryUri account does not match the validated STS identity.'
    }
    $stack = Invoke-M7AwsJson -Arguments @('cloudformation','describe-stacks','--stack-name',$StackName)
    if (@($stack.Stacks).Count -ne 1 -or $stack.Stacks[0].StackStatus -ne 'CREATE_COMPLETE') { throw 'Existing stack must be CREATE_COMPLETE.' }
    $key = Invoke-M7AwsJson -Arguments @('ec2','describe-key-pairs','--key-names',$KeyPairName,'--include-public-key')
    if (@($key.KeyPairs).Count -ne 1) { throw 'Key pair is missing.' }

    $vpcResult = Invoke-M7AwsJson -Arguments @('ec2', 'describe-vpcs', '--vpc-ids', $VpcId)
    if (@($vpcResult.Vpcs).Count -ne 1 -or -not $vpcResult.Vpcs[0].IsDefault) {
        throw 'VpcId must identify the existing default VPC.'
    }

    $subnetResult = Invoke-M7AwsJson -Arguments @('ec2', 'describe-subnets', '--subnet-ids', $SubnetId)
    if (@($subnetResult.Subnets).Count -ne 1) { throw 'SubnetId was not found.' }
    $subnet = $subnetResult.Subnets[0]
    if ($subnet.VpcId -ne $VpcId -or $subnet.State -ne 'available' -or -not $subnet.MapPublicIpOnLaunch) {
        throw 'SubnetId must be public, available and belong to VpcId.'
    }

    $routeTables = Invoke-M7AwsJson -Arguments @('ec2', 'describe-route-tables', '--filters', "Name=vpc-id,Values=$VpcId")
    $selectedTables = @($routeTables.RouteTables | Where-Object {
        @($_.Associations | Where-Object { $_.SubnetId -eq $SubnetId }).Count -gt 0
    })
    if (-not $selectedTables.Count) {
        $selectedTables = @($routeTables.RouteTables | Where-Object {
            @($_.Associations | Where-Object { $_.Main -eq $true }).Count -gt 0
        })
    }
    $hasInternetGateway = @($selectedTables | Where-Object {
        @($_.Routes | Where-Object {
            $_.GatewayId -like 'igw-*' -and $_.State -eq 'active' -and $_.DestinationCidrBlock -eq '0.0.0.0/0'
        }).Count -gt 0
    }).Count -gt 0
    if (-not $hasInternetGateway) { throw 'SubnetId has no active default route to an Internet Gateway.' }

    $imageResult = Invoke-M7AwsJson -Arguments @('ec2', 'describe-images', '--image-ids', $AmiId)
    $image = @($imageResult.Images | Where-Object {
        $_.State -eq 'available' -and $_.Architecture -eq 'x86_64' -and
        $_.OwnerId -eq '099720109477' -and $_.Name -match 'ubuntu-noble-24\.04-amd64-server'
    })
    if ($image.Count -ne 1) { throw 'AmiId must be an available Canonical Ubuntu 24.04 amd64 AMI.' }

    $offering = Invoke-M7AwsJson -Arguments @(
        'ec2', 'describe-instance-type-offerings', '--location-type', 'availability-zone',
        '--filters', "Name=location,Values=$($subnet.AvailabilityZone)",
        "Name=instance-type,Values=$InstanceType"
    )
    if (@($offering.InstanceTypeOfferings).Count -lt 1) {
        throw "$InstanceType is not offered in the selected Availability Zone."
    }

    $profileResult = Invoke-M7AwsJson -Arguments @('iam', 'get-instance-profile', '--instance-profile-name', $InstanceProfileName)
    $role = @($profileResult.InstanceProfile.Roles)[0]
    if (-not $role) { throw 'InstanceProfileName has no associated role.' }
    $requiredActions = @(
        'ecr:GetAuthorizationToken',
        'ecr:BatchCheckLayerAvailability',
        'ecr:BatchGetImage',
        'ecr:GetDownloadUrlForLayer',
        'logs:CreateLogStream',
        'logs:PutLogEvents'
    )
    $simulation = Invoke-M7AwsJson -Arguments (@(
        'iam', 'simulate-principal-policy', '--policy-source-arn', $role.Arn, '--action-names'
    ) + $requiredActions)
    $notAllowed = @($simulation.EvaluationResults | Where-Object { $_.EvalDecision -ne 'allowed' })
    if ($notAllowed.Count) { throw 'The instance profile does not simulate all required ECR pull and Logs permissions.' }

    $repositories = Invoke-M7AwsJson -Arguments @(
        'ecr', 'describe-repositories', '--repository-names', 'm7-g05-backend', 'm7-g05-frontend'
    )
    if (@($repositories.Repositories).Count -ne 2) { throw 'Both MVP ECR repositories must exist.' }
    if (@($repositories.Repositories | Where-Object { $_.ImageTagMutability -ne 'IMMUTABLE' }).Count) {
        throw 'Both ECR repositories must enforce immutable tags.'
    }
    foreach ($pair in @(
        @{ Name = 'm7-g05-backend'; Tag = $BackendImageTag; Digest = $BackendImageDigest },
        @{ Name = 'm7-g05-frontend'; Tag = $FrontendImageTag; Digest = $FrontendImageDigest }
    )) {
        $imageDetails = Invoke-M7AwsJson -Arguments @(
            'ecr', 'describe-images', '--repository-name', $pair.Name,
            '--image-ids', "imageTag=$($pair.Tag)"
        )
        if (@($imageDetails.ImageDetails).Count -ne 1 -or $imageDetails.ImageDetails[0].ImageDigest -ne $pair.Digest) {
            throw "Immutable tag/digest mismatch in ECR repository $($pair.Name)."
        }
    }
}

try {
    Assert-Inputs
    if ($ConfirmExecution -and $Action -ne 'ExecuteChangeSet') { throw 'ConfirmExecution applies only to ExecuteChangeSet.' }
    if ($Action -eq 'ExecuteChangeSet' -and -not $ConfirmExecution) { throw 'Execution requires -ConfirmExecution.' }

    Import-M7AwsEnvironment
    $identity = Assert-M7AwsSession
    Write-Output 'AWS STS: valid; region: us-east-1.'

    if ($Action -in @('InspectChangeSet','ExecuteChangeSet')) {
        $stack = Invoke-M7AwsJson -Arguments @('cloudformation','describe-stacks','--stack-name',$StackName)
        if (@($stack.Stacks).Count -ne 1 -or $stack.Stacks[0].StackStatus -ne 'CREATE_COMPLETE') { throw 'Existing stack changed state; stop and repeat preflight.' }
        $change = Assert-ChangeSet -ExpectedStackId ([string]$stack.Stacks[0].StackId)
        Write-Output "Ready UPDATE change set $ChangeSetName replaces ApplicationInstance due to KeyName. Expect downtime and old root EBS deletion."
        foreach ($item in $change.Changes) {
            Write-Output ($item.ResourceChange | ConvertTo-Json -Depth 12)
        }
        if ($Action -eq 'ExecuteChangeSet' -and $PSCmdlet.ShouldProcess("$StackName / $ChangeSetName",'Execute UPDATE change set and replace EC2')) {
            $null = Invoke-M7AwsJson -Arguments @('cloudformation','execute-change-set','--stack-name',$StackName,'--change-set-name',$ChangeSetName)
            Write-Output 'Change set execution submitted.'
        }
        return
    }

    $dockerCli = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $dockerCli) { throw 'Docker CLI is not installed or not discoverable.' }
    $null = Invoke-LocalGate -Program $dockerCli.Source -Arguments @(
        'compose', '-f', 'compose.prod.yml', 'config', '--quiet'
    ) -Failure 'Docker Compose config validation failed.'
    Write-Output 'Docker Compose config: valid.'

    $renderedTemplate = Get-M7RenderedTemplate -RepoRoot $script:AwsRepoRoot
    try {
        $cfnLint = Get-Command cfn-lint -ErrorAction SilentlyContinue
        if ($cfnLint) {
            $null = Invoke-LocalGate -Program $cfnLint.Source -Arguments @($renderedTemplate) -Failure 'cfn-lint failed.'
            Write-Output 'cfn-lint: valid.'
        } else {
            Write-Output 'cfn-lint: unavailable; YAML and User Data require the local gates documented in the runbook.'
        }

        $templateUri = 'file://' + $renderedTemplate.Replace('\', '/')
        $null = Invoke-M7AwsJson -Arguments @('cloudformation', 'validate-template', '--template-body', $templateUri)
        Write-Output 'CloudFormation validate-template: valid.'

        Assert-AwsInputs -AccountId ([string]$identity.Account)
        Write-Output 'VPC, subnet route, AMI, key pair, IAM profile, immutable ECR tags/digests and existing stack: valid.'
        Write-Output "Chosen images: backend $BackendImageTag $BackendImageDigest; frontend $FrontendImageTag $FrontendImageDigest."
        $git = Get-Command git -ErrorAction SilentlyContinue
        if (-not $git) { throw 'Git is required to compare image tag and current HEAD trees.' }
        if ($BackendImageTag -ne $FrontendImageTag) { throw 'This re-use plan requires the same reviewed image tag for both repositories.' }
        $imageTree = (& $git.Source -C $script:AwsRepoRoot rev-parse "$BackendImageTag^{tree}" 2>$null | Out-String).Trim()
        $headTree = (& $git.Source -C $script:AwsRepoRoot rev-parse 'HEAD^{tree}' 2>$null | Out-String).Trim()
        if ($imageTree -notmatch '^[a-f0-9]{40}$' -or $headTree -notmatch '^[a-f0-9]{40}$' -or $imageTree -ne $headTree) { throw 'Local image-tag commit and HEAD trees differ or cannot be checked.' }
        Write-Output "Git trees match: $imageTree. Equal trees alone do not prove image build provenance."

        if ($Action -eq 'CreateChangeSet') {
            $parameters = @(
                "ParameterKey=VpcId,ParameterValue=$VpcId",
                "ParameterKey=SubnetId,ParameterValue=$SubnetId",
                "ParameterKey=AmiId,ParameterValue=$AmiId",
                "ParameterKey=InstanceType,ParameterValue=$InstanceType",
                "ParameterKey=RootVolumeSize,ParameterValue=$RootVolumeSize",
                "ParameterKey=InstanceProfileName,ParameterValue=$InstanceProfileName",
                "ParameterKey=EcrRegistryUri,ParameterValue=$EcrRegistryUri",
                "ParameterKey=BackendImageTag,ParameterValue=$BackendImageTag",
                "ParameterKey=FrontendImageTag,ParameterValue=$FrontendImageTag",
                "ParameterKey=KeyPairName,ParameterValue=$KeyPairName",
                "ParameterKey=OperatorSshCidr,ParameterValue=$OperatorSshCidr"
            )
            $generatedName = 'm7-g05-ssh-' + [guid]::NewGuid().ToString('N')
            if ($PSCmdlet.ShouldProcess("CloudFormation stack $StackName in us-east-1", 'Create UPDATE change set only')) {
                $arguments = @(
                    'cloudformation', 'create-change-set', '--stack-name', $StackName,
                    '--change-set-name', $generatedName, '--change-set-type', 'UPDATE',
                    '--template-body', $templateUri, '--parameters'
                ) + $parameters
                $null = Invoke-M7AwsJson -Arguments $arguments
                Write-Output "Change set created: $generatedName. Inspect it in a later invocation with -Action InspectChangeSet -ChangeSetName $generatedName. It was not executed."
            }
        } else {
            Write-Output 'Read-only preflight complete; no change set was created.'
        }
    } finally {
        if (Test-Path -LiteralPath $renderedTemplate) {
            Remove-Item -LiteralPath $renderedTemplate -Force
        }
    }
} catch {
    if ($_.Exception.Message -eq 'CREDENTIALS_EXPIRED') {
        Write-Error 'STATUS: CREDENCIAIS_EXPIRADAS. No further AWS operations were attempted.'
        exit 3
    }
    if ($_.Exception.Message -eq 'AWS_ACCESS_DENIED') {
        Write-Error 'AWS_ACCESS_DENIED: the requested AWS action is unavailable.'
        exit 4
    }
    Write-Error $_.Exception.Message
    exit 1
}
