# Launcher desacoplado do fluxo completo para teste manual.
# Sobe API + workers (scheduler, publisher, evaluator, notifier) + frontend.
# Cada processo roda em janela propria e NAO fica vinculado ao shell chamador,
# evitando qualquer bloqueio do terminal que dispara este script.

$ErrorActionPreference = 'Stop'

$backendPath = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$repoRoot = (Resolve-Path (Join-Path $backendPath '..\..')).Path
$frontendPath = (Resolve-Path (Join-Path $repoRoot 'src\frontend')).Path
$pythonPath = (Resolve-Path (Join-Path $backendPath '.venv\Scripts\python.exe')).Path
$runtimePath = Join-Path $backendPath '.runtime'
if (-not (Test-Path $runtimePath)) { New-Item -ItemType Directory -Path $runtimePath | Out-Null }

# Segredo de confirmacao compartilhado e estavel durante a sessao de teste.
# Persistido em arquivo para que API e workers usem exatamente o mesmo valor.
$secretFile = Join-Path $runtimePath 'alert-secret.txt'
if (-not (Test-Path $secretFile)) {
    $bytes = New-Object byte[] 32
    $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    $rng.GetBytes($bytes); $rng.Dispose()
    ([BitConverter]::ToString($bytes)).Replace('-', '') | Set-Content -LiteralPath $secretFile -NoNewline
}
$secret = (Get-Content -LiteralPath $secretFile -Raw).Trim()

# Inicia um processo desacoplado, redirecionando logs, sem prender o shell atual.
function Start-Detached {
    param([string]$Name, [string]$File, [string[]]$ArgList, [string]$WorkDir, [hashtable]$ExtraEnv)
    $envPrefix = "`$env:ALERT_CONFIRMATION_SECRET='$secret'; `$env:PLN_WARMUP='0'; "
    if ($ExtraEnv) { foreach ($k in $ExtraEnv.Keys) { $envPrefix += "`$env:$k='$($ExtraEnv[$k])'; " } }
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
Start-Detached -Name 'frontend' -File 'npm.cmd' -ArgList @('run','dev') -WorkDir $frontendPath

Write-Output 'STACK_LAUNCHED'
