import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_role'),
        ('courses', '0002_daraja_ochish_uchun_foiz_oquvchifan_qolda_ochilgan'),
        ('exams', '0003_mashq_default_80'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopbuyurtma',
            name='status',
            field=models.CharField(
                choices=[('yangi', 'Yangi'), ('tayyor', 'Tayyorlanmoqda'), ('berildi', 'Berildi')],
                default='yangi',
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name='SozJuftligi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chet_soz', models.CharField(max_length=180)),
                ('uzbek_soz', models.CharField(max_length=180)),
                ('tartib', models.PositiveIntegerField(default=0)),
                ('faol', models.BooleanField(default=True)),
                ('fan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='soz_juftliklari', to='courses.fan')),
            ],
            options={
                'verbose_name': "So'z juftligi",
                'verbose_name_plural': "So'z juftliklari",
                'db_table': 'soz_juftliklari',
                'ordering': ['tartib', 'id'],
                'unique_together': {('fan', 'chet_soz', 'uzbek_soz')},
            },
        ),
        migrations.CreateModel(
            name='SozOyiniSessiya',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('cardlar', models.JSONField(default=list)),
                ('tugallangan', models.BooleanField(default=False)),
                ('topilgan_soni', models.PositiveIntegerField(default=0)),
                ('berilgan_coin', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('fan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='soz_oyini_sessiyalari', to='courses.fan')),
                ('oquvchi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='soz_oyini_sessiyalari', to='accounts.user')),
            ],
            options={
                'verbose_name': "So'z o'yini sessiyasi",
                'verbose_name_plural': "So'z o'yini sessiyalari",
                'db_table': 'soz_oyini_sessiyalari',
                'ordering': ['-created_at'],
            },
        ),
    ]
