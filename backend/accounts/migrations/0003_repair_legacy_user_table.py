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


def repair_legacy_user_table(apps, schema_editor):
    """Repair old Railway schemas without deleting any user data.

    Earlier production copies did not all have the same ``users`` columns.
    This migration therefore checks a column before touching it instead of
    assuming that every legacy database matches the original migration state.
    """

    if schema_editor.connection.vendor != 'postgresql':
        return

    quote = schema_editor.connection.ops.quote_name
    User = apps.get_model('accounts', 'User')
    table = User._meta.db_table
    pk_column = User._meta.pk.column

    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT to_regclass(%s)", [f'public.{table}'])
        if not cursor.fetchone()[0]:
            return

        for column in ('filial_id', 'yaratgan_id'):
            if _column_exists(cursor, table, column):
                cursor.execute(
                    f'ALTER TABLE {quote(table)} ALTER COLUMN {quote(column)} DROP NOT NULL'
                )

        cursor.execute("SELECT pg_get_serial_sequence(%s, %s)", [table, pk_column])
        row = cursor.fetchone()
        sequence_name = row[0] if row else None
        if sequence_name:
            cursor.execute(
                f'SELECT COALESCE(MAX({quote(pk_column)}), 0) FROM {quote(table)}'
            )
            max_pk = int(cursor.fetchone()[0] or 0)
            if max_pk > 0:
                cursor.execute("SELECT setval(%s, %s, true)", [sequence_name, max_pk])
            else:
                cursor.execute("SELECT setval(%s, 1, false)", [sequence_name])


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0002_alter_user_role'),
    ]

    operations = [
        migrations.RunPython(repair_legacy_user_table, migrations.RunPython.noop),
    ]
