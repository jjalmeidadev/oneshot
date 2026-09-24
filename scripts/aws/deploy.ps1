[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [string]$StackName = 'm7-g05-mvp',
    [Parameter(Mandatory = $true)]
    [string]$VpcId,
    [Parameter(Mandatory = $true)]
    [string]$SubnetId,
    [Parameter(Mandatory = $true)]
    [string]$AmiId,
    [ValidateSet('t3.large', 't3.xlarge')]
    [string]$InstanceType = 't3.large',
    [ValidateRange(50, 100)]
    [int]$RootVolumeSize = 50,
    [Parameter(Mandatory = $true)]
    [string]$InstanceProfileName,
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9]{12}\.dkr\.ecr\.us-east-1\.amazonaws\.com$')]
    [string]$EcrRegistryUri,
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-fA-F0-9]{40}$')]
    [string]$BackendImageTag,
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-fA-F0-9]{40}$')]
    [string]$FrontendImageTag,
    [switch]$Provision,
    [switch]$ConfirmProvisioning
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'common.ps1')

function Invoke-LocalGate {
    param([string]$Program, [string[]]$Arguments, [string]$Failure)
    $output = & $Program @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) { throw $Failure }
    return $output
}

function Assert-CommitTags {
    $gitCli = Get-Command git -ErrorAction SilentlyContinue
    if (-not $gitCli) { throw 'Git is required to validate immutable tags.' }
    $headSha = (& $gitCli.Source -c "safe.directory=$script:AwsRepoRoot" -C $script:AwsRepoRoot rev-parse HEAD 2>$null | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $BackendImageTag -ne $headSha -or $FrontendImageTag -ne $headSha) {
        throw 'BackendImageTag and FrontendImageTag must equal the full reviewed HEAD commit SHA.'
    }
}

