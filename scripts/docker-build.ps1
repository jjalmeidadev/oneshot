param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^(?!latest$)[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$')]
    [string]$Tag,

    [switch]$WithNotebook
)

$ErrorActionPreference = 'Stop'
$env:APP_IMAGE_TAG = $Tag

docker compose -f compose.prod.yml build backend frontend
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

if ($WithNotebook) {
    docker compose --profile notebook -f compose.prod.yml build notebook
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
