#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "Project root: $ROOT_DIR"

# Create .env from example if missing
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
  else
    echo "Warning: .env.example not found; please create .env manually" >&2
  fi
else
  echo ".env already exists"
fi

# Create setup/.env from example if missing
if [ ! -f setup/.env ]; then
  if [ -f setup/.env.example ]; then
    cp setup/.env.example setup/.env
    echo "Created setup/.env from setup/.env.example"
  else
    echo "Warning: setup/.env.example not found; please create setup/.env manually" >&2
  fi
else
  echo "setup/.env already exists"
fi

# Build and start services
echo "Building Airflow image and dependencies..."
docker compose -f docker-compose.airflow.yaml build --pull --no-cache airflow

echo "Starting services (detached)..."
docker compose -f docker-compose.airflow.yaml up -d

# Wait for Airflow health endpoint
echo "Waiting for Airflow webserver to become healthy at http://localhost:8080/health ..."
for i in $(seq 1 60); do
  if curl -sSf http://localhost:8080/health > /dev/null 2>&1; then
    echo "Airflow webserver is healthy"
    break
  fi
  sleep 2
done

if ! curl -sSf http://localhost:8080/health > /dev/null 2>&1; then
  echo "Warning: Airflow did not become healthy in time. Check container logs: docker compose -f docker-compose.airflow.yaml logs airflow" >&2
else
  echo "Airflow UI available at http://localhost:8080"
fi

echo "Startup script finished."