function Assert-AwsInputs {
    param([string]$AccountId)

    if ($EcrRegistryUri.Split('.')[0] -ne $AccountId) {
        throw 'EcrRegistryUri account does not match the validated STS identity.'
    }

    $vpcResult = Invoke-M7AwsJson -Arguments @('ec2', 'describe-vpcs', '--vpc-ids', $VpcId)
    if (@($vpcResult.Vpcs).Count -ne 1 -or -not $vpcResult.Vpcs[0].IsDefault) {
        throw 'VpcId must identify the existing default VPC.'
    }

    $subnetResult = Invoke-M7AwsJson -Arguments @('ec2', 'describe-subnets', '--subnet-ids', $SubnetId)
    if (@($subnetResult.Subnets).Count -ne 1) { throw 'SubnetId was not found.' }
    $subnet = $subnetResult.Subnets[0]
    if ($subnet.VpcId -ne $VpcId -or $subnet.State -ne 'available') {
        throw 'SubnetId must be available and belong to VpcId.'
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
        'ssm:UpdateInstanceInformation',
        'ssmmessages:CreateControlChannel',
        'ssmmessages:CreateDataChannel',
        'ssmmessages:OpenControlChannel',
        'ssmmessages:OpenDataChannel',
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
    if ($notAllowed.Count) { throw 'The instance profile does not simulate all required SSM, ECR pull and Logs permissions.' }

    $repositories = Invoke-M7AwsJson -Arguments @(
        'ecr', 'describe-repositories', '--repository-names', 'm7-g05-backend', 'm7-g05-frontend'
    )
    if (@($repositories.Repositories).Count -ne 2) { throw 'Both MVP ECR repositories must exist.' }
    if (@($repositories.Repositories | Where-Object { $_.ImageTagMutability -ne 'IMMUTABLE' }).Count) {
        throw 'Both ECR repositories must enforce immutable tags.'
    }
    foreach ($pair in @(
        @{ Name = 'm7-g05-backend'; Tag = $BackendImageTag },
        @{ Name = 'm7-g05-frontend'; Tag = $FrontendImageTag }
    )) {
        $imageDetails = Invoke-M7AwsJson -Arguments @(
            'ecr', 'describe-images', '--repository-name', $pair.Name,
            '--image-ids', "imageTag=$($pair.Tag)"
        )
        if (@($imageDetails.ImageDetails).Count -ne 1) {
            throw "The immutable tag is missing from ECR repository $($pair.Name)."
        }
    }

    $stacks = Invoke-M7AwsJson -Arguments @('cloudformation', 'list-stacks')
    $active = @($stacks.StackSummaries | Where-Object {
        $_.StackName -eq $StackName -and $_.StackStatus -notmatch '^DELETE_'
    })
    if ($active.Count) { throw 'StackName already exists; this MVP script only prepares a first create.' }
}

try {
    if ($ConfirmProvisioning -and -not $Provision) {
        throw 'ConfirmProvisioning is valid only with Provision.'
    }
    if ($Provision -and -not $ConfirmProvisioning) {
        throw 'Provisioning requires both -Provision and -ConfirmProvisioning.'
    }

    Import-M7AwsEnvironment
    $identity = Assert-M7AwsSession
    Write-Output 'AWS STS: valid; region: us-east-1.'

    $dockerCli = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $dockerCli) { throw 'Docker CLI is not installed or not discoverable.' }
    $null = Invoke-LocalGate -Program $dockerCli.Source -Arguments @(
        'compose', '-f', 'compose.prod.yml', 'config', '--quiet'
    ) -Failure 'Docker Compose config validation failed.'
    Write-Output 'Docker Compose config: valid.'

    Assert-CommitTags
    $renderedTemplate = Get-M7RenderedTemplate -RepoRoot $script:AwsRepoRoot
    try {
        $cfnLint = Get-Command cfn-lint -ErrorAction SilentlyContinue
        if ($cfnLint) {
            $null = Invoke-LocalGate -Program $cfnLint.Source -Arguments @($renderedTemplate) -Failure 'cfn-lint failed.'
            Write-Output 'cfn-lint: valid.'
        } else {
            Write-Output 'cfn-lint: unavailable; YAML and User Data require the local gates documented in the runbook.'
        }

        $awsTemplateValidationAvailable = $true
        try {
            $templateUri = 'file://' + $renderedTemplate.Replace('\', '/')
            $null = Invoke-M7AwsJson -Arguments @('cloudformation', 'validate-template', '--template-body', $templateUri)
            Write-Output 'CloudFormation validate-template: valid.'
        } catch {
            if ($_.Exception.Message -ne 'AWS_ACCESS_DENIED') { throw }
            $awsTemplateValidationAvailable = $false
            Write-Warning 'AWS_TEMPLATE_VALIDATION_UNAVAILABLE: cloudformation:ValidateTemplate was denied.'
        }

        Assert-AwsInputs -AccountId ([string]$identity.Account)
        Write-Output 'VPC, public subnet route, AMI, instance type, IAM profile, ECR tags and stack state: valid.'

        if ($Provision) {
            if (-not $awsTemplateValidationAvailable) {
                throw 'Provisioning is blocked until cloudformation:ValidateTemplate succeeds.'
            }
            $parameters = @(
                "ParameterKey=VpcId,ParameterValue=$VpcId",
                "ParameterKey=SubnetId,ParameterValue=$SubnetId",
                "ParameterKey=AmiId,ParameterValue=$AmiId",
                "ParameterKey=InstanceType,ParameterValue=$InstanceType",
                "ParameterKey=RootVolumeSize,ParameterValue=$RootVolumeSize",
                "ParameterKey=InstanceProfileName,ParameterValue=$InstanceProfileName",
                "ParameterKey=EcrRegistryUri,ParameterValue=$EcrRegistryUri",
                "ParameterKey=BackendImageTag,ParameterValue=$BackendImageTag",
                "ParameterKey=FrontendImageTag,ParameterValue=$FrontendImageTag"
            )
            if ($PSCmdlet.ShouldProcess("CloudFormation stack $StackName in us-east-1", 'CreateStack')) {
                $arguments = @(
                    'cloudformation', 'create-stack', '--stack-name', $StackName,
                    '--template-body', $templateUri, '--on-failure', 'DO_NOTHING', '--parameters'
                ) + $parameters + @(
                    '--tags', 'Key=Application,Value=m7-g05',
                    'Key=Lifetime,Value=temporary-four-days'
                )
                $null = Invoke-M7AwsJson -Arguments $arguments
                Write-Output 'CloudFormation CreateStack was submitted.'
            }
        } else {
            Write-Output 'Read-only preflight complete; no resource operation was requested.'
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
        Write-Error 'AWS_ACCESS_DENIED: a read-only preflight action is unavailable.'
        exit 4
    }
    Write-Error $_.Exception.Message
    exit 1
}
