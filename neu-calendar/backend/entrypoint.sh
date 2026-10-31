#!/usr/bin/env bash
set -e

echo "[ENTRYPOINT] Waiting for database connection..."
python - << 'EOF'
import time
import sys
import os
import psycopg2
from urllib.parse import urlparse

db_url = os.environ.get("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/neu_calendar")
# Normalize scheme for psycopg2
db_url = db_url.replace("postgresql+psycopg2://", "postgresql://")
result = urlparse(db_url)
username = result.username or "postgres"
password = result.password or "postgres"
database = result.path[1:] if result.path else "neu_calendar"
hostname = result.hostname or "db"
port = result.port or 5432

max_tries = 30
for i in range(max_tries):
    try:
        conn = psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host=hostname,
            port=port,
            connect_timeout=3
        )
        conn.close()
        print("[ENTRYPOINT] Successfully connected to PostgreSQL!")
        sys.exit(0)
    except Exception as e:
        print(f"[ENTRYPOINT] DB not ready yet (attempt {i+1}/{max_tries}): {e}")
        time.sleep(1)

print("[ENTRYPOINT] Could not connect to database after 30 seconds.")
sys.exit(1)
EOF

echo "[ENTRYPOINT] Running Alembic database migrations..."
alembic upgrade head

echo "[ENTRYPOINT] Checking and seeding initial sample data..."
python -m app.seed.seed_data

echo "[ENTRYPOINT] Starting FastAPI application with Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
