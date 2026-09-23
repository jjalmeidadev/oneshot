# Evidência do RNF06 — issue #232

## Objetivo e protocolo

O RNF06 exige simultaneamente F1-macro mínimo de 0,80 na classificação de
intenções e *recall*@3 mínimo de 0,80 na recuperação de informações. A
avaliação prospectiva ampliada usa 72 consultas novas, oito por fonte e nove
por tipo de variação linguística. A implementação, a massa, os limiares e os
hashes foram congelados antes da execução em
[`massa-congelada-v2.json`](massa-congelada-v2.json).

A massa v2 não contém consultas idênticas às 18 da avaliação v1. Ela cobre
paráfrases, sinônimos novos, formulações coloquiais e implícitas, erros leves,
consultas curtas e longas e detalhes operacionais. A execução foi única: após
observar o resultado, nem o recuperador nem a massa foram ajustados.

A classificação usa as 1.135 solicitações do `split == teste`, o classificador
versão 2 e o snapshot imutável
`94d69c95f98f7d5b2a8700c420230ae10def0baa` do BERTimbau, sem retreino.

## Execução prospectiva v2

- Data: 23 de setembro de 2026.
- Responsável: Pedro Damacena Machado Uchoa.
- Implementação congelada: `73e36def87e31b66a731d0d0939f9f6174b62206`.
- Commit executado: `c627dd26525472d9ca3e2a9592abbca15059d5aa`.
- Ambiente: Windows, Python 3.13.15, scikit-learn 1.6.1, NumPy 2.5.2,
  joblib 1.6.0, Torch 2.13.0 e Transformers 5.16.1.
- Evidência estruturada: [`resultado-rnf06-v2.json`](resultado-rnf06-v2.json).

Comando reproduzível, a partir de `src/backend`:

```powershell
..\..\.venv\Scripts\python.exe scripts\benchmark_rnf06.py
```

O comando retorna código 0 somente quando F1-macro, *recall*@3 pontual e o
limite inferior do intervalo de confiança de Wilson a 95% atingem 0,80. A
execução v2 terminou com código 1 e foi preservada sem nova tentativa.

## Resultados observados

| Componente | Métrica | Resultado | Limiar | Situação |
| --- | --- | ---: | ---: | --- |
| Classificação de intenção específica | Acurácia | 0,839648 | Informativa | Medida |
| Classificação de intenção específica | F1-macro | 0,832724 | ≥ 0,80 | Aprovado |
| Recuperação — 72 consultas | *Recall*@3 | 0,555556 (40/72) | ≥ 0,80 | Reprovado |
| Recuperação — incerteza amostral | IC de Wilson 95% | [0,440874; 0,664609] | Limite inferior ≥ 0,80 | Reprovado |
| RNF06 consolidado | Critérios simultâneos | F1 0,832724; *recall*@3 0,555556 | ≥ 0,80 | **Reprovado** |

O desempenho por variação foi:

| Tipo de consulta | Acertos | *Recall*@3 |
| --- | ---: | ---: |
| Coloquial | 5/9 | 0,555556 |
| Consulta curta | 3/9 | 0,333333 |
| Consulta longa | 8/9 | 0,888889 |
| Detalhe operacional | 8/9 | 0,888889 |
| Erro leve | 5/9 | 0,555556 |
| Formulação implícita | 4/9 | 0,444444 |
| Paráfrase | 4/9 | 0,444444 |
| Sinônimo novo | 3/9 | 0,333333 |

Consultas curtas, sinônimos novos, formulações implícitas e paráfrases são os
principais pontos de fragilidade. Na classificação, as classes mais frágeis
continuam sendo `analise_tendencia_desempenho` (F1 0,041667),
`consulta_indicadores_kpi` (0,587156) e `consulta_orcamento_custo` (0,676056).

## Interpretação das rodadas anteriores

A linha de base v1, executada em 22 de setembro, recuperou 11 de 18 fontes e
obteve *recall*@3 de 0,611111. Depois dela, o recuperador recebeu equivalências
lexicais derivadas dos próprios erros dessa massa. A nova execução sobre os
mesmos 18 casos chegou a 1,000000, mas esse valor mede apenas regressão dos
casos já conhecidos: houve contaminação entre avaliação e ajuste, portanto ele
não é evidência válida de generalização nem sustenta aprovação do RNF06.

Os arquivos `massa-congelada.json` e `resultado-rnf06.json` permanecem
versionados para rastreabilidade histórica. A conclusão vigente é determinada
pela avaliação prospectiva v2.

## Conclusão e limitações

O RNF06 está **reprovado**: a classificação supera 0,80, porém a recuperação
atinge *recall*@3 de 0,555556, com intervalo de confiança incompatível com o
limiar. A implementação não deve ser ajustada com base nesses 72 casos e depois
reavaliada na mesma massa; uma melhoria futura precisa usar dados de
desenvolvimento separados e outro conjunto prospectivo ainda não observado.

A v2 é mais confiável que a reexecução contaminada porque foi criada e
congelada contra a implementação anterior e usada uma única vez. Ainda assim,
ela foi escrita internamente e não de forma cega, usa fontes sintéticas locais
e não substitui uma amostra externa de solicitações reais nem a homologação com
o SharePoint do parceiro.
