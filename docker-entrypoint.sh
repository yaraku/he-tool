#!/bin/sh
set -e

echo "Running database migrations..."
flask db upgrade

echo "Starting gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 -w "${WORKERS:-1}" human_evaluation_tool:app
