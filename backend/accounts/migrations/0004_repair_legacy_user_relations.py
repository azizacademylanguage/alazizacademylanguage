from django.db import migrations


def _column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s AND column_name = %s
        """,
        [table, column],
    )
    return cursor.fetchone() is not None


def repair_legacy_user_relations(apps, schema_editor):
    """Restore relationship columns missing from old Railway databases.

    Some legacy databases had migration rows recorded while the real
    ``users.filial_id`` and/or ``users.yaratgan_id`` columns were absent. This
    caused branch/manager lists and student creation requests to return 500.
    The repair only adds nullable columns and indexes; it never deletes users.
    """

    if schema_editor.connection.vendor != 'postgresql':
        return

    connection = schema_editor.connection
    quote = connection.ops.quote_name
    User = apps.get_model('accounts', 'User')
    users_table = User._meta.db_table

    with connection.cursor() as cursor:
        cursor.execute("SELECT to_regclass(%s)", [f'public.{users_table}'])
        if not cursor.fetchone()[0]:
            return

        if not _column_exists(cursor, users_table, 'filial_id'):
            cursor.execute(
                f'ALTER TABLE {quote(users_table)} ADD COLUMN {quote("filial_id")} bigint NULL'
            )
        else:
            cursor.execute(
                f'ALTER TABLE {quote(users_table)} ALTER COLUMN {quote("filial_id")} DROP NOT NULL'
            )

        if not _column_exists(cursor, users_table, 'yaratgan_id'):
            cursor.execute(
                f'ALTER TABLE {quote(users_table)} ADD COLUMN {quote("yaratgan_id")} bigint NULL'
            )
        else:
            cursor.execute(
                f'ALTER TABLE {quote(users_table)} ALTER COLUMN {quote("yaratgan_id")} DROP NOT NULL'
            )

        cursor.execute(
            f'CREATE INDEX IF NOT EXISTS {quote("users_filial_id_idx")} '
            f'ON {quote(users_table)} ({quote("filial_id")})'
        )
        cursor.execute(
            f'CREATE INDEX IF NOT EXISTS {quote("users_yaratgan_id_idx")} '
            f'ON {quote(users_table)} ({quote("yaratgan_id")})'
        )


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0003_repair_legacy_user_table'),
    ]

    operations = [
        migrations.RunPython(repair_legacy_user_relations, migrations.RunPython.noop),
    ]
