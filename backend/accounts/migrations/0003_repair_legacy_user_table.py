from django.db import migrations


def repair_legacy_user_table(apps, schema_editor):
    """Repair old Railway schemas without deleting any user data."""

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

        # Legacy copies of this project sometimes had these columns NOT NULL.
        cursor.execute(
            f'ALTER TABLE {quote(table)} ALTER COLUMN {quote("filial_id")} DROP NOT NULL'
        )
        cursor.execute(
            f'ALTER TABLE {quote(table)} ALTER COLUMN {quote("yaratgan_id")} DROP NOT NULL'
        )

        # Imported/restored data can leave PostgreSQL sequences behind MAX(id),
        # which causes POST create requests to fail with duplicate primary keys.
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
