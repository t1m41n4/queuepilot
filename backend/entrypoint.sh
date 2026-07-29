#!/bin/sh
set -e

max_retries="${MIGRATION_MAX_RETRIES:-10}"
retry_delay="${MIGRATION_RETRY_DELAY_SECONDS:-3}"
attempt=1

while ! alembic upgrade head; do
  if [ "$attempt" -ge "$max_retries" ]; then
    echo "Database migration failed after ${attempt} attempts" >&2
    exit 1
  fi
  echo "Database migration attempt ${attempt} failed; retrying in ${retry_delay}s" >&2
  attempt=$((attempt + 1))
  sleep "$retry_delay"
done

echo "Database migrations completed successfully"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
