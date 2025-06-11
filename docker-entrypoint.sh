#!/bin/bash
set -e

uv run manage.py migrate
uv run manage.py import_orders

exec uv run uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --log-level debug
