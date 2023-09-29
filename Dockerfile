FROM python:3.11-alpine

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PIP_ROOT_USER_ACTION=ignore \
  APP_HOME=/app \
  PORT=8000 \
  PYTHONPATH="${PYTHONPATH}:${APP_HOME}/src"

WORKDIR $APP_HOME

COPY requirements.lock ./

RUN pip install -r requirements.lock

COPY . .

RUN pip install -e .

CMD ./entrypoint.sh
