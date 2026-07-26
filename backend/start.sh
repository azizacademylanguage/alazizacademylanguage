#!/usr/bin/env bash
set -Eeuo pipefail

echo "[1/4] Migratsiyalar bajarilmoqda..."
python manage.py migrate --noinput

echo "[2/4] Admin login tayyorlanmoqda..."
python manage.py ensure_admin --force

echo "[3/4] Katalog holati tekshirilmoqda..."
NEEDS_SEED="$(python manage.py shell -c "from courses.models import Fan, Daraja, Mavzu; from exams.models import ListeningSavol, SpeakingTopshiriq; print('yes' if Fan.objects.count()<3 or Daraja.objects.count()<21 or Mavzu.objects.count()<63 or ListeningSavol.objects.count()<630 or SpeakingTopshiriq.objects.count()<63 else 'no')" | tail -n 1 | tr -d '\r')"

if [ "$NEEDS_SEED" = "yes" ]; then
  echo "Katalog fonda tayyorlanadi; server kutib turmaydi."
  (
    python manage.py seed_languages --catalog-only
    echo "CATALOG_SEED_READY"
  ) &
else
  echo "CATALOG_ALREADY_READY"
fi

echo "[4/4] Gunicorn ishga tushmoqda..."
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --threads 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
