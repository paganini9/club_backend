#!/bin/bash
set -e

# ──────────────────────────────────────────────
# PostgreSQL 대기
# ──────────────────────────────────────────────
echo "Waiting for PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT}..."

python << 'EOF'
import os
import socket
import time

host = os.environ.get("POSTGRES_HOST", "db")
port = int(os.environ.get("POSTGRES_PORT", "5432"))
timeout = 30
start = time.time()

while True:
    try:
        sock = socket.create_connection((host, port), timeout=2)
        sock.close()
        print(f"PostgreSQL is ready at {host}:{port}")
        break
    except (socket.error, OSError):
        elapsed = time.time() - start
        if elapsed >= timeout:
            print(f"Timeout: PostgreSQL not available after {timeout}s")
            exit(1)
        time.sleep(1)
EOF

# ──────────────────────────────────────────────
# 마이그레이션
# ──────────────────────────────────────────────
echo "Running migrations..."
python manage.py migrate --noinput

# ──────────────────────────────────────────────
# 시드 데이터 (SEED_DATA=true 인 경우)
# ──────────────────────────────────────────────
if [ "${SEED_DATA}" = "true" ]; then
    echo "Loading seed data..."
    python manage.py seed_data || echo "Seed data already exists or failed (non-fatal)"
fi

# ──────────────────────────────────────────────
# Static files 수집
# ──────────────────────────────────────────────
echo "Collecting static files..."
python manage.py collectstatic --noinput

# ──────────────────────────────────────────────
# CMD 실행 (시그널 전달을 위해 exec 사용)
# ──────────────────────────────────────────────
echo "Starting server..."
exec "$@"
