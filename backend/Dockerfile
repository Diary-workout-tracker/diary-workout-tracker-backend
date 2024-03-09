FROM python:3.11

ARG DJANGO_ENV

ENV DJANGO_ENV=${DJANGO_ENV} \
    # Python configuration:
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    # pip configuration:
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Poetry's configuration:
    POETRY_VERSION=1.7.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local'

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app
COPY ./pyproject.toml /app/pyproject.toml
RUN poetry install $(test "$DJANGO_ENV" == production && echo "--only=main") --no-interaction --no-ansi
COPY ./backend .
