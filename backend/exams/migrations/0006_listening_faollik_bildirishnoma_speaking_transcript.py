from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0002_alter_user_role'),
        ('courses', '0002_daraja_ochish_uchun_foiz_oquvchifan_qolda_ochilgan'),
        ('exams', '0005_alter_cointarix_sabab'),
    ]

    operations = [
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
            options={'db_table': 'listening_savollari', 'ordering': ['tartib', 'id']},
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
            options={'db_table': 'listening_natijalari', 'ordering': ['-created_at']},
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
            options={'db_table': 'kunlik_faolliklar', 'ordering': ['-sana'], 'unique_together': {('oquvchi', 'sana')}},
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
            options={'db_table': 'bildirishnomalar', 'ordering': ['-created_at']},
        ),
        migrations.AddIndex(
            model_name='bildirishnoma',
            index=models.Index(fields=['oquvchi', 'oqilgan', '-created_at'], name='bildirish_oquvchi_0b824d_idx'),
        ),
    ]
