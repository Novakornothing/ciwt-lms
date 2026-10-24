#!/bin/sh
# CIWT LMS container entrypoint: persistent data lives on the mounted volume ($CIWT_DATA_DIR, default /var/data/ciwt).
set -e
DATA="${CIWT_DATA_DIR:-/var/data/ciwt}"
mkdir -p "$DATA/instance" "$DATA/backups"
case "${DATABASE_URL:-}" in
  sqlite:////*)
    DB="${DATABASE_URL#sqlite:///}"
    if [ ! -f "$DB" ] && [ -f /app/ciwt_lms.db ] && [ "${CIWT_SEED_FROM_BUNDLE:-1}" = "1" ]; then
      echo "First boot: copying the bundled ciwt_lms.db to $DB"
      cp /app/ciwt_lms.db "$DB"
    fi ;;
esac
exec gunicorn app:app --bind "0.0.0.0:${PORT:-8000}" --workers "${WEB_CONCURRENCY:-1}" --threads "${GUNICORN_THREADS:-8}" \
  --timeout "${GUNICORN_TIMEOUT:-120}" --forwarded-allow-ips="${FORWARDED_ALLOW_IPS:-127.0.0.1}" --access-logfile -
