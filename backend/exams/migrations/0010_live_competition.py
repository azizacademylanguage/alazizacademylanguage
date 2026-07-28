from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('exams', '0009_competition_writing_audit'),
    ]

    operations = [
        migrations.AddField(
            model_name='musobaqa',
            name='davomiyligi_daq',
            field=models.PositiveIntegerField(default=15),
        ),
        migrations.AddField(
            model_name='musobaqa',
            name='savollar_soni',
            field=models.PositiveIntegerField(default=20),
        ),
        migrations.AddField(
            model_name='musobaqa',
            name='boshlangan_vaqt',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='musobaqa',
            name='yakunlangan_vaqt',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='MusobaqaUrinish',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('savol_idlari', models.JSONField(blank=True, default=list)),
                ('javoblar', models.JSONField(blank=True, default=list)),
                ('togri_soni', models.PositiveIntegerField(default=0)),
                ('jami_soni', models.PositiveIntegerField(default=0)),
                ('foiz', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('sarflangan_soniya', models.PositiveIntegerField(default=0)),
                ('status', models.CharField(choices=[('boshlandi', 'Boshlangan'), ('yakun', 'Yakunlangan')], default='boshlandi', max_length=20)),
                ('boshlangan_vaqt', models.DateTimeField(auto_now_add=True)),
                ('tugagan_vaqt', models.DateTimeField(blank=True, null=True)),
                ('musobaqa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='urinishlar', to='exams.musobaqa')),
                ('oquvchi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='musobaqa_urinishlari', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'musobaqa_urinishlari',
                'ordering': ['-foiz', 'sarflangan_soniya', 'boshlangan_vaqt'],
                'unique_together': {('musobaqa', 'oquvchi')},
                'indexes': [
                    models.Index(fields=['musobaqa', 'status'], name='mus_urinish_status_idx'),
                    models.Index(fields=['oquvchi', '-boshlangan_vaqt'], name='mus_urinish_user_idx'),
                ],
            },
        ),
    ]
