"""Repair partially-created final-test and certificate tables on Railway.

Legacy production databases may have migration records without all physical
columns/tables. This migration preserves existing data where possible and only
recreates a table when its essential relationship columns are unusable.
"""

from django.db import migrations


def _columns(connection, table_name):
    with connection.cursor() as cursor:
        return {
            column.name
            for column in connection.introspection.get_table_description(cursor, table_name)
        }


def _backup_name(connection, table_name):
    existing = set(connection.introspection.table_names())
    base = f'{table_name}_legacy_0012'
    candidate = base
    counter = 1
    while candidate in existing:
        counter += 1
        candidate = f'{base}_{counter}'
    return candidate


def _archive_and_recreate(connection, schema_editor, model):
    table_name = model._meta.db_table
    quote = connection.ops.quote_name
    legacy_name = _backup_name(connection, table_name)
    if connection.vendor == 'postgresql':
        schema_editor.execute(f'CREATE TABLE {quote(legacy_name)} AS TABLE {quote(table_name)}')
        schema_editor.execute(f'DROP TABLE {quote(table_name)} CASCADE')
    else:
        schema_editor.execute(f'CREATE TABLE {quote(legacy_name)} AS SELECT * FROM {quote(table_name)}')
        schema_editor.execute(f'DROP TABLE {quote(table_name)}')
    schema_editor.create_model(model)


def _ensure_table(connection, schema_editor, model, essential=(), optional=()):
    table = model._meta.db_table
    tables = set(connection.introspection.table_names())
    if table not in tables:
        schema_editor.create_model(model)
        return

    columns = _columns(connection, table)
    if any(column not in columns for column in essential):
        _archive_and_recreate(connection, schema_editor, model)
        return

    for field_name in optional:
        field = model._meta.get_field(field_name)
        if field.column not in columns:
            schema_editor.add_field(model, field)
            columns.add(field.column)


def repair_final_test_schema(apps, schema_editor):
    connection = schema_editor.connection

    FinalTest = apps.get_model('exams', 'FinalTest')
    FinalTestSavol = apps.get_model('exams', 'FinalTestSavol')
    FinalTestJavob = apps.get_model('exams', 'FinalTestJavob')
    Sertifikat = apps.get_model('exams', 'Sertifikat')
    FinalTestNatija = apps.get_model('exams', 'FinalTestNatija')
    OquvchiCoin = apps.get_model('exams', 'OquvchiCoin')
    CoinTarix = apps.get_model('exams', 'CoinTarix')
    KunlikFaollik = apps.get_model('exams', 'KunlikFaollik')
    Bildirishnoma = apps.get_model('exams', 'Bildirishnoma')

    _ensure_table(
        connection, schema_editor, FinalTest,
        essential=('id', 'daraja_id', 'sarlavha'),
        optional=('otish_bali_foiz',),
    )
    _ensure_table(
        connection, schema_editor, FinalTestSavol,
        essential=('id', 'final_test_id', 'matn'),
        optional=('tartib',),
    )
    _ensure_table(
        connection, schema_editor, FinalTestJavob,
        essential=('id', 'savol_id', 'matn', 'togri'),
        optional=('tartib',),
    )
    _ensure_table(
        connection, schema_editor, Sertifikat,
        essential=('id', 'oquvchi_id', 'daraja_id', 'kod', 'foiz'),
        optional=('berilgan_sana',),
    )
    _ensure_table(
        connection, schema_editor, FinalTestNatija,
        essential=('id', 'oquvchi_id', 'final_test_id', 'foiz', 'otdi'),
        optional=('togri_soni', 'jami_soni', 'sertifikat', 'urinish_raqami', 'created_at'),
    )

    # Reward/notification tables are optional for submission, but creating them
    # here restores the full post-test experience on partially migrated DBs.
    _ensure_table(
        connection, schema_editor, OquvchiCoin,
        essential=('id', 'oquvchi_id', 'balans'),
        optional=('updated_at',),
    )
    _ensure_table(
        connection, schema_editor, CoinTarix,
        essential=('id', 'oquvchi_id', 'miqdor', 'sabab'),
        optional=('izoh', 'created_at'),
    )
    _ensure_table(
        connection, schema_editor, KunlikFaollik,
        essential=('id', 'oquvchi_id', 'sana'),
        optional=('faollik_soni', 'turlar', 'updated_at'),
    )
    _ensure_table(
        connection, schema_editor, Bildirishnoma,
        essential=('id', 'oquvchi_id', 'sarlavha'),
        optional=('matn', 'tur', 'havola', 'oqilgan', 'created_at'),
    )


class Migration(migrations.Migration):
    dependencies = [
        ('exams', '0011_finaltest_minimum_80'),
    ]

    operations = [
        migrations.RunPython(
            repair_final_test_schema,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
