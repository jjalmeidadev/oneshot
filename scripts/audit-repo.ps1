param(
    [string]$BaseBranch = ""
)

$ErrorActionPreference = "Stop"

$homologacaoComAcento = "homologa" + [char]0x00E7 + [char]0x00E3 + "o"
$protectedBranches = @("main", "dev", "develop", "hmg", "homologacao", $homologacaoComAcento)
$validPrefixes = @(
    "feature/",
    "feat/",
    "fix/",
    "bugfix/",
    "hotfix/",
    "docs/",
    "doc/",
    "style/",
    "refactor/",
    "test/",
    "chore/",
    "perf/",
    "ci/",
    "build/",
    "release/"
)
$commitPattern = "^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\([A-Za-z0-9._-]+\))?!?: .+$"
$issuePattern = "#[0-9]+"
$failures = 0
$warnings = 0

function Invoke-Git {
    param([string[]]$Arguments)

    $output = & git @Arguments 2>$null
    return @{
        ExitCode = $LASTEXITCODE
        Output = $output
    }
}

function Write-Result {
    param(
        [ValidateSet("OK", "WARN", "FAIL")]
        [string]$Level,
        [string]$Message,
        [string]$Fix = ""
    )

    Write-Host "[$Level] $Message"
    if ($Fix) {
        Write-Host "      Como corrigir: $Fix"
    }

    if ($Level -eq "FAIL") {
        $script:failures++
    }
    elseif ($Level -eq "WARN") {
        $script:warnings++
    }
}

function Test-RefExists {
    param([string]$Ref)

    $result = Invoke-Git @("rev-parse", "--verify", "$Ref^{commit}")
    return $result.ExitCode -eq 0
}

function Test-ValidBranchPrefix {
    param([string]$Branch)

    foreach ($prefix in $validPrefixes) {
        if ($Branch.StartsWith($prefix)) {
            return $true
        }
    }
    return $false
}

$repoRootResult = Invoke-Git @("rev-parse", "--show-toplevel")
if ($repoRootResult.ExitCode -ne 0) {
    Write-Result "FAIL" "Diretorio atual nao esta dentro de um repositorio Git." "Execute o script a partir do repositorio g05."
    exit 1
}

$repoRoot = ($repoRootResult.Output | Select-Object -First 1)
Set-Location $repoRoot

Write-Host "Auditoria local do repositorio"
Write-Host "Repositorio: $repoRoot"

if (-not $BaseBranch) {
    if (Test-RefExists "origin/develop") {
        $BaseBranch = "origin/develop"
    }
    else {
        $BaseBranch = "develop"
    }
}
Write-Host "Base de comparacao: $BaseBranch"
Write-Host ""

$branchResult = Invoke-Git @("branch", "--show-current")
$currentBranch = (($branchResult.Output | Select-Object -First 1) -as [string])

if ($currentBranch) {
    Write-Result "OK" "Branch atual: $currentBranch"
}
else {
    Write-Result "WARN" "Estado detached HEAD detectado; nao ha branch atual nomeada." "Volte para uma branch de trabalho antes de abrir MR."
}

if ($currentBranch -and ($protectedBranches -contains $currentBranch)) {
    Write-Result "FAIL" "A branch atual '$currentBranch' e permanente." "Crie uma branch de trabalho, por exemplo: feature/minha-tarefa ou docs/atualizar-readme."
}
elseif ($currentBranch) {
    Write-Result "OK" "A branch atual nao e permanente."
}

if ($currentBranch) {
    if (Test-ValidBranchPrefix $currentBranch) {
        Write-Result "OK" "A branch atual usa prefixo valido."
    }
    else {
        Write-Result "FAIL" "A branch atual '$currentBranch' nao usa prefixo valido." "Use um destes prefixos: $($validPrefixes -join ', ')"
    }
}

$baseExists = Test-RefExists $BaseBranch
if ($baseExists) {
    Write-Result "OK" "Base '$BaseBranch' encontrada para auditar commits em $BaseBranch..HEAD."
    $commitResult = Invoke-Git @("log", "--format=%H", "$BaseBranch..HEAD")
}
else {
    Write-Result "WARN" "Base '$BaseBranch' nao encontrada; usando os ultimos 20 commits." "Execute git fetch ou informe uma base existente com -BaseBranch develop."
    $commitResult = Invoke-Git @("log", "--format=%H", "-n", "20")
}

$commits = @()
if ($commitResult.ExitCode -eq 0 -and $commitResult.Output) {
    $commits = @($commitResult.Output)
}

if ($commits.Count -eq 0) {
    Write-Result "OK" "Nenhum commit recente novo detectado para auditar."
}
else {
    $invalidConventional = @()
    $missingIssue = @()

    foreach ($commit in $commits) {
        $subject = (Invoke-Git @("log", "-1", "--format=%s", $commit)).Output | Select-Object -First 1
        $message = (Invoke-Git @("log", "-1", "--format=%s%n%b", $commit)).Output -join "`n"

        if ($subject -notmatch $commitPattern) {
            $invalidConventional += "$($commit.Substring(0, 7)) $subject"
        }

        if ($message -notmatch $issuePattern) {
            $missingIssue += "$($commit.Substring(0, 7)) $subject"
        }
    }

    if ($invalidConventional.Count -eq 0) {
        Write-Result "OK" "Commits recentes seguem Conventional Commits."
    }
    else {
        Write-Result "FAIL" "Commits recentes fora de Conventional Commits: $($invalidConventional -join '; ')" "Reescreva as mensagens antes do MR. Exemplo: feat(auth): adicionar login (#12)"
    }

    if ($missingIssue.Count -eq 0) {
        Write-Result "OK" "Commits recentes contem referencia #N."
    }
    else {
        Write-Result "FAIL" "Commits recentes sem referencia #N: $($missingIssue -join '; ')" "Inclua a issue da sprint na mensagem, por exemplo: (#12)."
    }
}

$requiredFiles = @(
    ".githooks/commit-msg",
    ".githooks/pre-commit",
    ".githooks/pre-push",
    ".gitlab/issue_templates/Tarefa.md"
)

foreach ($file in $requiredFiles) {
    if (Test-Path -LiteralPath $file) {
        Write-Result "OK" "Arquivo encontrado: $file"
    }
    else {
        Write-Result "FAIL" "Arquivo ausente: $file" "Restaure ou crie o arquivo versionado esperado."
    }
}

$hooksPathResult = Invoke-Git @("config", "core.hooksPath")
$hooksPath = (($hooksPathResult.Output | Select-Object -First 1) -as [string])
if ($hooksPath -eq ".githooks") {
    Write-Result "OK" "core.hooksPath configurado para .githooks."
}
elseif ($hooksPath) {
    Write-Result "FAIL" "core.hooksPath esta configurado como '$hooksPath'." "Rode powershell -ExecutionPolicy Bypass -File scripts/install-hooks.ps1"
}
else {
    Write-Result "FAIL" "core.hooksPath nao esta configurado." "Rode powershell -ExecutionPolicy Bypass -File scripts/install-hooks.ps1"
}

Write-Host ""
Write-Host "Resumo: $failures falha(s), $warnings aviso(s)."

if ($failures -gt 0) {
    exit 1
}

exit 0
