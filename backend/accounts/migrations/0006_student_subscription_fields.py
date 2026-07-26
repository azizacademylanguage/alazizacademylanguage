"""Add subscription fields without breaking legacy Railway databases.

Some production databases received these columns from an earlier manual repair,
while Django's migration history still says that migration 0006 is pending.
A normal ``AddField`` therefore raises ``DuplicateColumn``.  The database part
below inspects the real ``users`` table and only creates missing columns.  The
state part still records all fields so future migrations see the correct model.
"""

from django.db import migrations, models


def _existing_columns(schema_editor, table_name):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        description = connection.introspection.get_table_description(cursor, table_name)
    return {column.name for column in description}


def ensure_subscription_columns(apps, schema_editor):
    table = 'users'
    qn = schema_editor.quote_name
    columns = _existing_columns(schema_editor, table)
    vendor = schema_editor.connection.vendor

    # SQL types supported by both PostgreSQL and SQLite.  Fixed literals are
    # used here; no user-controlled values are interpolated.
    if 'tarif' not in columns:
        schema_editor.execute(
            f"ALTER TABLE {qn(table)} ADD COLUMN {qn('tarif')} varchar(80) "
            "DEFAULT 'Standart' NOT NULL"
        )
    if 'boshlanish_sana' not in columns:
        schema_editor.execute(
            f"ALTER TABLE {qn(table)} ADD COLUMN {qn('boshlanish_sana')} date NULL"
        )
    if 'tugash_sana' not in columns:
        schema_editor.execute(
            f"ALTER TABLE {qn(table)} ADD COLUMN {qn('tugash_sana')} date NULL"
        )
    if 'tolov_holati' not in columns:
        schema_editor.execute(
            f"ALTER TABLE {qn(table)} ADD COLUMN {qn('tolov_holati')} varchar(20) "
            "DEFAULT 'tolangan' NOT NULL"
        )
    if 'muddat_bloklash' not in columns:
        bool_default = 'TRUE' if vendor == 'postgresql' else '1'
        schema_editor.execute(
            f"ALTER TABLE {qn(table)} ADD COLUMN {qn('muddat_bloklash')} boolean "
            f"DEFAULT {bool_default} NOT NULL"
        )

    # Repair partially-created PostgreSQL columns left by an interrupted deploy.
    # SQLite does not support these ALTER COLUMN statements and does not need
    # them for fresh local databases.
    if vendor == 'postgresql':
        schema_editor.execute(
            f"UPDATE {qn(table)} SET {qn('tarif')} = 'Standart' "
            f"WHERE {qn('tarif')} IS NULL"
        )
        schema_editor.execute(
            f"ALTER TABLE {qn(table)} ALTER COLUMN {qn('tarif')} SET DEFAULT 'Standart'"
        )
        schema_editor.execute(
            f"ALTER TABLE {qn(table)} ALTER COLUMN {qn('tarif')} SET NOT NULL"
        )

        schema_editor.execute(
            f"UPDATE {qn(table)} SET {qn('tolov_holati')} = 'tolangan' "
            f"WHERE {qn('tolov_holati')} IS NULL"
        )
        schema_editor.execute(
            f"ALTER TABLE {qn(table)} ALTER COLUMN {qn('tolov_holati')} SET DEFAULT 'tolangan'"
        )
        schema_editor.execute(
            f"ALTER TABLE {qn(table)} ALTER COLUMN {qn('tolov_holati')} SET NOT NULL"
        )

        schema_editor.execute(
            f"UPDATE {qn(table)} SET {qn('muddat_bloklash')} = TRUE "
            f"WHERE {qn('muddat_bloklash')} IS NULL"
        )
        schema_editor.execute(
            f"ALTER TABLE {qn(table)} ALTER COLUMN {qn('muddat_bloklash')} SET DEFAULT TRUE"
        )
        schema_editor.execute(
            f"ALTER TABLE {qn(table)} ALTER COLUMN {qn('muddat_bloklash')} SET NOT NULL"
        )


class Migration(migrations.Migration):
    dependencies = [('accounts', '0005_user_token_version')]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    ensure_subscription_columns,
                    reverse_code=migrations.RunPython.noop,
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='user',
                    name='tarif',
                    field=models.CharField(blank=True, default='Standart', max_length=80),
                ),
                migrations.AddField(
                    model_name='user',
                    name='boshlanish_sana',
                    field=models.DateField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name='user',
                    name='tugash_sana',
                    field=models.DateField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name='user',
                    name='tolov_holati',
                    field=models.CharField(
                        choices=[
                            ('tolangan', "To'langan"),
                            ('qarzdor', 'Qarzdor'),
                            ('kutilmoqda', 'Kutilmoqda'),
                        ],
                        default='tolangan',
                        max_length=20,
                    ),
                ),
                migrations.AddField(
                    model_name='user',
                    name='muddat_bloklash',
                    field=models.BooleanField(default=True),
                ),
            ],
        ),
    ]
