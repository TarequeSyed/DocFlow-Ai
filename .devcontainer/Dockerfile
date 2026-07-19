FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

# Avoid writing .pyc files to disk and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install development utilities, PostgreSQL libraries, and native build dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        postgresql-client \
        curl \
        git \
        jq \
        sudo \
        xdg-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
