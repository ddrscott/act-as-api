#!/bin/sh -ev
set -o pipefail

exec uvicorn --reload --port $PORT --host 0.0.0.0 --workers 4 act_as_api.app:app
