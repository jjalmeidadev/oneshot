$ErrorActionPreference = "Stop"

$repoRoot = git rev-parse --show-toplevel
if (-not $repoRoot) {
    Write-Error "Nao foi possivel localizar a raiz do repositorio Git."
    exit 1
}

Set-Location $repoRoot
git config core.hooksPath .githooks

Write-Host "Hooks Git instalados com sucesso."
Write-Host "core.hooksPath configurado para .githooks"
Write-Host "Repositorio: $repoRoot"
