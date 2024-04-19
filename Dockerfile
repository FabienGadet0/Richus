FROM python:3.12-slim

RUN mkdir -p /opt/dagster/dagster_home /opt/dagster/app

ENV DAGSTER_HOME=/app/src/dag

WORKDIR /app

# COPY pyproject.toml poetry.lock* ./

COPY . .

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi


# RUN rm -f .env

ENTRYPOINT  ["poetry","run","dagster","dev", "-f" ,"/app/src/dag/dagster.py"]
