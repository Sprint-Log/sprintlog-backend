ARG BUILDER_IMAGE=python:3.13-slim-bookworm

# ---------------------------------------------------------------------------------- #
# ------------------------- Python base -------------------------------------------- #
# ---------------------------------------------------------------------------------- #
FROM ${BUILDER_IMAGE} AS python-base

RUN apt-get update \
  && apt-get upgrade -y \
  && apt-get install -y --no-install-recommends tini \
  && apt-get autoremove -y \
  && apt-get clean -y \
  && rm -rf /root/.cache \
  && rm -rf /var/apt/lists/* \
  && rm -rf /var/cache/apt/* \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && mkdir -p /workspace/app

# Copy uv executables from the published uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# ---------------------------------------------------------------------------------- #
# ------------------------- Python build base -------------------------------------- #
# ---------------------------------------------------------------------------------- #
FROM python-base AS builder

ARG UV_INSTALL_ARGS="--no-dev"
ENV GRPC_PYTHON_BUILD_WITH_CYTHON=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_INSTALL_ARGS="${UV_INSTALL_ARGS}" \
    UV_SYSTEM_PYTHON=1 \
    PATH="/workspace/app/.venv/bin:/usr/local/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Install build dependencies (C toolchain, git, etc.)
RUN apt-get install -y --no-install-recommends git build-essential curl \
  && apt-get autoremove -y \
  && apt-get clean -y \
  && rm -rf /root/.cache \
  && rm -rf /var/apt/lists/* \
  && rm -rf /var/cache/apt/* \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && mkdir -p /cloudsql

WORKDIR /workspace/app

# Copy only Python-related build files (no Node/JS files)
COPY pyproject.toml uv.lock README.md LICENSE Makefile ./

# Create a virtual environment & install Python dependencies
RUN uv venv \
  && uv sync ${UV_INSTALL_ARGS} --frozen --no-install-project --no-editable \
  && uv export ${UV_INSTALL_ARGS} --frozen --no-hashes --output-file=requirements.txt

# Copy source code and perform any additional sync or build steps
COPY src ./src/

RUN uv sync ${UV_INSTALL_ARGS} --frozen --no-install-project --no-editable \
  && uv export ${UV_INSTALL_ARGS} --frozen --no-hashes --output-file=requirements.txt

# Build your Python distribution/wheels
RUN uv build

# ---------------------------------------------------------------------------------- #
# ----------------------------- Runtime Image --------------------------------------- #
# ---------------------------------------------------------------------------------- #
FROM python-base AS runner

ARG ENV_SECRETS="runtime-secrets"
ARG LITESTAR_APP="app.asgi:create_app"

ENV ENV_SECRETS="${ENV_SECRETS}" \
    PATH="/workspace/app/.venv/bin:/usr/local/bin:$PATH" \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_INSTALL_ARGS="${UV_INSTALL_ARGS}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    LITESTAR_APP="${LITESTAR_APP}"

# Create nonroot user and set permissions
RUN addgroup --system --gid 65532 nonroot \
  && adduser --no-create-home --system --uid 65532 nonroot \
  && chown -R nonroot:nonroot /workspace

# Copy the build artifacts (wheels) from builder
COPY --from=builder --chown=65532:65532 /cloudsql /cloudsql
COPY --from=builder --chown=65532:nonroot /workspace/app/dist /tmp/

WORKDIR /workspace/app

# Install the built wheel(s)
RUN uv pip ${UV_INSTALL_ARGS} install --quiet --disable-pip-version-check /tmp/*.whl \
  && rm -rf /tmp/* \
  && chown -R nonroot:nonroot /workspace/app

USER nonroot
STOPSIGNAL SIGINT

EXPOSE 8000
ENTRYPOINT ["tini","--"]
CMD [ "app", "run", "--port", "8000", "--host", "0.0.0.0" ]
VOLUME /workspace/app
