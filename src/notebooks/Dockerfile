FROM python:3.13-slim-bookworm AS notebook-dependencies

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/huggingface

WORKDIR /build
COPY src/notebooks/requirements.txt /build/requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install --index-url https://download.pytorch.org/whl/cpu \
        --extra-index-url https://pypi.org/simple \
        -r /build/requirements.txt

RUN python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='neuralmind/bert-base-portuguese-cased', revision='94d69c95f98f7d5b2a8700c420230ae10def0baa')"
RUN python -c "from pathlib import Path; p=Path('/opt/huggingface/hub/models--neuralmind--bert-base-portuguese-cased/refs'); p.mkdir(parents=True, exist_ok=True); (p/'main').write_text('94d69c95f98f7d5b2a8700c420230ae10def0baa', encoding='ascii')"

ENV NLTK_DATA=/opt/nltk_data
RUN python -m nltk.downloader -d /opt/nltk_data punkt punkt_tab stopwords rslp

FROM python:3.13-slim-bookworm AS notebook

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/opt/huggingface \
    NLTK_DATA=/opt/nltk_data \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    HF_HUB_DISABLE_TELEMETRY=1

RUN groupadd --gid 10001 notebook \
    && useradd --uid 10001 --gid notebook --create-home --shell /usr/sbin/nologin notebook \
    && mkdir -p /workspace /etc/jupyter \
    && chown -R notebook:notebook /workspace

COPY --from=notebook-dependencies /usr/local /usr/local
COPY --from=notebook-dependencies --chown=notebook:notebook /opt/huggingface /opt/huggingface
COPY --from=notebook-dependencies --chown=notebook:notebook /opt/nltk_data /opt/nltk_data
COPY --chown=notebook:notebook src/notebooks/ /workspace/
COPY --chown=notebook:notebook src/backend/app/nlp/ /workspace/src/backend/app/nlp/
COPY src/notebooks/jupyter_server_config.py /etc/jupyter/jupyter_server_config.py

WORKDIR /workspace
USER 10001:10001
EXPOSE 8888
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('127.0.0.1', 8888), timeout=3).close()" || exit 1

CMD ["jupyter", "notebook", "--config=/etc/jupyter/jupyter_server_config.py", "--ip=0.0.0.0", "--port=8888", "--no-browser"]
