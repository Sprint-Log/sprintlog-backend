ARG PYTHON_BUILDER_IMAGE=3.13-slim-bookworm

# ---------------------------------------------------------------------------------- #
# ------------------------- Python base -------------------------------------------- #
# ---------------------------------------------------------------------------------- #
FROM python:${PYTHON_BUILDER_IMAGE} AS python-base

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends git tini \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /root/.cache \
    && rm -rf /var/apt/lists/* \
    && rm -rf /var/cache/apt/* \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && mkdir -p /workspace/app \
    && pip install --quiet -U pip wheel setuptools virtualenv

# Install uv from an external image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# ---------------------------------------------------------------------------------- #
# ------------------------- Python Dev Image --------------------------------------- #
# ---------------------------------------------------------------------------------- #
FROM python-base AS dev-image

ARG UV_INSTALL_ARGS="--all-groups"
ARG ENV_SECRETS="runtime-secrets"
ARG LITESTAR_APP="app.asgi:create_app"
ARG SAQ_USE_SERVER_LIFESPAN="false"

ENV PATH="/workspace/app/.venv/bin:/usr/local/bin:$PATH" \
    VIRTUAL_ENV="/workspace/app/.venv" \
    ENV_SECRETS="${ENV_SECRETS}" \
    SAQ_USE_SERVER_LIFESPAN="${SAQ_USE_SERVER_LIFESPAN}" \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_INSTALL_ARGS="${UV_INSTALL_ARGS}" \
    UV_SYSTEM_PYTHON=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    LITESTAR_APP="${LITESTAR_APP}"

RUN apt-get install -y --no-install-recommends git build-essential curl \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /root/.cache \
    && rm -rf /var/apt/lists/* \
    && rm -rf /var/cache/apt/* \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false

WORKDIR /workspace/app

COPY pyproject.toml uv.lock README.md LICENSE Makefile  ./

RUN uv sync ${UV_INSTALL_ARGS} --no-install-project

COPY src/ src/

RUN uv sync ${UV_INSTALL_ARGS}

STOPSIGNAL SIGINT
EXPOSE 8000
ENTRYPOINT ["tini","--"]
CMD [ "litestar","run","--host","0.0.0.0"]
VOLUME /workspace/app
