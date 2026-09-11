<table>
  <tr>
    <td><a href="https://www.metro.sp.gov.br/"><img src="img/logo-metro.png" alt="Companhia do Metropolitano de Sao Paulo - Metro" border="0" width="180"></a></td>
    <td><a href="https://www.inteli.edu.br/"><img src="img/logo-Inteli.png" alt="Inteli - Instituto de Tecnologia e Lideranca" border="0" width="180"></a></td>
  </tr>
</table>

# Nome do Projeto: <nome do projeto>

## Nome do Grupo: <nome do grupo>

## Índice da documentação

Este arquivo reúne os documentos que compõem a documentação do projeto e indica a finalidade de cada um.

### Gestão do Projeto

| Documento | Conteúdo |
|---|---|
| [GestaoProjeto.md](GestaoProjeto.md) | Análise das sprints, matriz de papéis e responsabilidades, contrato de convivência, planejamento das sprints e gestão do processo de desenvolvimento. |

### Processo de Desenvolvimento de Software

| Documento | Conteúdo |
|---|---|
| [GestaoConfiguracao.md](GestaoConfiguracao.md) | Fluxo GitFlow, políticas de branch, commit e merge request, com convenções de nomenclatura e exemplos práticos. |
| [GuiaPadroesDesenvolvimento.md](GuiaPadroesDesenvolvimento.md) | Padrões de desenvolvimento adotados pela equipe. |

### Desenvolvimento do Produto

| Documento | Conteúdo |
|---|---|
| [Projeto.md](Projeto.md) | Entendimento do negócio e especificação de requisitos: problema e SWOT, contexto da indústria, visão e objetivo do produto, personas e jornada, fluxo do negócio, brainstorming de features, canvas do MVP, matriz de risco, business drivers, requisitos funcionais e não funcionais, visão técnica da solução e visão inicial sobre tecnologias e ferramentas. |
| [Frontend integrado e testes](../src/frontend/README.md) | Estrutura, componentes, fluxos, APIs e evidências S3/S5 da bancada web (#131). |
| [Manual-instalacao.md](Manual-instalacao.md) | Instruções de instalação e execução da solução. |

### Código-fonte

| Pasta | Conteúdo |
|---|---|
| [../src/backend/](../src/backend/) | API FastAPI da bancada de teste, com o cliente de geração de resposta e a recuperação de contexto sobre listas simuladas do SharePoint. |
| [../src/frontend/](../src/frontend/) | Bancada de teste em React, Vite e Tailwind, usada para exercitar o caminho de consulta do RAG. Não é a interface do produto, que é o Microsoft Teams. |
| [../src/notebooks/](../src/notebooks/) | Notebook do classificador de intenções, com o benchmark reproduzível do pipeline de PLN. |
| [../src/database/](../src/database/) | Scripts de criação, carga inicial sintética e rollback controlado do banco de dados. |

### Recursos

| Pasta | Conteúdo |
|---|---|
| [img/](img/) | Imagens utilizadas na documentação (logotipos, diagramas). |
| [diagrams/](diagrams/) | Código-fonte dos diagramas em PlantUML, versionado para permitir revisão e regeração. |

<p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://git.inteli.edu.br/graduacao/2026-2a/t17/g05">[nome do projeto]</a> by <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://git.inteli.edu.br/graduacao/2026-2a/t17/g05">INTELI, [aluno 1], [aluno 2], [aluno 3], [aluno 4], [aluno 5], [aluno 6], [aluno 7]</a> is licensed under <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"></a></p>
