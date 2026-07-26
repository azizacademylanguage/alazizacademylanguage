from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection

from accounts.db_utils import reset_model_sequences


def column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s AND column_name = %s
        """,
        [table, column],
    )
    return cursor.fetchone() is not None


class Command(BaseCommand):
    help = "Legacy Railway PostgreSQL constraints and serial sequences are repaired safely."

    def handle(self, *args, **options):
        if connection.vendor != "postgresql":
            self.stdout.write(self.style.SUCCESS("DB_REPAIR_SKIPPED vendor is not PostgreSQL"))
            return

        with connection.cursor() as cursor:
            cursor.execute("SELECT to_regclass('public.users')")
            if cursor.fetchone()[0]:
                # These columns are created by accounts.0004 when missing. The
                # command remains defensive so a partially migrated container
                # never crashes in an endless restart loop.
                for column in ('filial_id', 'yaratgan_id'):
                    if column_exists(cursor, 'users', column):
                        cursor.execute(
                            f'ALTER TABLE "users" ALTER COLUMN "{column}" DROP NOT NULL'
                        )

        updated = reset_model_sequences(apps.get_models())
        self.stdout.write(self.style.SUCCESS(f"DB_REPAIR_READY sequences={updated}"))
