# Evidência do RNF06 — issue #232

## Objetivo e protocolo

Esta execução mede os dois critérios indivisíveis do RNF06: F1-macro mínimo
de 0,80 na classificação de intenções e *recall*@3 mínimo de 0,80 na
recuperação de informações. A massa, os limiares e os hashes foram congelados
antes da execução em [`massa-congelada.json`](massa-congelada.json); nenhum
exemplo foi removido, reclassificado ou incorporado ao treino após a medição.

A classificação usa as 1.135 solicitações do `split == teste`, o classificador
versão 2 e o snapshot imutável
`94d69c95f98f7d5b2a8700c420230ae10def0baa` do BERTimbau, sem retreino. A
recuperação usa 18 consultas: nove formulações diretas e nove paráfrases com
variação lexical, cada uma com uma fonte relevante previamente rotulada.

## Execução

- Data: 22 de setembro de 2026.
- Responsável: Pedro Damacena Machado Uchoa.
- Commit executado: `b827aa8ecda5693987040859595741021699f05a`.
- Ambiente: Windows, Python 3.13.15, scikit-learn 1.6.1, NumPy 2.5.2,
  joblib 1.6.0, Torch 2.13.0 e Transformers 5.16.1.
- Evidência estruturada: [`resultado-rnf06.json`](resultado-rnf06.json).

Comando reproduzível, a partir de `src/backend`:

```powershell
..\..\.venv\Scripts\python.exe scripts\benchmark_rnf06.py
```

O comando retorna código 1 quando qualquer critério fica abaixo do limiar. Esse
retorno representa uma reprovação detectada corretamente, não uma falha de
execução do benchmark.

## Resultados observados

| Componente | Métrica | Resultado | Limiar | Situação |
| --- | --- | ---: | ---: | --- |
| Classificação de intenção específica | Acurácia | 0,839648 | Informativa | Medida |
| Classificação de intenção específica | F1-macro | 0,832724 | ≥ 0,80 | Aprovado |
| Recuperação — formulações diretas | *Recall*@3 | 1,000000 | ≥ 0,80 | Aprovado |
| Recuperação — desafio lexical | *Recall*@3 | 0,222222 | ≥ 0,80 | Reprovado |
| Recuperação — conjunto completo | *Recall*@3 | 0,611111 | ≥ 0,80 | Reprovado |

O recuperador encontrou 11 das 18 fontes relevantes. As nove consultas diretas
foram recuperadas, mas somente duas das nove paráfrases foram atendidas. As
falhas concentram sinônimos e flexões ausentes da sobreposição lexical atual,
como `passe`/`bilhete`, `barreira`/`catraca`, `bike`/`bicicleta`,
`comboios`/`trens` e `queixa`/`reclamação`.

Na classificação, as classes mais frágeis continuam sendo
`analise_tendencia_desempenho` (F1 0,041667),
`consulta_indicadores_kpi` (0,587156) e `consulta_orcamento_custo` (0,676056).
Essas fragilidades não derrubam o F1-macro global abaixo de 0,80, mas permanecem
como risco de qualidade e devem orientar a próxima coleta de exemplos reais.

## Conclusão

O RNF06 está **reprovado** nesta execução. A classificação atinge a meta com a
nova acurácia de 0,839648 e F1-macro de 0,832724, porém a recuperação fica
18,89 pontos percentuais abaixo do mínimo. O ganho do classificador não pode ser
usado para declarar o requisito atendido porque o critério exige simultaneamente
classificação e recuperação acima de 0,80.

Como próximo passo, o recuperador deve tratar equivalências lexicais ou adotar
representação semântica, mantendo esta massa intacta como teste de regressão.
A medição é local e sintética; não substitui homologação com SharePoint real nem
validação externa com solicitações do domínio.
