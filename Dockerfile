ARG APP_ROOT="/src"
ARG PYTHON_VERSION="3.12"
ARG USER="appuser"


# Stage 1: Builder Image
FROM python:${PYTHON_VERSION}-slim AS builder
LABEL author="qte77"
LABEL builder=true
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
COPY pyproject.toml uv.lock /
RUN set -xe \
    && pip install --no-cache-dir uv \
    && uv sync --frozen


# Stage 2: Runtime Image
FROM python:${PYTHON_VERSION}-slim AS runtime
LABEL author="qte77"
LABEL runtime=true

ARG APP_ROOT
ARG USER
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=${APP_ROOT} \
    PATH="${APP_ROOT}:${PATH}"
#    WANDB_KEY=${WANDB_KEY} \
#    WANDB_DISABLE_CODE=true

USER ${USER}
WORKDIR ${APP_ROOT}
COPY --from=builder /.venv .venv
COPY --chown=${USER}:${USER} ${APP_ROOT} .

CMD [ \
    "uv", "run", \
    "--locked", "--no-sync", \
    "python", "-m", "." \
]
