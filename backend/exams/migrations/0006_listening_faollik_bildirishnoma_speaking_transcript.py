"""
Listening, speaking transcript, streak and notification schema.

Railway/PostgreSQL'da ayrim jadvallar avvalgi deploy urinishida allaqachon
yaratilgan bo'lishi mumkin. Oddiy CreateModel bunday holatda DuplicateTable
beradi. Ushbu migration database sxemasini introspection orqali tekshiradi va
faqat yetishmayotgan jadval/ustun/indexlarni yaratadi; migration state esa
odatdagi Django holatida saqlanadi.
"""

from django.apps import apps as global_apps
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


BILDIRISHNOMA_INDEX_NAME = 'bildirish_oquvchi_0b824d_idx'


def _table_columns(connection, table_name):
    with connection.cursor() as cursor:
        return {
            column.name
            for column in connection.introspection.get_table_description(cursor, table_name)
        }


def _constraints(connection, table_name):
    with connection.cursor() as cursor:
        return connection.introspection.get_constraints(cursor, table_name)


def _required_columns(model):
    """Return physical DB column names required by the current model."""
    return {field.column for field in model._meta.local_fields}


def _next_legacy_table_name(connection, table_name):
    """Choose a collision-free backup name for a malformed pre-existing table."""
    existing = set(connection.introspection.table_names())
    base = f"{table_name}_legacy_0006"
    candidate = base
    number = 1
    while candidate in existing:
        number += 1
        candidate = f"{base}_{number}"
    return candidate


def _archive_malformed_table(connection, schema_editor, table_name):
    """
    Copy malformed rows to a legacy table, then remove the broken table.

    We copy+drop instead of a simple RENAME because PostgreSQL may keep the
    original identity sequence name after a rename. That can conflict when
    Django creates the replacement table with the original name.
    """
    legacy_name = _next_legacy_table_name(connection, table_name)
    quote = connection.ops.quote_name
    if connection.vendor == 'postgresql':
        schema_editor.execute(
            f"CREATE TABLE {quote(legacy_name)} AS TABLE {quote(table_name)}"
        )
        schema_editor.execute(f"DROP TABLE {quote(table_name)} CASCADE")
    else:
        schema_editor.execute(
            f"CREATE TABLE {quote(legacy_name)} AS SELECT * FROM {quote(table_name)}"
        )
        schema_editor.execute(f"DROP TABLE {quote(table_name)}")
    return legacy_name


def _ensure_model_table(connection, schema_editor, model, existing_tables):
    """
    Ensure the table matches at least the columns required by the model.

    A previous interrupted Railway deploy may have left a table with the same
    name but a completely different/partial schema. In that case we preserve
    it under a *_legacy_0006 name and create the correct Django table.
    """
    table_name = model._meta.db_table
    if table_name not in existing_tables:
        schema_editor.create_model(model)
        existing_tables.add(table_name)
        return True

    columns = _table_columns(connection, table_name)
    required = _required_columns(model)
    missing = required - columns
    if missing:
        _archive_malformed_table(connection, schema_editor, table_name)
        schema_editor.create_model(model)
        return True

    return False


