# S4-09 — carga sintetica idempotente

Execute `02_initial_data.sql` e `04_rag_synthetic_data.sql` duas vezes no
mesmo ambiente. As contagens de subportfolios, projetos, artefatos, extratos,
TAP, beneficios, avancos, entregas, riscos e intencoes devem permanecer
iguais entre as execucoes.

`scripts/verify-supabase.ps1` automatiza essa comparacao e salva uma evidencia
JSON local com o identificador de correlacao usado no evento de auditoria.
