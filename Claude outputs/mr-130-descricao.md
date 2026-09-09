## O que foi feito

Refeito o frontend em `src/frontend` como interface visual do agente de PLN, sem relação com a landing page de `src/lp`. Os componentes anteriores (`agent-chat`, `chat-input`, `metrics-panel`, `silk-background-animation`) foram removidos e a aplicação foi reconstruída sobre React 19, Vite, Tailwind com tema claro/escuro e primitivos Radix no padrão shadcn/21st.dev.

Interface entregue:

- **Barra lateral esquerda** com o histórico de conversas, busca, agrupamento por data, identificação do usuário e alternância de tema.
- **Chat ao centro** com resposta em markdown, citações `[Fonte N]` clicáveis, selo do resultado do classificador de intenções e estados de carregando e erro.
- **Toggle da camada validadora de intenção** acima do campo de texto, com a explicação dos limiares 0,55 e 0,70 e do comportamento de cada posição.
- **Botão de áudio** com captura real via `MediaRecorder`, medidor de nível, contagem regressiva e corte automático no limite de 60 s, além da revisão da gravação antes do envio.
- **Painel de documentos do RAG à direita**, listando as fontes recuperadas na mesma ordem das citações, com lista de origem, data, score e link, mais a aba "Resposta" com latências, consumo de tokens e as confianças da classificação.

Camada de contrato com o backend em `src/lib/api/`: os tipos espelham os `BaseModel` de `app/gemini/schemas.py` e `app/audio/schemas.py`, e todos os limites exibidos na interface (60 s e 2 MB de áudio, limiares do classificador, teto de 20.000 caracteres da mensagem, orçamento de 10 s do RNF05) ficam em `constants.ts` com o arquivo de origem anotado ao lado de cada valor.

**A integração com o modelo de PLN não faz parte deste MR** e é tratada em task separada. Os quatro pontos de integração estão isolados e documentados em `src/frontend/README.md`, e o `sendMessage` de `state/chat-store.tsx` traz o código exato a ser colocado no lugar do stub. Como as conversões de `sources`, `usage` e latências já estão prontas em `lib/domain.ts`, ligar a API não exige alterar nenhum componente.

O README também registra as lacunas do backend encontradas durante o desenvolvimento, que impedem parte da interface de exibir dado real e precisam de decisão antes da integração: `GeminiSource` não devolve o trecho do documento recuperado, o `MediaRecorder` do Chrome grava um contêiner que a validação de áudio recusa, `GeminiSource` e `AudioAnswerSource` têm formatos diferentes para o mesmo conceito, e apenas a rota de áudio exige `Authorization`. Nenhuma dessas lacunas foi contornada com dado inventado na interface.

Para revisão sem backend no ar, foi incluído um seletor de estados na barra lateral que simula resposta em andamento, erro 503 sem `GEMINI_API_KEY`, resposta sem fontes, fontes com trecho e confiança abaixo do limiar. O seletor e os dados fictícios são descartáveis e o README indica o que remover na integração.

Closes #130

## Como testar

1. Suba a interface:

   ```bash
   cd src/frontend
   npm install
   npm run dev
   ```

2. Acesse `http://localhost:5173` e confira a disposição dos três painéis: conversas à esquerda, chat ao centro e documentos à direita.
3. Selecione conversas diferentes na barra lateral e use a busca; confirme o agrupamento por "Hoje", "Ontem", "Últimos 7 dias" e "Últimos 30 dias".
4. Clique em uma citação `[Fonte N]` dentro da resposta e confirme que o painel da direita abre o documento correspondente, com lista de origem, data, identificador, score e link.
5. Abra a aba "Resposta" no painel da direita e confira as latências, o consumo de tokens e as barras de confiança com a marca do limiar.
6. Acione o toggle "Validação de intenção" e passe o cursor sobre o ícone de informação; confirme a explicação dos dois limiares.
7. Clique no ícone de microfone, permita o acesso e grave alguns segundos; confirme a contagem, o medidor de nível e a revisão com duração e tamanho do arquivo.
8. Percorra o seletor "Estado da interface", no rodapé da barra lateral, e confirme cada estado simulado.
9. Alterne o tema no rodapé da barra lateral e reduza a janela abaixo de 1024 px; confirme que a barra lateral e o painel de documentos viram painéis deslizantes.
10. Rode as verificações:

    ```bash
    npm run lint
    npm run build
    npm run format:check
    ```

**Resultado esperado:** a interface carrega com as conversas de exemplo, a navegação entre conversas e documentos funciona, o toggle e a gravação de áudio respondem, os estados simulados são exibidos corretamente nos dois temas e em tela estreita, e `lint`, `build` e `format:check` terminam sem erro ou aviso.

O envio da mensagem responde com um aviso de que a integração com o pipeline de PLN é feita em task separada — este é o comportamento esperado neste MR.

## Checklist

- [x] Título descritivo com mais de 3 palavras, sem `WIP:` ou `Draft:`, seguindo o formato do commit principal
- [x] Descrição com mais de 40 caracteres
- [x] Issue vinculada por meio de `Closes #N` ou referência equivalente
- [ ] Reviewer designado

---

> A partir deste ponto, as informações servem apenas como lembrete para quem estiver realizando o merge. Apague esta seção antes de finalizar o Merge Request.

- [x] Branch de origem segue o padrão `feature/`, `fix/`, `docs/` ou equivalente
- [ ] Label definida (`FEATURE`, `BUG FIX` ou `DOCUMENTATION`)
- [ ] Milestone definida e igual à sprint da issue de origem
- [ ] Reviewer definido no campo `Reviewers`
- [ ] Revisão contém pelo menos um comentário/nota antes da aprovação
- [ ] Vínculo entre Issue e Merge Request foi conferido
