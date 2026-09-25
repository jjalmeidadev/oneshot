FROM python:3.13-slim-bookworm AS dependencies

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/huggingface \
    PLN_BERT_MODEL=neuralmind/bert-base-portuguese-cased \
    PLN_BERT_REVISION=94d69c95f98f7d5b2a8700c420230ae10def0baa

WORKDIR /build
COPY src/backend/requirements.txt /build/requirements.txt
COPY src/backend/requirements-pln.txt /build/requirements-pln.txt

# PLN is enabled in the production Compose configuration. Install its pinned
# CPU-capable PyTorch/Transformers dependencies explicitly; no GPU is required.
RUN python -m pip install --upgrade pip \
    && python -m pip install -r /build/requirements.txt \
    && python -m pip install --index-url https://download.pytorch.org/whl/cpu \
        --extra-index-url https://pypi.org/simple \
        -r /build/requirements-pln.txt

# Bake the immutable BERTimbau snapshot into the image so runtime startup is
# offline and does not depend on Hugging Face availability.
RUN python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='neuralmind/bert-base-portuguese-cased', revision='94d69c95f98f7d5b2a8700c420230ae10def0baa')"

ENV NLTK_DATA=/opt/nltk_data
RUN python -m nltk.downloader -d /opt/nltk_data punkt punkt_tab stopwords rslp

FROM python:3.13-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/opt/huggingface \
    NLTK_DATA=/opt/nltk_data \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    HF_HUB_DISABLE_TELEMETRY=1 \
    PLN_BERT_MODEL=neuralmind/bert-base-portuguese-cased \
    PLN_BERT_REVISION=94d69c95f98f7d5b2a8700c420230ae10def0baa

WORKDIR /app
RUN groupadd --gid 10001 m7 \
    && useradd --uid 10001 --gid m7 --create-home --shell /usr/sbin/nologin m7 \
    && mkdir -p /var/lib/m7/reports \
    && chown -R m7:m7 /var/lib/m7

COPY --from=dependencies /usr/local /usr/local
COPY --from=dependencies --chown=m7:m7 /opt/huggingface /opt/huggingface
COPY --from=dependencies --chown=m7:m7 /opt/nltk_data /opt/nltk_data
COPY --chown=m7:m7 src/backend/app /app/src/backend/app
COPY --chown=m7:m7 src/backend/docker-entrypoint.py /app/docker-entrypoint.py
COPY --chown=m7:m7 src/database/sql /app/src/database/sql
COPY --chown=m7:m7 src/notebooks/artefatos /app/src/notebooks/artefatos

WORKDIR /app/src/backend
USER 10001:10001

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=180s --retries=3 \
    CMD python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:8000/health', timeout=3).read()" || exit 1

CMD ["python", "/app/docker-entrypoint.py"]

FROM runtime AS test
ENV PLN_WARMUP=0
COPY --chown=m7:m7 src/backend/app/tests /app/src/backend/app/tests
COPY --chown=m7:m7 src/backend/scripts /app/src/backend/scripts
RUN PYTHONPATH=/app/src/backend python -m pytest -q /app/src/backend/app/tests
