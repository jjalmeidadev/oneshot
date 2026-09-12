<table>
  <tr>
    <td><a href="https://www.metro.sp.gov.br/"><img src="img/logo-metro.png" alt="Companhia do Metropolitano de São Paulo - Metrô" border="0" width="180"></a></td>
    <td><a href="https://www.inteli.edu.br/"><img src="img/logo-Inteli.png" alt="Inteli - Instituto de Tecnologia e Liderança" border="0" width="180"></a></td>
  </tr>
</table>

# Agente de IA para o Portfólio de Projetos do Metrô

## Grupo Oneshot

# Manual de Instalação

# Sumário

- [1. Introdução](#1-introdução)
- [2. Pré-requisitos](#2-pré-requisitos)
- [3. Instalação](#3-instalação)
- [4. Configuração](#4-configuração)
- [5. Execução](#5-execução)
- [6. Verificação da instalação](#6-verificação-da-instalação)
- [7. Teste manual da interface](#7-teste-manual-da-interface)
- [8. Banco de dados opcional](#8-banco-de-dados-opcional)
- [9. Solução de problemas](#9-solução-de-problemas)
- [Referências](#referências)

# 1. Introdução

Este manual permite instalar e executar localmente a bancada web e a API do Agente de IA. O fluxo disponível recebe texto ou áudio, classifica a intenção opcionalmente, recupera contexto em dados sintéticos e produz uma resposta. A instalação é destinada a desenvolvimento, revisão e demonstração; não configura Microsoft Teams, Entra ID ou SharePoint corporativo.

O PostgreSQL é opcional porque os scripts do banco ainda não estão ligados à API. Sem banco, toda a bancada continua executável: o RAG usa exports JSON versionados e as conversas existem somente na memória do navegador.

# 2. Pré-requisitos

- Git;
- Python 3.12 ou 3.13; Python 3.14 não é suportado pelas dependências atuais de PLN;
- Node.js 24 e npm;
- acesso à internet na primeira instalação e na primeira carga do encoder;
- para o fluxo real de resposta, chave do Gemini;
- para o fluxo real de voz, recurso e chave do Azure AI Speech;
- opcionalmente, PostgreSQL 14+ e `psql` para executar o modelo físico.

Os comandos abaixo usam PowerShell e partem da raiz do repositório.

# 3. Instalação

Crie um ambiente Python na raiz e instale o back-end e o núcleo de PLN:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install --upgrade pip
.venv/Scripts/python.exe -m pip install -r src/backend/requirements.txt -r src/backend/requirements-pln.txt
```

Instale as dependências exatas do front-end a partir do arquivo de lock:

```powershell
Set-Location src/frontend
npm ci
Set-Location ../..
```

Não use `npm install` para uma reprodução limpa, pois ele pode alterar o lock. O encoder ONNX é obtido do repositório de modelo documentado na Seção 8.11 de `Projeto.md` quando o classificador é carregado pela primeira vez.

# 4. Configuração

Crie o arquivo local do back-end a partir do exemplo versionado:

```powershell
Copy-Item src/backend/.env.example src/backend/.env
```

Edite somente `src/backend/.env` e não versione credenciais. Para exercitar todos os caminhos, preencha:

```dotenv
GEMINI_API_KEY=<chave-do-google-ai-studio>
GEMINI_MODEL=gemini-3.7-flash
AZURE_SPEECH_RESOURCE=<nome-do-recurso>
AZURE_SPEECH_KEY=<chave-do-azure-speech>
AUDIO_SIMULATED_IDENTITIES=token-local=usuario-local
PLN_WARMUP=1
```

Use `AZURE_SPEECH_ENDPOINT` quando o portal fornecer um endpoint regional explícito. Os timeouts, retentativas, limite de fontes e diretório alternativo de dados simulados possuem valores documentados no próprio `.env.example`.

O valor `token-local` do exemplo é informado na barra lateral da interface. Ele simula a identidade somente no endpoint de áudio; não é chave do Azure ou Gemini e não implementa autenticação Entra ID. Com `PLN_WARMUP=0`, a API inicia mais rápido, mas a primeira solicitação com classificação paga o custo de carga do modelo.

# 5. Execução

Abra dois terminais na raiz do repositório.

No primeiro, inicie a API:

```powershell
.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir src/backend --host 127.0.0.1 --port 8000
```

No segundo, inicie a interface:

```powershell
Set-Location src/frontend
npm run dev
```

Abra `http://localhost:5173`. O servidor Vite encaminha `/api` e `/health` para `http://127.0.0.1:8000`. Se o back-end usar outro endereço, defina `API_PROXY_TARGET` antes de `npm run dev`.

`npm run preview` serve o build estático, mas não encaminha sozinho as rotas da API. Em uma publicação, o servidor ou gateway deve entregar o front-end e encaminhar `/api` e `/health` ao FastAPI na mesma origem.

# 6. Verificação da instalação

Com a API ativa, verifique a saúde e a documentação automática:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

O resultado esperado é `status: ok`. Acesse também:

- `http://127.0.0.1:8000/docs` para Swagger UI;
- `http://127.0.0.1:8000/redoc` para ReDoc;
- `http://127.0.0.1:8000/openapi.json` para o contrato OpenAPI.

Execute as verificações determinísticas:

```powershell
.venv/Scripts/python.exe -m pytest src/backend/app/tests
Set-Location src/frontend
npm run lint
npm run format:check
npm run test:coverage
npm run build
npx playwright install chromium
npm run test:e2e
```

O Playwright inicia servidores exclusivos nas portas 5174 e 8001 e usa provedores simulados. Relatórios locais são gerados em `src/frontend/coverage/` e `src/frontend/playwright-report/`. A execução padrão não consome franquia do Azure ou Gemini e não comprova a disponibilidade desses serviços reais.

# 7. Teste manual da interface

1. Abra `http://localhost:5173` e confirme que o estado vazio e as sugestões aparecem.
2. Envie uma pergunta por texto. O esperado é aparecer uma mensagem da pessoa usuária, o indicador de processamento e depois a resposta; quando houver contexto recuperado, as fontes e o trecho devem aparecer no painel de documentos.
3. Ative **Validação de intenção** e envie uma pergunta do portfólio. O esperado é a classificação aparecer nos detalhes. Envie depois uma pergunta claramente fora do domínio e confirme a resposta controlada.
4. Crie uma nova conversa, retorne à anterior e confirme que cada histórico conserva seu próprio contexto durante a sessão. Teste também busca e exclusão.
5. Informe `token-local` no campo de token, acione o microfone, conceda a permissão, grave uma frase, conclua e ouça a prévia. Envie o áudio; o esperado é receber a transcrição e a resposta na mesma conversa.
6. Inicie uma solicitação e use **Interromper resposta**. O indicador deve parar e um retorno tardio não deve ser inserido na conversa.
7. Reduza a janela abaixo de 1024 px. Conversas e documentos devem abrir em diálogos; `Escape` deve fechá-los. Alterne também os temas claro e escuro.
8. Recarregue a página e confirme a limitação conhecida: conversas e token são apagados, pois ainda não existe persistência no back-end.

Se as chaves externas não estiverem disponíveis, os passos de texto que exigem geração e o áudio real devem apresentar indisponibilidade controlada. Use `npm run test:e2e` para validar o mesmo fluxo com fronteiras determinísticas.

# 8. Banco de dados opcional

Defina uma URL de um banco de desenvolvimento e aplique os scripts na ordem:

```powershell
$env:DATABASE_URL = "postgresql://usuario:senha@localhost:5432/metro_poc"
psql "$env:DATABASE_URL" -v ON_ERROR_STOP=1 -f src/database/sql/01_create_database.sql
psql "$env:DATABASE_URL" -v ON_ERROR_STOP=1 -f src/database/sql/02_initial_data.sql
```

O modelo e a carga sintética podem ser inspecionados independentemente, mas não alteram as respostas da API atual. `03_rollback_data.sql` remove o baseline e só deve ser aplicado em banco descartável ou após um backup.

# 9. Solução de problemas

| Sintoma | Verificação e correção |
| --- | --- |
| `python` aponta para 3.14 | Instale Python 3.12 ou 3.13, recrie `.venv` e reinstale as dependências. |
| Erro ao carregar o classificador | Confirme `requirements-pln.txt`, acesso ao cache/repositório do encoder e compatibilidade do artefato com scikit-learn 1.6.1. |
| API não fica pronta com `PLN_WARMUP=1` | Aguarde a primeira obtenção do encoder ou use temporariamente `PLN_WARMUP=0` para isolar a inicialização. |
| Chat devolve indisponibilidade | Confira `GEMINI_API_KEY`, acesso de rede, modelo, timeout e limite do provedor. |
| Áudio devolve 401 | Envie o token mapeado em `AUDIO_SIMULATED_IDENTITIES`; não informe a chave do Azure na interface. |
| Áudio devolve 400, 413 ou 422 | Grave novamente e confirme fala audível, WAV aceito, duração de até 60 s e tamanho de até 2 MB. |
| Interface abre, mas `/api` falha | Confirme o FastAPI na porta 8000 e o destino de `API_PROXY_TARGET`. Em preview/publicação, configure o proxy de mesma origem. |
| Microfone não é oferecido | Use `localhost`, confirme a permissão do navegador e feche outra aplicação que esteja usando o dispositivo. |
| Teste E2E não encontra Python | Defina `E2E_PYTHON` com o caminho absoluto de `.venv/Scripts/python.exe`. |
| `psql` falha no primeiro script | Confirme PostgreSQL 14+, credenciais, permissão para `pgcrypto` e execute com `ON_ERROR_STOP=1`. |

# Referências

- [Documentação principal](Projeto.md), especialmente as Seções 4, 6 e 8;
- [Referência do back-end](../src/backend/README.md);
- [Referência do front-end](../src/frontend/README.md);
- [Matriz e evidências de testes](../src/frontend/TESTES.md);
- [Documentação do banco](../src/database/docs/README.md).

<p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://git.inteli.edu.br/graduacao/2026-2a/t17/g05">Agente de IA para o Portfólio de Projetos do Metrô</a> by <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://git.inteli.edu.br/graduacao/2026-2a/t17/g05">INTELI e Grupo Oneshot</a> is licensed under <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"></a></p>
