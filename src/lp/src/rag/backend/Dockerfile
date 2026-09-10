# Imagem do backend da sala ao vivo, com o modelo RAG dentro.
#
# O contexto de build é `src/lp/src/rag` (e não a pasta do backend), porque o
# modelo é irmão do backend e precisa entrar na imagem:
#     docker build -f backend/Dockerfile -t oneshot-live src/lp/src/rag
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    RAG_MODEL_BACKEND=local

WORKDIR /app

# As dependências entram antes do código: enquanto os requirements não
# mudarem, o cache destas camadas é reaproveitado a cada build.
COPY backend/requirements.txt backend/requirements.txt
COPY model/requirements.txt model/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/app ./backend/app
COPY model ./model
COPY documentsRAG ./documentsRAG

WORKDIR /app/backend

EXPOSE 8000

# `--workers 1` não é economia: a sala está na memória do processo, e um
# segundo worker criaria uma segunda sala. Ver "Escala" no README.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1"]
