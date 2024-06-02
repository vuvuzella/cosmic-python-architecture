# syntax=docker/dockerfile:1

FROM python:3.11-slim-buster

WORKDIR /app

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install --user pipx
RUN python3 -m pipx ensurepath

ENV PATH="${PATH}:/root/.local/bin"

RUN pipx install poetry

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

COPY poetry.lock .
COPY pyproject.toml .

COPY flask_api/ ./flask_api
COPY domain/ ./domain
COPY infrastructure/ ./infrastructure
COPY services/ ./services
COPY *.py ./

RUN poetry install --no-root

EXPOSE 5000

CMD ["poetry", "run", "gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "flask_api.app:app" ]
