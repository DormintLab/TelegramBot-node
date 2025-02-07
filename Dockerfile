FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    shadowsocks-libev \
    build-essential \
    ssh \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip pip install poetry
RUN poetry config virtualenvs.create false
ADD pyproject.toml .
RUN --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --no-root --no-interaction --no-ansi

COPY . .
