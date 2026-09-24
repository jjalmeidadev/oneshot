$ErrorActionPreference = 'Stop'

$script:AwsRepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$script:AwsCliPath = $null

function Import-M7AwsEnvironment {
    $envFile = if ($env:M7_AWS_ENV_FILE) {
        $env:M7_AWS_ENV_FILE
    } else {
        Join-Path $script:AwsRepoRoot 'src/backend/.env'
    }
    if (-not (Test-Path -LiteralPath $envFile -PathType Leaf)) {
        throw 'AWS environment file is missing. Set M7_AWS_ENV_FILE to a protected .env path.'
    }

    $wanted = @('AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN', 'AWS_DEFAULT_REGION')
    $values = @{}
    foreach ($line in [IO.File]::ReadAllLines($envFile)) {
        if ($line -match '^\s*(AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|AWS_DEFAULT_REGION)\s*=\s*(.*?)\s*$') {
            $value = $Matches[2]
            if ($value.Length -ge 2 -and
                (($value.StartsWith('"') -and $value.EndsWith('"')) -or
                 ($value.StartsWith("'") -and $value.EndsWith("'")))) {
                $value = $value.Substring(1, $value.Length - 2)
            }
            $values[$Matches[1]] = $value
        }
    }
    foreach ($name in $wanted) {
        if (-not $values.ContainsKey($name) -or [string]::IsNullOrWhiteSpace($values[$name])) {
            throw "AWS environment file is missing $name. Values are never displayed by this script."
        }
        [Environment]::SetEnvironmentVariable($name, $values[$name], 'Process')
    }
    if ($values['AWS_DEFAULT_REGION'] -ne 'us-east-1') {
        throw 'AWS_DEFAULT_REGION must be us-east-1 for this prepared stack.'
    }

    Remove-Item Env:AWS_PROFILE -ErrorAction SilentlyContinue
    $env:AWS_REGION = 'us-east-1'
    $env:AWS_PAGER = ''
    $env:AWS_EC2_METADATA_DISABLED = 'true'

    $awsCommand = Get-Command aws -ErrorAction SilentlyContinue
    if ($awsCommand) {
        $script:AwsCliPath = $awsCommand.Source
    } elseif (Test-Path -LiteralPath 'C:\Program Files\Amazon\AWSCLIV2\aws.exe') {
        $script:AwsCliPath = 'C:\Program Files\Amazon\AWSCLIV2\aws.exe'
    } else {
        throw 'AWS CLI is not installed or not discoverable.'
    }
}

function Invoke-M7AwsJson {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    $allArguments = @($Arguments) + @('--region', 'us-east-1', '--output', 'json', '--no-cli-pager')
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $raw = (& $script:AwsCliPath @allArguments 2>&1 | Out-String)
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousPreference
    if ($exitCode -ne 0) {
        if ($raw -match 'ExpiredToken|RequestExpired|InvalidClientTokenId|UnrecognizedClientException|The security token included in the request is expired') {
            throw 'CREDENTIALS_EXPIRED'
        }
        if ($raw -match 'AccessDenied|UnauthorizedOperation') {
            throw 'AWS_ACCESS_DENIED'
        }
        throw 'AWS_CLI_ERROR'
    }
    try {
        return $raw | ConvertFrom-Json -ErrorAction Stop
    } catch {
        throw 'AWS_CLI_RESPONSE_INVALID'
    }
}

function Assert-M7AwsSession {
    # This must be the first AWS API request made by a phase script.
    $identity = Invoke-M7AwsJson -Arguments @('sts', 'get-caller-identity')
    return $identity
}

function Get-M7RenderedTemplate {
    param([Parameter(Mandatory = $true)][string]$RepoRoot)

    $templatePath = Join-Path $RepoRoot 'infra/aws/template.yaml'
    $userDataPath = Join-Path $RepoRoot 'infra/aws/user-data.sh'
    $composePath = Join-Path $RepoRoot 'compose.prod.yml'
    $agentPath = Join-Path $RepoRoot 'infra/aws/cloudwatch-agent.json'
    $template = [IO.File]::ReadAllText($templatePath)
    $userData = [IO.File]::ReadAllText($userDataPath)

    $composeBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes([IO.File]::ReadAllText($composePath)))
    $agentBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes([IO.File]::ReadAllText($agentPath)))
    $userData = $userData.Replace('__COMPOSE_PROD_BASE64__', $composeBase64)
    $userData = $userData.Replace('__CLOUDWATCH_AGENT_BASE64__', $agentBase64)

    $indentUserData = (($userData -split '\r?\n') | ForEach-Object { "            $_" }) -join "`n"
    $stubPattern = '(?m)^            echo "This template source must be rendered with scripts/aws/deploy\.ps1\." >&2\r?\n            exit 64[ \t]*$'
    $stubMatch = [regex]::Match($template, $stubPattern)
    if (-not $stubMatch.Success) {
        throw 'CloudFormation UserData render marker is missing or has changed.'
    }
    $rendered = $template.Substring(0, $stubMatch.Index) + $indentUserData + $template.Substring($stubMatch.Index + $stubMatch.Length)

    $tempPath = Join-Path ([IO.Path]::GetTempPath()) ("m7-g05-template-{0}.yaml" -f [guid]::NewGuid().ToString('N'))
    [IO.File]::WriteAllText($tempPath, $rendered, [Text.UTF8Encoding]::new($false))
    return $tempPath
}
