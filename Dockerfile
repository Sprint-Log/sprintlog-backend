
FROM python:3.11

# Configure Poetry
ENV POETRY_VERSION=1.5.1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

# Install poetry separated from system interpreter
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Add `poetry` to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app/workspace

# Install dependencies
COPY poetry.lock pyproject.toml ./

# Run your app
COPY . /app/workspace/
RUN poetry install
RUN chown -R 65532:65532 /workspace
EXPOSE 8000
ENTRYPOINT ["poetry", "run"]
VOLUME /app/workspace
