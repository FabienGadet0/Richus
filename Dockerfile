FROM python:3.12-slim

RUN mkdir -p /opt/dagster/dagster_home /opt/dagster/app

ENV DAGSTER_HOME=/opt/dagster/dagster_home/

WORKDIR /opt/dagster/app

# COPY pyproject.toml poetry.lock* ./

COPY . .
COPY dagster.yaml /opt/dagster/dagster_home/
COPY workspace.yaml /opt/dagster/app

RUN pip install poetry && \
    # poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi


# RUN rm -f .env

ENTRYPOINT ["poetry", "run", "dagster-webserver", "-h", "0.0.0.0", "-p", "3000"]
