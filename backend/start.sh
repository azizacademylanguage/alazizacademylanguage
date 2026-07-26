#!/usr/bin/env bash
set -Eeuo pipefail

echo "[1/4] Migratsiyalar bajarilmoqda..."
python manage.py migrate --noinput

echo "[2/4] Fanlar, darajalar va testlar tekshirilmoqda..."
python manage.py seed_languages --catalog-only

echo "[3/4] Admin login tayyorlanmoqda..."
python manage.py ensure_admin --force

echo "[4/4] Gunicorn ishga tushmoqda..."
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --threads 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
