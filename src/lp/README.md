# Landing Page — Agente de IA para o Portfólio de Projetos do Metrô

Projeto React + Vite + TypeScript da Landing Page de apresentação do produto, desenvolvido no contexto da parceria acadêmica entre o Inteli e o Metrô de São Paulo.

> Setup inicial: apenas a estrutura de pastas e as dependências base foram configuradas. O desenvolvimento da interface ainda não foi iniciado.

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

## Scripts

- `npm run dev` — inicia o servidor de desenvolvimento
- `npm run build` — gera o build de produção (`dist/`)
- `npm run preview` — pré-visualiza o build de produção
- `npm run lint` — executa o linter (Oxlint)
