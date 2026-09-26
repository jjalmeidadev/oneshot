$ErrorActionPreference = 'Stop'

$source = Join-Path $PSScriptRoot 'deploy.ps1'
$tokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($source, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count) { throw 'deploy.ps1 has PowerShell syntax errors.' }
$definition = $ast.Find({
    param($node)
    $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Assert-ChangeSet'
}, $true)
if (-not $definition) { throw 'Assert-ChangeSet was not found.' }
Invoke-Expression $definition.Extent.Text

$StackName = 'm7-g05-mvp'
$ChangeSetName = 'm7-g05-ssh-9435a35c3cb34a9e8c3459965ade114c'
$expectedStackId = 'arn:aws:cloudformation:us-east-1:123456789012:stack/m7-g05-mvp/example'
$script:mockIp = '198.51.100.10'

function Invoke-M7AwsJson {
    param([string[]]$Arguments)
    return $script:mockChange
}

function Invoke-RestMethod {
    param([string]$Uri, [int]$TimeoutSec)
    return $script:mockIp
}

function New-MockChangeSet {
    return [pscustomobject]@{
        ChangeSetName = $ChangeSetName
        StackName = $StackName
        StackId = $expectedStackId
        Status = 'CREATE_COMPLETE'
        ExecutionStatus = 'AVAILABLE'
        Parameters = @([pscustomobject]@{ ParameterKey = 'OperatorSshCidr'; ParameterValue = '198.51.100.10/32' })
        Changes = @(
            [pscustomobject]@{ ResourceChange = [pscustomobject]@{
                LogicalResourceId = 'ApplicationInstance'
                Action = 'Modify'
                Replacement = 'True'
                Details = @([pscustomobject]@{ Target = [pscustomobject]@{ Name = 'KeyName' } })
            } }
            [pscustomobject]@{ ResourceChange = [pscustomobject]@{
                LogicalResourceId = 'ApplicationSecurityGroup'
                Action = 'Modify'
                Replacement = 'False'
                Details = @(
                    [pscustomobject]@{ Target = [pscustomobject]@{ Name = 'SecurityGroupIngress' } }
                    [pscustomobject]@{ Target = [pscustomobject]@{ Name = 'SecurityGroupEgress' } }
                )
            } }
        )
    }
}

function Assert-Rejected {
    param([string]$CaseName, [string]$ExpectedMessage)
    try {
        $null = Assert-ChangeSet -ExpectedStackId $expectedStackId
    } catch {
        if ($_.Exception.Message -notlike "*$ExpectedMessage*") { throw "$CaseName failed with an unexpected error: $($_.Exception.Message)" }
        Write-Output "PASS: $CaseName"
        return
    }
    throw "$CaseName was unexpectedly accepted."
}

$script:mockChange = New-MockChangeSet
if ($script:mockChange.PSObject.Properties.Name -contains 'ChangeSetType') { throw 'Fixture must omit ChangeSetType.' }
$accepted = Assert-ChangeSet -ExpectedStackId $expectedStackId
if ($accepted.Changes[0].ResourceChange.Replacement -ne 'True') { throw 'EC2 replacement was not accepted.' }
Write-Output 'PASS: no ChangeSetType, EC2 replacement by KeyName and in-place SG update'

$script:mockChange = New-MockChangeSet
$script:mockChange.Changes[0].ResourceChange.Replacement = 'False'
Assert-Rejected -CaseName 'EC2 without replacement' -ExpectedMessage 'Expected EC2 replacement'

$script:mockChange = New-MockChangeSet
$script:mockChange.Changes[0].ResourceChange.Details = @()
Assert-Rejected -CaseName 'EC2 replacement without KeyName cause' -ExpectedMessage 'KeyName is not listed'

$script:mockChange = New-MockChangeSet
$script:mockChange.Changes[1].ResourceChange.Replacement = 'True'
Assert-Rejected -CaseName 'Security Group replacement' -ExpectedMessage 'may replace'

$script:mockChange = New-MockChangeSet
$script:mockIp = '198.51.100.11'
Assert-Rejected -CaseName 'stale operator CIDR' -ExpectedMessage 'STALE_OPERATOR_SSH_CIDR'
$script:mockIp = '198.51.100.10'

$script:mockChange = New-MockChangeSet
$script:mockChange.Changes += [pscustomobject]@{ ResourceChange = [pscustomobject]@{ LogicalResourceId = 'UnexpectedResource'; Action = 'Add'; Replacement = 'False' } }
Assert-Rejected -CaseName 'unexpected resource' -ExpectedMessage 'unexpected resources'

$script:mockChange = New-MockChangeSet
$script:mockChange.StackId = 'other-stack'
Assert-Rejected -CaseName 'wrong stack identity' -ExpectedMessage 'expected stack'
