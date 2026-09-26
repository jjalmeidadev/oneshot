$ErrorActionPreference = 'Stop'

$backendPath = Resolve-Path (Join-Path $PSScriptRoot '..')
$pythonPath = Resolve-Path (Join-Path $backendPath '.venv\Scripts\python.exe')
$runtimePath = Resolve-Path (Join-Path $backendPath '.runtime')

# Segredo efêmero apenas para desenvolvimento local. Produção deve fornecer
# ALERT_CONFIRMATION_SECRET por um gerenciador de segredos.
$secretBytes = New-Object byte[] 32
$generator = [Security.Cryptography.RandomNumberGenerator]::Create()
$generator.GetBytes($secretBytes)
$generator.Dispose()
$env:ALERT_CONFIRMATION_SECRET = ([BitConverter]::ToString($secretBytes)).Replace('-', '')
$env:PLN_WARMUP = '0'

$processes = @()
$processes += Start-Process -FilePath $pythonPath -ArgumentList '-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000' -WorkingDirectory $backendPath -WindowStyle Hidden -RedirectStandardOutput "$runtimePath\alert-api.out.log" -RedirectStandardError "$runtimePath\alert-api.err.log" -PassThru
foreach ($worker in @('scheduler', 'publisher', 'evaluator', 'notifier')) {
    $processes += Start-Process -FilePath $pythonPath -ArgumentList '-m','app.alerts.worker',$worker -WorkingDirectory $backendPath -WindowStyle Hidden -RedirectStandardOutput "$runtimePath\alert-$worker.out.log" -RedirectStandardError "$runtimePath\alert-$worker.err.log" -PassThru
}

$processes | Select-Object Id, ProcessName
