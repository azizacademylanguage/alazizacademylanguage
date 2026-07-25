from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_token_version_kirishtarixi'),
        ('exams', '0005_alter_cointarix_sabab'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIYordamchiXabar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('user', "O'quvchi"), ('assistant', 'AI yordamchi')], max_length=20)),
                ('matn', models.TextField()),
                ('meta', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('oquvchi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_yordamchi_xabarlari', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'AI yordamchi xabari',
                'verbose_name_plural': 'AI yordamchi xabarlari',
                'db_table': 'ai_yordamchi_xabarlari',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='Murojaat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kod', models.CharField(db_index=True, editable=False, max_length=16, unique=True)),
                ('kategoriya', models.CharField(choices=[('texnik', 'Texnik muammo'), ('dars', "Dars bo'yicha savol"), ('test', "Test yoki natija"), ('sertifikat', 'Sertifikat'), ('hisob', 'Hisob va xavfsizlik'), ('taklif', 'Taklif'), ('boshqa', 'Boshqa')], default='boshqa', max_length=30)),
                ('sarlavha', models.CharField(max_length=200)),
                ('matn', models.TextField()),
                ('status', models.CharField(choices=[('yangi', 'Yangi'), ('korilmoqda', "Ko'rib chiqilmoqda"), ('javob_berildi', 'Javob berildi'), ('yopildi', 'Yopildi')], default='yangi', max_length=30)),
                ('ustuvorlik', models.CharField(choices=[('past', 'Past'), ('oddiy', 'Oddiy'), ('yuqori', 'Yuqori'), ('shoshilinch', 'Shoshilinch')], default='oddiy', max_length=20)),
                ('oxirgi_javob_adminniki', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('foydalanuvchi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='murojaatlar', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Murojaat',
                'verbose_name_plural': 'Murojaatlar',
                'db_table': 'murojaatlar',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='PlatformSozlama',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform_nomi', models.CharField(default='Al-Aziz Academy', max_length=150)),
                ('platform_qisqa_nomi', models.CharField(default='AL-AZIZ', max_length=40)),
                ('logo_url', models.URLField(blank=True)),
                ('ai_yordamchi_faol', models.BooleanField(default=True)),
                ('ai_kunlik_limit', models.PositiveIntegerField(default=30)),
                ('murojaatlar_faol', models.BooleanField(default=True)),
                ('texnik_rejim', models.BooleanField(default=False)),
                ('texnik_xabar', models.CharField(blank=True, default='Platformada texnik ishlar olib borilmoqda.', max_length=255)),
                ('max_fayl_mb', models.PositiveIntegerField(default=10)),
                ('standart_test_foizi', models.PositiveIntegerField(default=80)),
                ('mashq_coin', models.PositiveIntegerField(default=5)),
                ('final_test_coin', models.PositiveIntegerField(default=50)),
                ('xavfsizlik_eslatmasi', models.CharField(default='Parolingizni hech kimga bermang va umumiy qurilmalarda hisobdan chiqishni unutmang.', max_length=255)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Platforma sozlamasi',
                'verbose_name_plural': 'Platforma sozlamalari',
                'db_table': 'platform_sozlamalari',
            },
        ),
        migrations.CreateModel(
            name='MurojaatJavob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matn', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('muallif', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='murojaat_javoblari', to=settings.AUTH_USER_MODEL)),
                ('murojaat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='javoblar', to='exams.murojaat')),
            ],
            options={
                'verbose_name': 'Murojaat javobi',
                'verbose_name_plural': 'Murojaat javoblari',
                'db_table': 'murojaat_javoblari',
                'ordering': ['created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='aiyordamchixabar',
            index=models.Index(fields=['oquvchi', '-created_at'], name='ai_oquvchi_created_idx'),
        ),
        migrations.AddIndex(
            model_name='murojaat',
            index=models.Index(fields=['status', '-updated_at'], name='murojaat_status_idx'),
        ),
    ]
