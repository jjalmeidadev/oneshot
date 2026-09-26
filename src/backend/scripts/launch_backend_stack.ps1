# Sobe apenas API + workers de alerta, desacoplados do shell chamador.
# O frontend e iniciado separadamente por launch_full_stack.ps1.

$ErrorActionPreference = 'Stop'

$backendPath = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$pythonPath = (Resolve-Path (Join-Path $backendPath '.venv\Scripts\python.exe')).Path
$runtimePath = Join-Path $backendPath '.runtime'
if (-not (Test-Path $runtimePath)) { New-Item -ItemType Directory -Path $runtimePath | Out-Null }

$secretFile = Join-Path $runtimePath 'alert-secret.txt'
if (-not (Test-Path $secretFile)) {
    $bytes = New-Object byte[] 32
    $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    $rng.GetBytes($bytes); $rng.Dispose()
    ([BitConverter]::ToString($bytes)).Replace('-', '') | Set-Content -LiteralPath $secretFile -NoNewline
}
$secret = (Get-Content -LiteralPath $secretFile -Raw).Trim()

function Start-Detached {
    param([string]$Name, [string]$File, [string[]]$ArgList, [string]$WorkDir)
    $envPrefix = "`$env:ALERT_CONFIRMATION_SECRET='$secret'; `$env:PLN_WARMUP='0'; "
    $argString = ($ArgList | ForEach-Object { '"' + $_ + '"' }) -join ' '
    $outLog = Join-Path $runtimePath "$Name.out.log"
    $errLog = Join-Path $runtimePath "$Name.err.log"
    $inner = "$envPrefix Set-Location '$WorkDir'; & '$File' $argString *> '$outLog' 2> '$errLog'"
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($inner))
    Start-Process -FilePath 'powershell.exe' -ArgumentList '-NoProfile','-WindowStyle','Hidden','-EncodedCommand',$encoded -WindowStyle Hidden | Out-Null
}

Start-Detached -Name 'alert-api' -File $pythonPath -ArgList @('-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000') -WorkDir $backendPath
foreach ($worker in @('scheduler','publisher','evaluator','notifier')) {
    Start-Detached -Name "alert-$worker" -File $pythonPath -ArgList @('-m','app.alerts.worker',$worker) -WorkDir $backendPath
}

Write-Output "BACKEND_LAUNCHED secret=$($secret.Substring(0,8))..."
