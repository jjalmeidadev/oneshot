param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^(?!latest$)[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$')]
    [string]$Tag
)

$ErrorActionPreference = 'Stop'
$env:APP_IMAGE_TAG = $Tag

$configOutput = docker compose -f compose.prod.yml config --format json
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$config = ($configOutput -join "`n") | ConvertFrom-Json -ErrorAction Stop
$runtime = $config.services.backend.environment
$audioEntries = @(
    ([string]$runtime.AUDIO_SIMULATED_IDENTITIES -split ',') |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ }
)
if (-not $audioEntries.Count -or @($audioEntries | Where-Object { $_ -notmatch '^.+?=.+$' }).Count) {
    throw 'Configure AUDIO_SIMULATED_IDENTITIES no formato token=entra_object_id.'
}

try {
    $reportIdentities = ([string]$runtime.REPORT_SIMULATED_IDENTITIES | ConvertFrom-Json -ErrorAction Stop)
} catch {
    throw 'Configure REPORT_SIMULATED_IDENTITIES como objeto JSON não vazio.'
}
$reportEntries = @($reportIdentities.PSObject.Properties | ForEach-Object { $_.Value })
if (-not $reportEntries.Count -or @($reportEntries | Where-Object {
    -not $_.subject -or -not $_.role
}).Count) {
    throw 'Cada identidade de relatório deve incluir subject e role.'
}
if ([string]::IsNullOrWhiteSpace([string]$runtime.GEMINI_API_KEY) -or
    [string]::IsNullOrWhiteSpace([string]$runtime.AZURE_SPEECH_KEY) -or
    ([string]::IsNullOrWhiteSpace([string]$runtime.AZURE_SPEECH_RESOURCE) -and
     [string]::IsNullOrWhiteSpace([string]$runtime.AZURE_SPEECH_ENDPOINT))) {
    throw 'Configure as credenciais runtime de Gemini e Azure Speech.'
}

docker compose -f compose.prod.yml up -d
exit $LASTEXITCODE
