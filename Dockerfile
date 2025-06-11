FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings \
    PATH="/root/.local/bin/:$PATH"

RUN adduser --disabled-password --gecos "" appuser
WORKDIR /app
RUN chown appuser:appuser /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=appuser:appuser pyproject.toml ./
COPY --chown=appuser:appuser . .

RUN touch /app/app.log && chown appuser:appuser /app/app.log
COPY --chown=appuser:appuser ./docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

USER appuser

RUN uv sync --no-group dev --group prod

RUN uv run manage.py collectstatic --noinput

EXPOSE 8000
ENTRYPOINT ["/app/docker-entrypoint.sh"]
