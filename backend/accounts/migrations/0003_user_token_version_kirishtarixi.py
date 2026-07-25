from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='token_version',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.CreateModel(
            name='KirishTarixi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(blank=True, max_length=150)),
                ('muvaffaqiyatli', models.BooleanField(default=False)),
                ('ip_manzil', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.CharField(blank=True, max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='kirish_tarixi', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Kirish tarixi',
                'verbose_name_plural': 'Kirish tarixi',
                'db_table': 'kirish_tarixi',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='kirishtarixi',
            index=models.Index(fields=['-created_at'], name='kirish_created_idx'),
        ),
        migrations.AddIndex(
            model_name='kirishtarixi',
            index=models.Index(fields=['username', '-created_at'], name='kirish_user_created_idx'),
        ),
    ]
