# Evidências S4-31 — VHS/cache

Plano e critérios: [plano-vhs.md](../../../testes/sprint4/plano-vhs.md).
Reprodução: em `src/backend`, executar `python scripts/verify_vhs.py`.

Rodada final: [20260925T171443134942Z](20260925T171443134942Z/resultado.json).
**81 testes aprovados em 36,20 s; coletor encerrado com código 0.**
Consultar [ambiente congelado](20260925T171443134942Z/ambiente.json),
[saída pytest](20260925T171443134942Z/pytest.txt) e
[JUnit com métricas](20260925T171443134942Z/pytest.xml).
Os SHA-256 identificam a implementação/testes da árvore local sobre o commit-base;
não se afirma que o commit-base já contém estas alterações.

| Validação | Escopo e evidência |
|---|---|
| Gravação e hit | Dois uploads, uma chamada HTTP; transcrição reproduzida e contadores comparados |
| Miss e isolamento | Áudio, idioma ou recurso diferentes fazem nova chamada |
| TTL e invalidação | Expiração e remoção explícita forçam nova chamada; invalidação em voo não repovoa cache |
| Erros e recuperação | 502/503/429/422 preservados; falhas não gravadas; nova tentativa aciona provedor |
| Concorrência e capacidade | Dez consultas iguais fazem uma chamada; LRU limita entradas |
| Regressão de áudio | Suíte existente de upload, autenticação, validação e cliente Azure |
| Azure/Copilot publicados | Não executados; S4-22/S4-28 não confirmadas nesta rodada |
| RNFs de carga e usabilidade | Não executados; duração do teste local não comprova RNF05 |

Sem rede real: o HTTP do Azure é substituído por resposta controlada e contado.
O PLN/LLM e a persistência do pipeline são substituídos na suíte de upload.
As evidências aprovam somente o escopo local testado. O cache é em memória,
por worker, com TTL de 300 s e capacidade de 256; não persiste após reinício.

## Defeito encontrado e reteste

Na [primeira coleta](20260925T171307400200Z/resultado.json), os 81 testes
passaram, mas o coletor falhou depois de gravar os arquivos ao imprimir no
terminal cp1252 do Windows (`UnicodeEncodeError`). Essa rodada preservada
comprova os testes, mas **falhou na conclusão do comando de coleta**; o
`exit_code: 0` do JSON antigo é do subprocesso pytest, não do coletor.
Correção: UTF-8 explícito na saída do subprocesso e do coletor. A rodada final
acima é o reteste do comando. A primeira coleta também contém caracteres de
caminho substituídos no TXT, limitação corrigida no reteste.

O warning de depreciação Starlette/httpx é da dependência existente; não houve
troca de dependências nesta entrega. Casos não exercitados ficam como
`nao executado`; um bloqueio só deve ser declarado após observar impedimento
concreto, com motivo e responsável. Falhas de assertions geram `falhou` com
traceback. Nenhum aceite externo é inferido do resultado local.
