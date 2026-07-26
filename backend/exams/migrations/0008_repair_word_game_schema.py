"""Repair word-game tables missing from partially migrated Railway databases.

Some production databases recorded exams.0004 as applied even though one or
both physical word-game tables were never created. The runtime repair command
must not crash on those absent tables, and this migration recreates the actual
schema without touching unrelated student data.
"""

from django.db import migrations


def _table_columns(connection, table_name):
    with connection.cursor() as cursor:
        return {
            column.name
            for column in connection.introspection.get_table_description(cursor, table_name)
        }


def _required_columns(model):
    return {field.column for field in model._meta.local_fields}


def _backup_name(connection, table_name):
    existing = set(connection.introspection.table_names())
    base = f'{table_name}_legacy_0008'
    candidate = base
    counter = 1
    while candidate in existing:
        counter += 1
        candidate = f'{base}_{counter}'
    return candidate


def _archive_and_recreate(connection, schema_editor, model):
    table_name = model._meta.db_table
    legacy_name = _backup_name(connection, table_name)
    quote = connection.ops.quote_name

    if connection.vendor == 'postgresql':
        schema_editor.execute(
            f'CREATE TABLE {quote(legacy_name)} AS TABLE {quote(table_name)}'
        )
        schema_editor.execute(f'DROP TABLE {quote(table_name)} CASCADE')
    else:
        schema_editor.execute(
            f'CREATE TABLE {quote(legacy_name)} AS SELECT * FROM {quote(table_name)}'
        )
        schema_editor.execute(f'DROP TABLE {quote(table_name)}')

    schema_editor.create_model(model)


def _ensure_model_table(connection, schema_editor, model, existing_tables):
    table_name = model._meta.db_table
    if table_name not in existing_tables:
        schema_editor.create_model(model)
        existing_tables.add(table_name)
        return

    columns = _table_columns(connection, table_name)
    missing = _required_columns(model) - columns
    if missing:
        _archive_and_recreate(connection, schema_editor, model)


def repair_word_game_schema(apps, schema_editor):
    connection = schema_editor.connection
    existing_tables = set(connection.introspection.table_names())

    SozJuftligi = apps.get_model('exams', 'SozJuftligi')
    SozOyiniSessiya = apps.get_model('exams', 'SozOyiniSessiya')
    ShopBuyurtma = apps.get_model('exams', 'ShopBuyurtma')

    _ensure_model_table(connection, schema_editor, SozJuftligi, existing_tables)
    _ensure_model_table(connection, schema_editor, SozOyiniSessiya, existing_tables)

    # A partial exams.0004 may also have skipped the order status column.
    shop_table = ShopBuyurtma._meta.db_table
    if shop_table in existing_tables:
        columns = _table_columns(connection, shop_table)
        status_field = ShopBuyurtma._meta.get_field('status')
        if status_field.column not in columns:
            schema_editor.add_field(ShopBuyurtma, status_field)


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0005_user_token_version'),
        ('exams', '0007_alter_cointarix_sabab'),
    ]

    operations = [
        migrations.RunPython(
            repair_word_game_schema,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
