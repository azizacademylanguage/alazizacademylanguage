"""Synchronise the legacy ``users.token_version`` column safely.

Some Railway databases already contain the column with a NOT NULL constraint,
while fresh databases do not have it yet. A normal AddField would therefore
fail on one of those two schemas. This migration introspects the real table,
adds the column only when it is missing, repairs NULL values, and records the
field in Django's migration state.
"""

from django.apps import apps as global_apps
from django.db import migrations, models


def _column_names(connection, table_name):
    with connection.cursor() as cursor:
        return {
            column.name
            for column in connection.introspection.get_table_description(cursor, table_name)
        }


def ensure_token_version_column(apps, schema_editor):
    connection = schema_editor.connection
    User = global_apps.get_model('accounts', 'User')
    table = User._meta.db_table
    field = User._meta.get_field('token_version')

    existing_tables = set(connection.introspection.table_names())
    if table not in existing_tables:
        return

    columns = _column_names(connection, table)
    quote = connection.ops.quote_name

    if field.column not in columns:
        schema_editor.add_field(User, field)

    # Existing production copies may have NULL rows or no database default.
    # Keep a DB-level default as well so old/raw insert paths cannot fail.
    if connection.vendor == 'postgresql':
        schema_editor.execute(
            f'UPDATE {quote(table)} SET {quote(field.column)} = 0 '
            f'WHERE {quote(field.column)} IS NULL'
        )
        schema_editor.execute(
            f'ALTER TABLE {quote(table)} ALTER COLUMN {quote(field.column)} SET DEFAULT 0'
        )
        schema_editor.execute(
            f'ALTER TABLE {quote(table)} ALTER COLUMN {quote(field.column)} SET NOT NULL'
        )


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0004_repair_legacy_user_relations'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    ensure_token_version_column,
                    reverse_code=migrations.RunPython.noop,
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='user',
                    name='token_version',
                    field=models.PositiveIntegerField(default=0),
                ),
            ],
        ),
    ]
