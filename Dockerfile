# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

WORKDIR /app

RUN python3 -m pip install --user pipx
RUN python3 -m pipx ensurepath

ENV PATH="${PATH}:/root/.local/bin"

RUN pipx install poetry

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

COPY poetry.lock .
COPY pyproject.toml .

RUN poetry install --no-root

COPY flask_api/ ./flask_api

COPY models/ ./models
COPY *.py ./

EXPOSE 5000

CMD ["poetry", "run", "flask", "--app", "flask_api.app", "run", "--host=0.0.0.0", "--port=5000"]
