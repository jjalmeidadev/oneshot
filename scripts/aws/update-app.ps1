[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [ValidateSet('Preflight', 'Execute')][string]$Action = 'Preflight',
    [Parameter(Mandatory = $true)][ValidatePattern('^i-[a-fA-F0-9]{8,17}$')][string]$InstanceId,
    [Parameter(Mandatory = $true)][string]$PrivateKeyPath,
    [string]$RuntimeEnvPath,
    [string]$RuntimeOverlayPath,
    [Parameter(Mandatory = $true)][ValidatePattern('^[0-9]{12}\.dkr\.ecr\.us-east-1\.amazonaws\.com$')][string]$EcrRegistryUri,
    [Parameter(Mandatory = $true)][ValidatePattern('^[a-fA-F0-9]{40}$')][string]$BackendImageTag,
    [Parameter(Mandatory = $true)][ValidatePattern('^[a-fA-F0-9]{40}$')][string]$FrontendImageTag,
    [Parameter(Mandatory = $true)][ValidatePattern('^sha256:[a-fA-F0-9]{64}$')][string]$BackendImageDigest,
    [Parameter(Mandatory = $true)][ValidatePattern('^sha256:[a-fA-F0-9]{64}$')][string]$FrontendImageDigest,
    [string]$KeyPairName = 'm7-g05-learner-lab-2026',
    [switch]$ConfirmUpdate
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'common.ps1')

function Assert-CommandSucceeded {
    param([string]$Program, [string[]]$Arguments, [string]$Failure)
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $output = (& $Program @Arguments 2>&1 | Out-String)
    $code = $LASTEXITCODE
    $ErrorActionPreference = $previousPreference
    if ($code -ne 0) { throw $Failure }
    return $output
}

