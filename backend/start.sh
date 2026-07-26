#!/usr/bin/env bash
set -u

log() {
  printf '[railway] %s\n' "$1"
}

# Railway avval web serverni ko'rishi kerak. Migratsiya va katalog tayyorlash
# fonda retry bilan bajariladi; shu sabab healthcheck kutib qolmaydi.
maintenance() {
  attempt=1
  max_attempts="${DB_INIT_MAX_ATTEMPTS:-30}"

  while [ "$attempt" -le "$max_attempts" ]; do
    log "Database tayyorlash urinishi ${attempt}/${max_attempts}"

    if python manage.py migrate --noinput \
      && python manage.py repair_database \
      && python manage.py ensure_admin --force; then
      log "Migratsiya va admin tayyor"

      if python manage.py seed_languages --catalog-only; then
        log "CATALOG_SEED_READY"
      else
        log "Katalog seed xato berdi; server ishlashda davom etadi"
      fi
      return 0
    fi

    log "Database hali tayyor emas; 5 soniyadan keyin qayta uriniladi"
    attempt=$((attempt + 1))
    sleep 5
  done

  log "Database tayyorlash urinishlari tugadi. Runtime logini tekshiring."
  return 1
}

maintenance &

log "Gunicorn ${PORT:-8000} portda ishga tushmoqda"
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --threads "${GUNICORN_THREADS:-4}" \
  --timeout "${GUNICORN_TIMEOUT:-120}" \
  --access-logfile - \
  --error-logfile - \
  --capture-output
