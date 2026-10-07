# CT-RNF10-P — reprodução do README em ambiente limpo

Data: 07/10/2026 (America/Sao_Paulo). Base: commit `84df352` da `develop`.

## Ambiente

Ambiente Linux novo, sem `.env`, sem banco e sem o `.venv` da equipe:
Python 3.13.15 em ambiente virtual vazio, criado só para esta execução.
`PYTHON_DOTENV_DISABLED=1` e a fixture `ambiente_isolado` neutralizaram
qualquer configuração local.

## Passos seguidos, na ordem do `src/backend/README.md`

| Passo do README | Comando executado | Resultado |
|---|---|---|
| Criar ambiente e instalar dependências | `python -m venv` + `pip install -r requirements.txt` | Instalação concluída, sem ajuste manual |
| Dados do NLTK para o pré-processamento | `nltk.download('stopwords')` e `nltk.download('punkt_tab')` | Corpora instalados no ambiente |
| Executar os testes | `python -m pytest app/tests` (em dois lotes, pelo limite de tempo do terminal) | Lote 1: 439 aprovados, 14 ignorados. Lote 2: 278 aprovados, 18 ignorados, 1 xfail, 6 falhas |
| Dependências do classificador (`requirements-pln.txt`) | `pip install torch==2.13.0` pelo índice CPU do PyTorch | **Não executado:** a rede deste ambiente bloqueou `download.pytorch.org` |

## As 6 falhas do lote 2

| Teste | Causa | Situação |
|---|---|---|
| `test_pipeline_api.py::test_audio_transcription_is_classified_by_real_classifier` | Classificador real exige `torch` (`requirements-pln.txt`), não instalado aqui | Coberto pela pipeline: job `backend-api` da [pipeline #89702](https://git.inteli.edu.br/graduacao/2026-2a/t17/g05/-/pipelines/89702), no mesmo commit, instala `requirements-pln.txt` e terminou com 539 aprovados e 0 falhas |
| `test_traceability.py::test_chat_real_classifier_contract_and_minimal_persistence` | Idem (`ModuleNotFoundError: torch` → HTTP 503 controlado) | Idem |
| `test_traceability.py::test_audio_real_classifier_contract_and_minimal_persistence` | Idem | Idem |
| `test_rnf07_rnf09_s5_31.py::test_ct_rnf07_p`, `test_ct_rnf07_n`, `test_ct_rnf08_p` | Falhas reais já registradas na S5-31 (RNF07 6/20; RNF08-P pelo critério Copilot) | Fora do escopo do RNF10; tratadas na S5-31 e na S5-43 |

Nenhuma falha decorre de instrução ausente ou errada no README. A única
dependência que exigiu passo adicional (NLTK) está documentada no próprio
README, na seção de testes de PLN.

## Arquivos

- `pytest-lote-1.txt` / `pytest-lote-1.xml`
- `pytest-lote-2.txt` / `pytest-lote-2.xml`

Caminhos absolutos do ambiente foram substituídos por `<sessao>`.