function Assert-LocalRuntime {
    param([string]$Path, [switch]$Overlay)
    $resolved = (Resolve-Path -LiteralPath $Path -ErrorAction Stop).Path
    if ($resolved.StartsWith($script:AwsRepoRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Runtime env must be outside the repository.'
    }
    $values = @{}
    foreach ($line in [IO.File]::ReadAllLines($resolved)) {
        if ($line -match '^\s*(?:export\s+)?AWS_[A-Za-z0-9_]*\s*=') { throw 'Runtime env must not contain AWS_* assignments.' }
        if ($line -match '^\s*#|^\s*$') { continue }
        if ($line -notmatch '^([A-Za-z_][A-Za-z0-9_]*)=(.*)$') { throw 'Runtime env contains an unsupported line.' }
        if ($values.ContainsKey($Matches[1])) { throw 'Runtime env contains a duplicate name.' }
        $value = $Matches[2].Trim()
        if ($value.Length -ge 2 -and (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'")))) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        $values[$Matches[1]] = $value
    }
    $required = if ($Overlay) {
        @('SUPABASE_URL','NOTIFICATION_CALLBACK_SECRET','SHAREPOINT_WEBHOOK_CLIENT_STATE','GEMINI_API_KEY')
    } else {
        @('GEMINI_API_KEY','AZURE_SPEECH_KEY','AZURE_SPEECH_TIMEOUT_SECONDS','AZURE_SPEECH_MAX_ATTEMPTS','AUDIO_SIMULATED_IDENTITIES','REPORT_SIMULATED_IDENTITIES','ALERT_CONFIRMATION_SECRET','RABBITMQ_USER','RABBITMQ_PASSWORD','RABBITMQ_URL','DATABASE_POOL_MAX_SIZE','DATABASE_STATEMENT_TIMEOUT_MS','SUPABASE_URL','NOTIFICATION_CALLBACK_SECRET','SHAREPOINT_WEBHOOK_CLIENT_STATE')
    }
    if ($Overlay) {
        $allowed = @('SUPABASE_URL','SUPABASE_PUBLISHABLE_KEY','SUPABASE_ANON_KEY','NOTIFICATION_CALLBACK_SECRET','SHAREPOINT_WEBHOOK_CLIENT_STATE','REPORT_CALLBACK_TOKEN','GEMINI_API_KEY')
        foreach ($name in $values.Keys) { if ($name -notin $allowed) { throw "Runtime overlay contains unsupported name: $name" } }
    }
    foreach ($name in $required) {
        if (-not $values.ContainsKey($name) -or [string]::IsNullOrWhiteSpace($values[$name])) { throw "Runtime env is missing $name." }
    }
    if (-not $Overlay -and -not $values['DATABASE_URL'] -and -not $values['SUPABASE_DATABASE_URL']) { throw 'Runtime env needs DATABASE_URL or SUPABASE_DATABASE_URL.' }
    if (-not $values['SUPABASE_PUBLISHABLE_KEY'] -and -not $values['SUPABASE_ANON_KEY']) { throw 'Runtime env needs a public Supabase API key.' }
    if (-not $Overlay -and -not $values['AZURE_SPEECH_RESOURCE'] -and -not $values['AZURE_SPEECH_ENDPOINT']) { throw 'Runtime env needs AZURE_SPEECH_RESOURCE or AZURE_SPEECH_ENDPOINT.' }
    return $resolved
}

function Assert-Compose {
    param([string]$RuntimePath, [switch]$Overlay)
    $docker = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $docker) { throw 'Docker CLI is required for local Compose validation.' }
    $saved = @{}
    $names = @('BACKEND_IMAGE','BACKEND_IMAGE_TAG','FRONTEND_IMAGE','FRONTEND_IMAGE_TAG','DATABASE_URL','RABBITMQ_USER','RABBITMQ_PASSWORD','RABBITMQ_URL','ALERT_CONFIRMATION_SECRET','DATABASE_POOL_MAX_SIZE','DATABASE_STATEMENT_TIMEOUT_MS')
    foreach ($name in $names) { $saved[$name] = [Environment]::GetEnvironmentVariable($name, 'Process') }
    try {
        if ($Overlay) {
            $env:DATABASE_URL = 'postgresql://probe:probe@localhost:5432/probe'
            $env:RABBITMQ_USER = 'probe'
            $env:RABBITMQ_PASSWORD = 'probe'
            $env:RABBITMQ_URL = 'amqp://probe:probe@rabbitmq:5672/'
            $env:ALERT_CONFIRMATION_SECRET = 'local-compose-validation-only'
            $env:DATABASE_POOL_MAX_SIZE = '5'
            $env:DATABASE_STATEMENT_TIMEOUT_MS = '5000'
        }
        $env:BACKEND_IMAGE = "$EcrRegistryUri/m7-g05-backend"
        $env:BACKEND_IMAGE_TAG = $BackendImageTag
        $env:FRONTEND_IMAGE = "$EcrRegistryUri/m7-g05-frontend"
        $env:FRONTEND_IMAGE_TAG = $FrontendImageTag
        $raw = Assert-CommandSucceeded -Program $docker.Source -Arguments @('compose','--env-file',$RuntimePath,'-f',(Join-Path $script:AwsRepoRoot 'compose.prod.yml'),'config','--format','json') -Failure 'Local Compose rendering failed.'
        try { $config = $raw | ConvertFrom-Json -ErrorAction Stop } catch { throw 'Local Compose JSON is invalid.' }
    } finally {
        foreach ($name in $saved.Keys) { [Environment]::SetEnvironmentVariable($name, $saved[$name], 'Process') }
    }
    $services = $config.services
    foreach ($name in @('backend','frontend','rabbitmq','scheduler','publisher','evaluator','notifier','delivery','sharepoint-publisher','sharepoint-consumer')) {
        if (-not $services.PSObject.Properties[$name]) { throw "Compose service $name is missing." }
    }
    if ($services.PSObject.Properties['notebook']) { throw 'Notebook must not be in the default Compose profile.' }
    $rabbitNetworks = @($services.rabbitmq.networks.PSObject.Properties.Name)
    if ($services.rabbitmq.image -ne 'rabbitmq:4.1.8-alpine' -or $services.rabbitmq.PSObject.Properties['ports'] -or
        $rabbitNetworks.Count -ne 1 -or $rabbitNetworks[0] -ne 'app-private' -or -not $services.rabbitmq.volumes -or -not $services.rabbitmq.healthcheck) { throw 'RabbitMQ must be pinned, persistent, healthy and private.' }
    if (@($services.frontend.ports).Count -ne 1 -or $services.frontend.ports[0].host_ip -ne '127.0.0.1' -or
        [string]$services.frontend.ports[0].published -ne '80') { throw 'Frontend must bind only to 127.0.0.1:80.' }
    if (-not $services.backend.environment.DATABASE_URL -and -not $services.backend.environment.SUPABASE_DATABASE_URL) { throw 'Compose did not inject the database URL.' }
    if (-not $services.backend.environment.SUPABASE_URL -or
        (-not $services.backend.environment.SUPABASE_PUBLISHABLE_KEY -and -not $services.backend.environment.SUPABASE_ANON_KEY) -or
        -not $services.backend.environment.NOTIFICATION_CALLBACK_SECRET -or
        -not $services.backend.environment.SHAREPOINT_WEBHOOK_CLIENT_STATE) { throw 'Compose did not inject Sprint 5 authentication and webhook settings.' }
    $broker = $services.rabbitmq.environment
    try { $url = [uri]$services.backend.environment.RABBITMQ_URL } catch { throw 'RabbitMQ URL is invalid.' }
    $userInfo = $url.UserInfo.Split(':', 2)
    if ($url.Scheme -ne 'amqp' -or $url.Host -ne 'rabbitmq' -or $url.Port -ne 5672 -or $userInfo.Count -ne 2 -or
        $broker.RABBITMQ_DEFAULT_USER -eq 'guest' -or
        [uri]::UnescapeDataString($userInfo[0]) -cne $broker.RABBITMQ_DEFAULT_USER -or
        [uri]::UnescapeDataString($userInfo[1]) -cne $broker.RABBITMQ_DEFAULT_PASS) { throw 'RabbitMQ URL and broker credentials do not match.' }
    foreach ($name in @('backend','scheduler','publisher','evaluator','notifier','delivery','sharepoint-publisher','sharepoint-consumer')) {
        $service = $services.PSObject.Properties[$name].Value
        if ($service.environment.ALERT_REPOSITORY_MODE -ne 'database' -or $service.environment.ALERT_SCHEDULE_SOURCE -ne 'database' -or
            -not $service.environment.ALERT_CONFIRMATION_SECRET -or -not $service.environment.RABBITMQ_URL -or
            -not $service.environment.DATABASE_POOL_MAX_SIZE -or -not $service.environment.DATABASE_STATEMENT_TIMEOUT_MS) { throw "Compose did not inject alert settings into $name." }
    }
    foreach ($name in @('scheduler','publisher','evaluator','notifier','delivery')) {
        $service = $services.PSObject.Properties[$name].Value
        if ($service.image -ne $services.backend.image -or (@($service.command) -join ' ') -ne "python -m app.alerts.worker $name" -or
            $service.depends_on.rabbitmq.condition -ne 'service_healthy' -or -not $service.read_only -or
            -not $service.healthcheck.disable) { throw "Worker $name is not configured for the reviewed backend image and broker." }
    }
    foreach ($name in @('sharepoint-publisher','sharepoint-consumer')) {
        $service = $services.PSObject.Properties[$name].Value
        $command = if ($name -eq 'sharepoint-publisher') { 'publisher' } else { 'consumer' }
        if ($service.image -ne $services.backend.image -or (@($service.command) -join ' ') -ne "python -m app.sharepoint_webhooks.worker $command" -or
            $service.depends_on.rabbitmq.condition -ne 'service_healthy' -or -not $service.read_only -or
            -not $service.healthcheck.disable) { throw "Worker $name is not configured for the reviewed backend image and broker." }
    }
}

try {
    if ([bool]$RuntimeEnvPath -eq [bool]$RuntimeOverlayPath) { throw 'Provide exactly one of RuntimeEnvPath or RuntimeOverlayPath.' }
    $overlayMode = [bool]$RuntimeOverlayPath
    if ($ConfirmUpdate -and $Action -ne 'Execute') { throw 'ConfirmUpdate applies only to Execute.' }
    if ($Action -eq 'Execute' -and -not $ConfirmUpdate) { throw 'Execution requires -Action Execute -ConfirmUpdate.' }
    foreach ($path in @($PrivateKeyPath, (Join-Path $script:AwsRepoRoot 'compose.prod.yml'), (Join-Path $script:AwsRepoRoot 'infra/aws/cloudwatch-agent.json'), (Join-Path $PSScriptRoot 'update-app-remote.sh'), (Join-Path $PSScriptRoot 'm7-compose-up.sh'), (Join-Path $PSScriptRoot 'restore-app-backup.sh'))) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw 'A required local file is missing.' }
    }
    $runtimePath = Assert-LocalRuntime -Path $(if ($overlayMode) { $RuntimeOverlayPath } else { $RuntimeEnvPath }) -Overlay:$overlayMode
    Assert-Compose -RuntimePath $runtimePath -Overlay:$overlayMode
    $ssh = Get-Command ssh -ErrorAction SilentlyContinue
    $scp = Get-Command scp -ErrorAction SilentlyContinue
    $sshKeygen = Get-Command ssh-keygen -ErrorAction SilentlyContinue
    if (-not $ssh -or -not $scp -or -not $sshKeygen) { throw 'OpenSSH ssh, scp and ssh-keygen are required.' }

    Import-M7AwsEnvironment
    $identity = Assert-M7AwsSession
    if ($env:AWS_DEFAULT_REGION -ne 'us-east-1' -or $EcrRegistryUri.Split('.')[0] -ne [string]$identity.Account) { throw 'AWS identity, region or ECR registry differs.' }
    $stack = Invoke-M7AwsJson -Arguments @('cloudformation','describe-stacks','--stack-name','m7-g05-mvp')
    if (@($stack.Stacks).Count -ne 1 -or $stack.Stacks[0].StackStatus -notin @('CREATE_COMPLETE','UPDATE_COMPLETE')) { throw 'Stack must be stable.' }
    $resource = Invoke-M7AwsJson -Arguments @('cloudformation','describe-stack-resource','--stack-name','m7-g05-mvp','--logical-resource-id','ApplicationInstance')
    if ($resource.StackResourceDetail.PhysicalResourceId -ne $InstanceId) { throw 'InstanceId is not the current stack instance.' }
    $instances = Invoke-M7AwsJson -Arguments @('ec2','describe-instances','--instance-ids',$InstanceId)
    $instance = @($instances.Reservations.Instances)[0]
    if (-not $instance -or $instance.State.Name -ne 'running' -or -not $instance.PublicIpAddress -or $instance.KeyName -ne $KeyPairName) { throw 'Target EC2 is not running with the expected public IP and key pair.' }
    $key = Invoke-M7AwsJson -Arguments @('ec2','describe-key-pairs','--key-names',$KeyPairName,'--include-public-key')
    $localPublic = Assert-CommandSucceeded -Program $sshKeygen.Source -Arguments @('-y','-f',$PrivateKeyPath) -Failure 'Cannot derive local public key.'
    if ($localPublic -notmatch '^ssh-ed25519\s+([A-Za-z0-9+/=]+)' -or $key.KeyPairs[0].PublicKey -notmatch '^ssh-ed25519\s+([A-Za-z0-9+/=]+)') { throw 'Key pair is not a matching ED25519 key.' }
    $awsPublic = $Matches[1]
    if ($localPublic -notmatch '^ssh-ed25519\s+([A-Za-z0-9+/=]+)' -or $Matches[1] -cne $awsPublic) { throw 'Private key does not match the imported key pair.' }
    $repos = Invoke-M7AwsJson -Arguments @('ecr','describe-repositories','--repository-names','m7-g05-backend','m7-g05-frontend')
    if (@($repos.Repositories).Count -ne 2 -or @($repos.Repositories | Where-Object { $_.ImageTagMutability -ne 'IMMUTABLE' }).Count) { throw 'Both ECR repositories must have immutable tags.' }
    foreach ($item in @(@{Name='m7-g05-backend';Tag=$BackendImageTag;Digest=$BackendImageDigest},@{Name='m7-g05-frontend';Tag=$FrontendImageTag;Digest=$FrontendImageDigest})) {
        $image = Invoke-M7AwsJson -Arguments @('ecr','describe-images','--repository-name',$item.Name,'--image-ids',"imageTag=$($item.Tag)")
        if (@($image.ImageDetails).Count -ne 1 -or $image.ImageDetails[0].ImageDigest -ne $item.Digest) { throw "Immutable tag/digest mismatch for $($item.Name)." }
    }
    $ip = [string]$instance.PublicIpAddress
    $knownHost = Assert-CommandSucceeded -Program $sshKeygen.Source -Arguments @('-F',$ip) -Failure 'Current SSH host key is not in known_hosts; verify it independently first.'
    if ([string]::IsNullOrWhiteSpace($knownHost)) { throw 'Current SSH host key is not in known_hosts.' }
    $sshArgs = @('-i',$PrivateKeyPath,'-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=10',"ubuntu@$ip")
    $null = Assert-CommandSucceeded -Program $ssh.Source -Arguments ($sshArgs + @('sudo -n test -f /etc/m7/deploy.env && sudo -n test -f /etc/m7/runtime.env && sudo -n test -f /opt/m7/compose.prod.yml && (sudo -n test -f /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json || sudo -n test -f /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.d/file_amazon-cloudwatch-agent.json)')) -Failure 'SSH host or required remote files are unavailable.'
    Write-Output "Read-only preflight passed for stack m7-g05-mvp and instance $InstanceId. Images and digests match; SSH host is trusted."
    if ($Action -eq 'Preflight') { Write-Output 'No files transferred and no remote mutation performed.'; return }

    if (-not $PSCmdlet.ShouldProcess("$InstanceId ($ip)",'Transfer application runtime and update containers over SSH')) { return }
    $stage = $null
    try {
        $stage = (Assert-CommandSucceeded -Program $ssh.Source -Arguments ($sshArgs + @('umask 077; mktemp -d /home/ubuntu/.m7-update-XXXXXXXX')) -Failure 'Could not create private remote stage.').Trim()
        if ($stage -notmatch '^/home/ubuntu/\.m7-update-[A-Za-z0-9]+$') { throw 'Remote stage path was invalid.' }
        $runtimeRemoteName = if ($overlayMode) { 'runtime.overlay' } else { 'runtime.env' }
        foreach ($file in @(@{Local=(Join-Path $script:AwsRepoRoot 'compose.prod.yml');Remote='compose.prod.yml'},@{Local=$runtimePath;Remote=$runtimeRemoteName},@{Local=(Join-Path $script:AwsRepoRoot 'infra/aws/cloudwatch-agent.json');Remote='cloudwatch-agent.json'},@{Local=(Join-Path $PSScriptRoot 'update-app-remote.sh');Remote='update-app-remote.sh'},@{Local=(Join-Path $PSScriptRoot 'm7-compose-up.sh');Remote='m7-compose-up.sh'},@{Local=(Join-Path $PSScriptRoot 'restore-app-backup.sh');Remote='restore-app-backup.sh'})) {
            $null = Assert-CommandSucceeded -Program $scp.Source -Arguments @('-i',$PrivateKeyPath,'-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-q',$file.Local,"ubuntu@${ip}:$stage/$($file.Remote)") -Failure 'Protected stage transfer failed.'
        }
        $runtimeMode = if ($overlayMode) { 'overlay' } else { 'full' }
        $result = Assert-CommandSucceeded -Program $ssh.Source -Arguments ($sshArgs + @("sudo -n bash $stage/update-app-remote.sh $stage $BackendImageTag $FrontendImageTag $runtimeMode")) -Failure 'Remote update failed; inspect root-only backup and container health before retrying.'
        if ($result -notmatch 'Update healthy\. Root-only backup: (/etc/m7/backups/update-[A-Za-z0-9]{8})') { throw 'Remote health completed without a verifiable backup path.' }
        Write-Output "Root-only restore point: $($Matches[1])"
        Write-Output 'Remote update and health check completed. Review /health and alert workflow before sharing the service.'
    } finally {
        if ($stage -match '^/home/ubuntu/\.m7-update-[A-Za-z0-9]+$') {
            try {
                $previousPreference = $ErrorActionPreference
                $ErrorActionPreference = 'Continue'
                $null = & $ssh.Source @sshArgs "rm -f $stage/compose.prod.yml $stage/runtime.env $stage/runtime.overlay $stage/cloudwatch-agent.json $stage/update-app-remote.sh $stage/m7-compose-up.sh $stage/restore-app-backup.sh; rmdir $stage 2>/dev/null || true" 2>$null
            } catch { } finally { $ErrorActionPreference = $previousPreference }
        }
    }
} catch {
    if ($_.Exception.Message -eq 'CREDENTIALS_EXPIRED') { Write-Error 'STATUS: CREDENCIAIS_EXPIRADAS.'; exit 3 }
    Write-Error $_.Exception.Message
    exit 1
}
