#!/usr/bin/env bash
set -Eeuo pipefail

log() { printf '[railway] %s\n' "$1"; }

log "Database migration boshlandi"
python manage.py migrate --noinput

log "Admin login tayyorlanmoqda"
python manage.py ensure_admin --force

log "Katalog tekshirilmoqda"
NEEDS_SEED="$(python manage.py shell -c "from courses.models import Fan, Daraja, Mavzu; from exams.models import ListeningSavol, SpeakingTopshiriq; print('yes' if Fan.objects.count()<3 or Daraja.objects.count()<21 or Mavzu.objects.count()<63 or ListeningSavol.objects.count()<630 or SpeakingTopshiriq.objects.count()<63 else 'no')" | tail -n 1 | tr -d '\r')"

if [ "$NEEDS_SEED" = "yes" ]; then
  log "Katalog fonda yaratiladi"
  (
    python manage.py seed_languages --catalog-only
    log "CATALOG_SEED_READY"
  ) 2>&1 &
else
  log "CATALOG_ALREADY_READY"
fi

log "Gunicorn ${PORT:-8000} portda ishga tushmoqda"
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --threads 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  --capture-output
