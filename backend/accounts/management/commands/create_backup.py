from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.backup_views import build_backup_bytes


class Command(BaseCommand):
    help = "Platformaning JSON/ZIP backup faylini MEDIA_ROOT/backups ichiga yaratadi."

    def add_arguments(self, parser):
        parser.add_argument('--keep', type=int, default=7, help='Eng oxirgi nechta backup saqlansin')

    def handle(self, *args, **options):
        directory = Path(settings.MEDIA_ROOT) / 'backups'
        directory.mkdir(parents=True, exist_ok=True)
        payload, manifest = build_backup_bytes()
        path = directory / f"alaziz_backup_{timezone.now():%Y%m%d_%H%M%S}.zip"
        path.write_bytes(payload)
        files = sorted(directory.glob('alaziz_backup_*.zip'), reverse=True)
        for old in files[max(options['keep'], 1):]:
            old.unlink(missing_ok=True)
        self.stdout.write(self.style.SUCCESS(f"BACKUP_READY path={path} rows={sum(manifest['models'].values())}"))
