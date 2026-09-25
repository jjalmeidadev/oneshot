# Checklist de ambiente

Rodar **inteiro antes de cada sessão**, e não uma vez por dia.

Uma sessão conduzida com o *backend* fora do ar, sem fonte citada ou com a
configuração diferente das outras produz ocorrências que são defeito de bancada, e
não de usabilidade. Elas entrariam na consolidação como problema do produto. Se um
item obrigatório falhar e não for resolvido antes do horário, a sessão é
reagendada e registrada como `bloqueada` em
[`dados/participantes.csv`](dados/participantes.csv), com o motivo.

## Versão congelada

As sessões comparam participantes entre si; por isso todas rodam contra a mesma
versão e a mesma configuração.

- [ ] Commit anotado em `dados/participantes.csv`: `____________`
- [ ] Mesmo commit das sessões anteriores desta rodada
- [ ] Árvore de trabalho limpa: `git status --porcelain` vazio
- [ ] Massa sintética inalterada desde a primeira sessão
- [ ] Provedor do LLM igual ao das outras sessões: `____________`

O *Free Tier* do Gemini limita a 20 requisições por dia e por modelo, menos do que
cinco sessões consomem. As sessões usam o mesmo provedor pago dos testes de RNF,
com o mesmo modelo da bancada.

## *Backend*

A partir de `src/backend`:

```bash
LLM_PROVIDER=openrouter .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- [ ] `curl -s http://127.0.0.1:8000/health` devolve `{"status":"ok"}`
- [ ] Log de inicialização sem erro de PLN
- [ ] Consulta de controle responde **com fonte citada**:

```bash
curl -s -X POST http://127.0.0.1:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Qual e o periodo da operacao assistida na Linha 1-Azul?"}'
```

Esperado: operação assistida de 24/08/2026 a 28/08/2026, com o comunicado entre as
fontes.

## *Frontend*

A partir de `src/frontend`, com `npm ci` já executado:

```bash
npm run dev
```

- [ ] `http://localhost:5173` abre sem erro no console do navegador
- [ ] Uma mensagem de teste é enviada e respondida, com as fontes visíveis
- [ ] **Token de sessão informado** na interface: sem ele, a proatividade e a voz
      recusam a requisição
- [ ] **Modo proatividade ligado** antes de o participante sentar, igual para
      todos: o cenário 6 observa se a sugestão é percebida sem aviso
- [ ] Entrada por voz testada com uma frase curta — se não funcionar, marcar
      ☐ indisponível e registrar o cenário 7 como `nao_testado`
- [ ] **Conversa nova** aberta, sem as mensagens de teste acima

## Sala

- [ ] Navegador em janela limpa, sem outras abas, zoom em 100%
- [ ] Notificações do sistema silenciadas
- [ ] Microfone e alto-falante testados
- [ ] Gravação de tela testada, se o participante autorizar
- [ ] Cronômetro à mão
- [ ] Termo de consentimento pronto para assinatura
- [ ] Planilha do grupo aberta na linha do participante certo
- [ ] Link do formulário SUS pronto para enviar ao final

## Privacidade

- [ ] Nenhum dado real de terceiros aberto na tela compartilhada
- [ ] Nenhum segredo visível: `.env`, chaves, tokens ou string de conexão
- [ ] Terminal fechado ou sem credencial visível na rolagem
- [ ] Nome do participante fora de qualquer arquivo versionado

## Registro da sessão

| Campo | Valor |
| --- | --- |
| Data e hora | |
| Participante | P___ |
| Moderador | |
| Observador | |
| Commit testado | |
| Provedor e modelo do LLM | |
| Voz disponível | ☐ sim ☐ não |
| Todos os itens obrigatórios passaram | ☐ sim ☐ não |
| Se não, o que falhou e o que foi feito | |
