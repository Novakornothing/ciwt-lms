# CIWT LMS — production image. Persistent state (SQLite DB + WAL, LTI/SSO keys, backups) lives on a mounted
# volume at /var/data/ciwt; the container filesystem itself is disposable. See docs/PRODUCTION_HOSTING.md.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    CIWT_DATA_DIR=/var/data/ciwt \
    DATABASE_URL=sqlite:////var/data/ciwt/ciwt_lms.db \
    CIWT_INSTANCE_DIR=/var/data/ciwt/instance \
    CIWT_BACKUP_DIR=/var/data/ciwt/backups \
    CIWT_SQLITE_WAL=1 \
    PORT=8000
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --system --uid 10001 --home /app ciwt && mkdir -p /var/data/ciwt && chown -R ciwt /var/data/ciwt /app
USER ciwt
VOLUME ["/var/data/ciwt"]
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=4).status == 200 else 1)"
ENTRYPOINT ["/app/docker/entrypoint.sh"]
