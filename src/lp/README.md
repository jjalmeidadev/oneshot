# Landing Page — Agente de IA para o Portfólio de Projetos do Metrô

Projeto React + Vite + TypeScript da Landing Page de apresentação do produto, desenvolvido no contexto da parceria acadêmica entre o Inteli e o Metrô de São Paulo.


## Stack

- [React](https://react.dev/) 19
- [Vite](https://vite.dev/) 8
- TypeScript
- [Oxlint](https://oxc.rs/) para lint

## Estrutura de pastas

```text
src/
├─ assets/        imagens, ícones e demais arquivos estáticos
├─ components/    componentes de UI reutilizáveis
├─ sections/      seções da landing page (hero, sobre, funcionalidades, contato, etc.)
├─ hooks/         hooks customizados
├─ types/         tipos e interfaces TypeScript compartilhados
├─ utils/         funções utilitárias
├─ App.tsx        componente raiz
├─ main.tsx       ponto de entrada da aplicação
└─ index.css      estilos globais
```

## Como rodar

```bash
npm install
npm run dev
```

## Presença ao vivo

A última seção da página mostra quem está conversando com o agente naquele
momento, no espírito de acompanhar um participante no Miro. Ela é alimentada
pelo backend em [`src/rag/backend`](src/rag/backend/README.md).

```bash
# src/lp/.env.local
VITE_LIVE_BACKEND_URL=http://localhost:8000
```

Com essa variável, cada aba que abre a página entra na sala e aparece no painel
dos outros dispositivos; o painel só aparece quando há **outra** pessoa além de
você. Sem ela — o padrão —, a página funciona normalmente e o painel roda no
modo simulado de `?ao-vivo=N` (`?ao-vivo=3` para três participantes de mentira).

Para testar com o celular na rede local, use o IP da máquina em vez de
`localhost` e rode `npm run dev -- --host`. O passo a passo completo, incluindo
firewall do Windows, está no
[README do backend](src/rag/backend/README.md#testar-com-vários-dispositivos).

Três arquivos cuidam disso: `src/lib/liveBackend.ts` (o endereço),
`src/lib/useLivePresence.ts` (observa a sala) e `src/lib/useLiveSession.ts`
(coloca esta aba nela).


## Scripts

- `npm run dev` — inicia o servidor de desenvolvimento
- `npm run build` — gera o build de produção (`dist/`)
- `npm run preview` — pré-visualiza o build de produção
- `npm run lint` — executa o linter (Oxlint)
