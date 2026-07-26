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


def ensure_0006_database_schema(apps, schema_editor):
    """Create only schema pieces that do not already exist."""
    connection = schema_editor.connection
    existing_tables = set(connection.introspection.table_names())

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

    created_tables = set()
    for model in (ListeningSavol, ListeningNatija, KunlikFaollik, Bildirishnoma):
        table_name = model._meta.db_table
        if table_name not in existing_tables:
            schema_editor.create_model(model)
            existing_tables.add(table_name)
            created_tables.add(table_name)

    # Existing bildirishnomalar table may predate this migration's index.
    if (
        Bildirishnoma._meta.db_table in existing_tables
        and Bildirishnoma._meta.db_table not in created_tables
    ):
        constraints = _constraints(connection, Bildirishnoma._meta.db_table)
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
