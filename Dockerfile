FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PIP_ROOT_USER_ACTION=ignore \
  APP_HOME=/app \
  PORT=8000 \
  PYTHONPATH="${PYTHONPATH}:${APP_HOME}/src"

WORKDIR $APP_HOME

COPY requirements.txt requirements.lock ./

RUN pip install -r requirements.lock

COPY . .

RUN pip install -e .

CMD ./entrypoint.sh
