# Fase 4 — infraestrutura local do MVP AWS

Status: Ready for Review

## Objetivo

Preparar artefatos locais para uma implantação temporária de quatro dias no AWS
Learner Lab, sem criar ou alterar recursos AWS.

## Critérios de aceite

- [x] Uma EC2 `t3.large` por padrão, com fallback explícito `t3.xlarge`.
- [x] EBS gp3 de 50 GiB.
- [x] Security Group sem regras de entrada.
- [x] Acesso à aplicação documentado por túnel SSM para `localhost:8080`.
- [x] Backend e frontend preparados para dois repositórios ECR.
- [x] Notebook desligado e fora do pull inicial.
- [x] Runtime local, em memória e sintético, sem Supabase.
- [x] Secrets fora de template, User Data, imagens e Git.
- [x] Logs mínimos com retenção curta.
- [x] Descoberta read-only e preflight documentados.
- [x] Custo estimado para quatro dias.
- [x] Pausa diária e encerramento documentados.
- [x] Nenhum recurso AWS criado ou alterado.
- [ ] `cloudformation:ValidateTemplate` executado com sucesso.

O último item permanece pendente porque a identidade atual retornou
`AccessDenied`. O estado é `AWS_TEMPLATE_VALIDATION_UNAVAILABLE`, separado dos
gates locais de sintaxe e estrutura.

## File List

- `compose.prod.yml`
- `docs/aws-operacao.md`
- `docs/docker-operacao.md`
- `docs/stories/phase-4-aws-mvp.md`
- `infra/aws/cloudwatch-agent.json`
- `infra/aws/template.yaml`
- `infra/aws/user-data.sh`
- `scripts/aws/common.ps1`
- `scripts/aws/deploy.ps1`
- `scripts/aws/rollback.ps1`
