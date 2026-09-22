# Evidencias locais de verificacao

Os arquivos JSON desta pasta sao gerados por `scripts/verify-supabase.ps1` e
nao devem conter URL, senha, chave ou outro segredo. Cada arquivo registra o
ID de correlacao, a versao do PostgreSQL, a conferencia do esquema e as duas
contagens da carga sintetica.

O baseline atual (`01_create_database.sql`) possui **27 tabelas, 46 indices
explicitos e 27 triggers**. A meta historica de 25/43/25 precede a inclusao de
`secondary_intents` e `pending_proactive_suggestions`, com seus respectivos
indices e triggers.
