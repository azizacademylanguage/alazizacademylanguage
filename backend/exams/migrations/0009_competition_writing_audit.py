from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0006_student_subscription_fields'),
        ('courses', '0002_daraja_ochish_uchun_foiz_oquvchifan_qolda_ochilgan'),
        ('exams', '0008_repair_word_game_schema'),
    ]

    operations = [
        migrations.AddField(model_name='writingnatija', name='baholash_tafsiloti', field=models.JSONField(blank=True, default=dict)),
        migrations.AddField(model_name='adminamallog', name='obyekt_turi', field=models.CharField(blank=True, max_length=80)),
        migrations.AddField(model_name='adminamallog', name='obyekt_id', field=models.CharField(blank=True, max_length=80)),
        migrations.AddField(model_name='adminamallog', name='ip_manzil', field=models.GenericIPAddressField(blank=True, null=True)),
        migrations.AddField(model_name='adminamallog', name='oldingi_holat', field=models.JSONField(blank=True, default=dict)),
        migrations.AddField(model_name='adminamallog', name='yangi_holat', field=models.JSONField(blank=True, default=dict)),
        migrations.CreateModel(
            name='Musobaqa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nomi', models.CharField(max_length=180)),
                ('tavsif', models.TextField(blank=True)),
                ('boshlanish_sana', models.DateField()),
                ('tugash_sana', models.DateField()),
                ('status', models.CharField(choices=[('reja', 'Rejada'), ('faol', 'Faol'), ('yakun', 'Yakunlangan')], default='reja', max_length=20)),
                ('birinchi_coin', models.PositiveIntegerField(default=100)),
                ('ikkinchi_coin', models.PositiveIntegerField(default=60)),
                ('uchinchi_coin', models.PositiveIntegerField(default=30)),
                ('goliblar', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('fan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='musobaqalar', to='courses.fan')),
                ('filial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='musobaqalar', to='accounts.filial')),
                ('yaratgan', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='yaratgan_musobaqalar', to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'musobaqalar', 'ordering': ['-boshlanish_sana', '-id']},
        ),
    ]
