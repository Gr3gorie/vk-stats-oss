# ------------------------------------------------------------------------------
# Base image
FROM python:3.10.2-slim AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
		POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
		WORKDIR_PATH="/backend" \
		VENV_PATH="/backend/.venv" \
		POETRY_HOME="/opt/poetry"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# ------------------------------------------------------------------------------
# Builder image
FROM python-base AS python-builder

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential \
        gcc \
        git

# Install Poetry. Respects $POETRY_VERSION & $POETRY_HOME.
RUN pip install poetry==$POETRY_VERSION

# Set working directory.
WORKDIR $WORKDIR_PATH

# Copy Poetry and Python manifests and install only main dependencies.
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --only main

# ------------------------------------------------------------------------------
# Production image
FROM python-base AS python-prod

RUN apt-get update && \
    apt-get install -y \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6

# Set working directory.
WORKDIR $WORKDIR_PATH

# Copy dependencies from builder image.
COPY --from=python-builder $VENV_PATH $VENV_PATH

# Copy source code.
COPY src src

# Run.
ENV PYTHONPATH="$WORKDIR_PATH/src:$PYTHONPATH"
CMD ["python", "src/main.py"]
