[CmdletBinding()]
param(
    [string]$DatabaseUrl = $(if ($env:DATABASE_URL) { $env:DATABASE_URL } else { $env:SUPABASE_DATABASE_URL }),
    [switch]$ApplySchema,
    [switch]$TestSchemaReexecution,
    [string]$EvidenceDirectory
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($EvidenceDirectory)) {
    $EvidenceDirectory = Join-Path $PSScriptRoot "..\\src\\database\\docs\\evidencias"
}

if ([string]::IsNullOrWhiteSpace($DatabaseUrl)) {
    throw 'Defina DATABASE_URL ou SUPABASE_DATABASE_URL localmente. A URL nao e gravada nem exibida por este script.'
}

$psql = Get-Command psql -ErrorAction SilentlyContinue
if ($null -eq $psql) {
    $installedPsql = Join-Path $env:ProgramFiles 'PostgreSQL\16\bin\psql.exe'
    if (Test-Path -LiteralPath $installedPsql) {
        $psqlPath = $installedPsql
    } else {
        throw 'psql nao foi encontrado no PATH nem na instalacao padrao do PostgreSQL 16.'
    }
} else {
    $psqlPath = $psql.Source
}

$sqlRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\\src\\database\\sql")).Path
$correlationId = "s4-db-$([guid]::NewGuid().ToString('N'))"

function Invoke-PsqlFile {
    param([Parameter(Mandatory)][string]$Path)

    & $psqlPath --no-psqlrc -X -v ON_ERROR_STOP=1 --dbname=$DatabaseUrl --file=$Path
    if ($LASTEXITCODE -ne 0) { throw "Falha ao executar $Path (psql exit code $LASTEXITCODE)." }
}

function Invoke-PsqlQuery {
    param([Parameter(Mandatory)][string]$Query)

    $result = & $psqlPath --no-psqlrc -X -v ON_ERROR_STOP=1 --tuples-only --no-align --dbname=$DatabaseUrl --command=$Query
    if ($LASTEXITCODE -ne 0) { throw "Falha na consulta de verificacao (psql exit code $LASTEXITCODE)." }
    return @($result | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
}

function ConvertFrom-Base64Text {
    param([Parameter(Mandatory)][string]$Value)

    return [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($Value))
}

$schemaQuery = @'
SELECT encode(convert_to(json_build_object(
  'postgres_version', current_setting('server_version'),
  'tables', (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = 'public' AND c.relkind IN ('r', 'p')),
  'explicit_indexes', (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = 'public' AND c.relkind = 'i' AND NOT EXISTS (SELECT 1 FROM pg_constraint con WHERE con.conindid = c.oid)),
  'triggers', (SELECT count(*) FROM pg_trigger t JOIN pg_class c ON c.oid = t.tgrelid JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = 'public' AND NOT t.tgisinternal)
)::text, 'UTF8'), 'base64');
'@

$domainQuery = @'
WITH domain_counts(domain, total) AS (
  VALUES
    ('subportfolios', (SELECT count(*) FROM public.subportfolios WHERE partner_source_id = 'SUB-MOCK-001')),
    ('projects', (SELECT count(*) FROM public.projects WHERE partner_source_id = 'PRJ-MOCK-0442')),
    ('artifacts_initial', (SELECT count(*) FROM public.project_artifacts WHERE partner_source_id = 'ART-MOCK-TAP-0442')),
    ('artifacts_rag', (SELECT count(*) FROM public.project_artifacts WHERE partner_source_id LIKE 'sharepoint-mock:%')),
    ('source_extracts_rag', (SELECT count(*) FROM public.source_extracts WHERE metadata ->> 'mock' = 'true')),
    ('charters', (SELECT count(*) FROM public.project_charters WHERE partner_source_id = 'TAP-MOCK-0442-R1')),
    ('benefits', (SELECT count(*) FROM public.project_benefits WHERE metadata ->> 'mock' = 'true')),
    ('progress_updates', (SELECT count(*) FROM public.project_progress_updates WHERE partner_source_id = 'AV-MOCK-0442-202608')),
    ('deliverables', (SELECT count(*) FROM public.project_deliverables_milestones WHERE metadata ->> 'mock' = 'true')),
    ('risks', (SELECT count(*) FROM public.risk_issue_items WHERE partner_source_id = 'RISK-MOCK-0442-001')),
    ('intent_catalog', (SELECT count(*) FROM public.intent_catalog)),
    ('secondary_intents', (SELECT count(*) FROM public.secondary_intents WHERE is_active))
)
SELECT encode(convert_to(json_object_agg(domain, total ORDER BY domain)::text, 'UTF8'), 'base64') FROM domain_counts;
'@

if ($ApplySchema) {
    Invoke-PsqlFile (Join-Path $sqlRoot '01_create_database.sql')
}

# A carga e executada duas vezes de proposito: o resultado deve ser identico.
Invoke-PsqlFile (Join-Path $sqlRoot '02_initial_data.sql')
Invoke-PsqlFile (Join-Path $sqlRoot '04_rag_synthetic_data.sql')
$firstSnapshot = ConvertFrom-Base64Text ([string](Invoke-PsqlQuery $domainQuery))

Invoke-PsqlFile (Join-Path $sqlRoot '02_initial_data.sql')
Invoke-PsqlFile (Join-Path $sqlRoot '04_rag_synthetic_data.sql')
$secondSnapshot = ConvertFrom-Base64Text ([string](Invoke-PsqlQuery $domainQuery))

if ($firstSnapshot -ne $secondSnapshot) {
    throw "A carga sintetica nao foi idempotente. Primeira contagem: $firstSnapshot. Segunda contagem: $secondSnapshot"
}

$schemaSnapshot = ConvertFrom-Base64Text ([string](Invoke-PsqlQuery $schemaQuery))
$auditPayloadBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($schemaSnapshot))
Invoke-PsqlQuery "INSERT INTO public.audit_events (event_type, component, event_status, correlation_id, event_payload) VALUES ('s4_schema_and_seed_verification', 'database', 'sucesso', '$correlationId', convert_from(decode('$auditPayloadBase64', 'base64'), 'UTF8')::jsonb);"

if ($TestSchemaReexecution) {
    $baselinePath = Join-Path $sqlRoot '01_create_database.sql'
    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        & $psqlPath --no-psqlrc -X -v ON_ERROR_STOP=1 --dbname=$DatabaseUrl --file=$baselinePath *> $null
        $schemaReexecutionExitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    if ($schemaReexecutionExitCode -eq 0) { throw 'A reexecucao do baseline deveria falhar; ela nao e uma migracao incremental.' }
}

New-Item -ItemType Directory -Force -Path $EvidenceDirectory | Out-Null
$evidence = [ordered]@{
    correlation_id = $correlationId
    executed_at_utc = (Get-Date).ToUniversalTime().ToString('o')
    schema = ($schemaSnapshot | ConvertFrom-Json)
    first_load_counts = ($firstSnapshot | ConvertFrom-Json)
    second_load_counts = ($secondSnapshot | ConvertFrom-Json)
    idempotent = $true
    schema_reexecution = if ($TestSchemaReexecution) { 'expected_failure_confirmed' } else { 'not_requested' }
}
$evidencePath = Join-Path $EvidenceDirectory ("s4-verification-$correlationId.json")
$evidence | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $evidencePath -Encoding utf8

Write-Host "Verificacao concluida. Correlation ID: $correlationId"
Write-Host "Evidencia: $evidencePath"
