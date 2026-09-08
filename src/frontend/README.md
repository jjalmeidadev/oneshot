# Frontend

Interface web do agente de IA para consulta de arquivos sobre projetos da empresa Metro de Sao Paulo.

## Stack

- React
- TypeScript
- Vite
- Tailwind CSS
- ESLint
- Prettier

## Comandos

```bash
npm install
npm run dev
npm run build
npm run lint
npm run format
```

## API do Gemini

O frontend usa `POST /api/chat`. No desenvolvimento, o Vite encaminha essa rota
para `http://127.0.0.1:8000`, mantendo a chave do Gemini somente no backend.

Inicie primeiro o backend conforme `../backend/README.md` e depois execute
`npm run dev`. Cada resposta registra latencia, taxa de sucesso e consumo de
tokens no painel de metricas.
