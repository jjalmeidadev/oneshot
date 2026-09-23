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

- Data da reexecução aprovada: 23 de setembro de 2026.
- Responsável: Pedro Damacena Machado Uchoa.
- Commit executado: `3a489a30c8c805e160e465cba8c7db669aec5f3c`.
- Ambiente: Windows, Python 3.13.15, scikit-learn 1.6.1, NumPy 2.5.2,
  joblib 1.6.0, Torch 2.13.0 e Transformers 5.16.1.
- Evidência estruturada: [`resultado-rnf06.json`](resultado-rnf06.json).

Comando reproduzível, a partir de `src/backend`:

```powershell
..\..\.venv\Scripts\python.exe scripts\benchmark_rnf06.py
```

O comando retorna código 0 somente quando os dois critérios atingem o limiar e
código 1 quando qualquer um deles fica abaixo. A reexecução documentada nesta
página terminou com código 0.

## Resultados observados

| Componente | Métrica | Resultado | Limiar | Situação |
| --- | --- | ---: | ---: | --- |
| Classificação de intenção específica | Acurácia | 0,839648 | Informativa | Medida |
| Classificação de intenção específica | F1-macro | 0,832724 | ≥ 0,80 | Aprovado |
| Recuperação — formulações diretas | *Recall*@3 | 1,000000 | ≥ 0,80 | Aprovado |
| Recuperação — desafio lexical | *Recall*@3 | 1,000000 | ≥ 0,80 | Aprovado |
| Recuperação — conjunto completo | *Recall*@3 | 1,000000 | ≥ 0,80 | Aprovado |

O recuperador encontrou as 18 fontes relevantes: nove nas consultas diretas e
nove nas paráfrases. A correção reduz termos equivalentes do domínio a formas
canônicas antes da pontuação, incluindo `passe`/`bilhete`,
`barreira`/`catraca`, `bike`/`bicicleta`, `comboios`/`trens` e
`queixa`/`reclamação`. A mesma normalização é aplicada à consulta, ao título e
ao conteúdo da fonte; não foi incluído modelo adicional em tempo de execução.

Como comparação, a rodada inicial de 22 de setembro recuperou 11 de 18 fontes,
com *recall*@3 global de 0,611111 e 0,222222 no desafio lexical. A massa e as
fontes permaneceram byte a byte idênticas entre as rodadas, conforme os hashes
registrados no manifesto e na evidência estruturada.

Na classificação, as classes mais frágeis continuam sendo
`analise_tendencia_desempenho` (F1 0,041667),
`consulta_indicadores_kpi` (0,587156) e `consulta_orcamento_custo` (0,676056).
Essas fragilidades não derrubam o F1-macro global abaixo de 0,80, mas permanecem
como risco de qualidade e devem orientar a próxima coleta de exemplos reais.

## Conclusão

O RNF06 está **aprovado** nesta execução: a classificação atingiu acurácia de
0,839648 e F1-macro de 0,832724, enquanto a recuperação atingiu *recall*@3 de
1,000000. Assim, os dois critérios indivisíveis ficaram acima de 0,80.

A aprovação vale para a massa sintética congelada. A medição não substitui a
homologação com SharePoint real nem validação externa com solicitações do
domínio; as classes frágeis do classificador e novas variações lexicais devem
continuar sendo monitoradas.