def ensure_0006_database_schema(apps, schema_editor):
    """Create only missing schema pieces and repair partial Railway tables."""
    connection = schema_editor.connection
    existing_tables = set(connection.introspection.table_names())

    # Runtime models are used intentionally: the models are introduced in the
    # state_operations of this same SeparateDatabaseAndState migration.
    SpeakingNatija = global_apps.get_model('exams', 'SpeakingNatija')
    ListeningSavol = global_apps.get_model('exams', 'ListeningSavol')
    ListeningNatija = global_apps.get_model('exams', 'ListeningNatija')
    KunlikFaollik = global_apps.get_model('exams', 'KunlikFaollik')
    Bildirishnoma = global_apps.get_model('exams', 'Bildirishnoma')

    speaking_table = SpeakingNatija._meta.db_table
    if speaking_table in existing_tables:
        speaking_columns = _table_columns(connection, speaking_table)
        if 'transkripsiya' not in speaking_columns:
            schema_editor.add_field(
                SpeakingNatija,
                SpeakingNatija._meta.get_field('transkripsiya'),
            )

    created_or_repaired = set()
    for model in (ListeningSavol, ListeningNatija, KunlikFaollik, Bildirishnoma):
        if _ensure_model_table(connection, schema_editor, model, existing_tables):
            created_or_repaired.add(model._meta.db_table)

    # Add the notification index only after validating that all referenced
    # columns exist. Newly created tables already receive Meta.indexes.
    notification_table = Bildirishnoma._meta.db_table
    if notification_table in existing_tables and notification_table not in created_or_repaired:
        columns = _table_columns(connection, notification_table)
        index_columns = {'oquvchi_id', 'oqilgan', 'created_at'}
        if index_columns.issubset(columns):
            constraints = _constraints(connection, notification_table)
            if BILDIRISHNOMA_INDEX_NAME not in constraints:
                schema_editor.add_index(
                    Bildirishnoma,
                    models.Index(
                        fields=['oquvchi', 'oqilgan', '-created_at'],
                        name=BILDIRISHNOMA_INDEX_NAME,
                    ),
                )


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0002_alter_user_role'),
        ('courses', '0002_daraja_ochish_uchun_foiz_oquvchifan_qolda_ochilgan'),
        ('exams', '0005_alter_cointarix_sabab'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    ensure_0006_database_schema,
                    reverse_code=migrations.RunPython.noop,
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='speakingnatija',
                    name='transkripsiya',
                    field=models.TextField(blank=True),
                ),
                migrations.CreateModel(
                    name='ListeningSavol',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('audio_matn', models.CharField(max_length=500)),
                        ('savol', models.CharField(default="Eshitgan so'zingizning tarjimasini tanlang", max_length=500)),
                        ('variantlar', models.JSONField(default=list)),
                        ('togri_javob', models.CharField(max_length=255)),
                        ('til_kodi', models.CharField(default='en-US', max_length=20)),
                        ('tartib', models.PositiveIntegerField(default=0)),
                        ('dars', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listening_savollari', to='courses.dars')),
                    ],
                    options={'db_table': 'listening_savollari', 'ordering': ['tartib', 'id'], 'verbose_name': 'Listening savoli', 'verbose_name_plural': 'Listening savollari'},
                ),
                migrations.CreateModel(
                    name='ListeningNatija',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('togri_soni', models.PositiveIntegerField(default=0)),
                        ('jami_soni', models.PositiveIntegerField(default=0)),
                        ('foiz', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                        ('javoblar', models.JSONField(blank=True, default=list)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('dars', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listening_natijalari', to='courses.dars')),
                        ('oquvchi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listening_natijalari', to='accounts.user')),
                    ],
                    options={'db_table': 'listening_natijalari', 'ordering': ['-created_at'], 'verbose_name': 'Listening natijasi', 'verbose_name_plural': 'Listening natijalari'},
                ),
                migrations.CreateModel(
                    name='KunlikFaollik',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('sana', models.DateField(default=django.utils.timezone.localdate)),
                        ('faollik_soni', models.PositiveIntegerField(default=0)),
                        ('turlar', models.JSONField(blank=True, default=list)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('oquvchi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kunlik_faolliklar', to='accounts.user')),
                    ],
                    options={'db_table': 'kunlik_faolliklar', 'ordering': ['-sana'], 'unique_together': {('oquvchi', 'sana')}, 'verbose_name': 'Kunlik faollik', 'verbose_name_plural': 'Kunlik faolliklar'},
                ),
                migrations.CreateModel(
                    name='Bildirishnoma',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('sarlavha', models.CharField(max_length=180)),
                        ('matn', models.TextField(blank=True)),
                        ('tur', models.CharField(choices=[('info', "Ma'lumot"), ('success', 'Muvaffaqiyat'), ('warning', 'Ogohlantirish'), ('shop', "Do'kon"), ('certificate', 'Sertifikat')], default='info', max_length=20)),
                        ('havola', models.CharField(blank=True, max_length=300)),
                        ('oqilgan', models.BooleanField(default=False)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('oquvchi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bildirishnomalar', to='accounts.user')),
                    ],
                    options={'db_table': 'bildirishnomalar', 'ordering': ['-created_at'], 'verbose_name': 'Bildirishnoma', 'verbose_name_plural': 'Bildirishnomalar'},
                ),
                migrations.AddIndex(
                    model_name='bildirishnoma',
                    index=models.Index(fields=['oquvchi', 'oqilgan', '-created_at'], name=BILDIRISHNOMA_INDEX_NAME),
                ),
            ],
        ),
    ]
