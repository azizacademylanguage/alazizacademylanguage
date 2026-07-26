from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection

from accounts.db_utils import reset_model_sequences


class Command(BaseCommand):
    help = "Legacy Railway PostgreSQL constraints and serial sequences are repaired safely."

    def handle(self, *args, **options):
        if connection.vendor != "postgresql":
            self.stdout.write(self.style.SUCCESS("DB_REPAIR_SKIPPED vendor is not PostgreSQL"))
            return

        with connection.cursor() as cursor:
            # Some older production databases had these foreign keys marked
            # NOT NULL even though the Django model has always allowed null.
            # Dropping NOT NULL is safe and preserves all existing data.
            cursor.execute("SELECT to_regclass('public.users')")
            if cursor.fetchone()[0]:
                cursor.execute('ALTER TABLE "users" ALTER COLUMN "filial_id" DROP NOT NULL')
                cursor.execute('ALTER TABLE "users" ALTER COLUMN "yaratgan_id" DROP NOT NULL')

        updated = reset_model_sequences(apps.get_models())
        self.stdout.write(self.style.SUCCESS(f"DB_REPAIR_READY sequences={updated}"))
