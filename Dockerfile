# ============================================
# Stage 1: Builder
# ============================================
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements/base.txt requirements/base.txt
COPY requirements/docker.txt requirements/docker.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements/docker.txt

# ============================================
# Stage 2: Runtime
# ============================================
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN groupadd -r app && useradd -r -g app -d /app -s /sbin/nologin app

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Entrypoint script
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create directories for static/media
RUN mkdir -p /app/staticfiles /app/media && \
    chown -R app:app /app

# Collect static files at build time (dummy env vars for collectstatic)
ENV DJANGO_SETTINGS_MODULE=config.settings.docker
RUN DJANGO_SECRET_KEY=build-only-dummy-key \
    POSTGRES_DB=x POSTGRES_USER=x POSTGRES_PASSWORD=x \
    POSTGRES_HOST=x POSTGRES_PORT=5432 \
    AWS_ACCESS_KEY_ID=x AWS_SECRET_ACCESS_KEY=x \
    MINIO_ENDPOINT_URL=http://localhost:9000 \
    python manage.py collectstatic --noinput 2>/dev/null || true

RUN chown -R app:app /app/staticfiles

USER app

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
