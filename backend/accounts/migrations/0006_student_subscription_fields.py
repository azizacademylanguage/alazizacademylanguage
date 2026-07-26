from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('accounts', '0005_user_token_version')]

    operations = [
        migrations.AddField(
            model_name='user',
            name='tarif',
            field=models.CharField(blank=True, default='Standart', max_length=80),
        ),
        migrations.AddField(
            model_name='user',
            name='boshlanish_sana',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='tugash_sana',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='tolov_holati',
            field=models.CharField(choices=[('tolangan', "To'langan"), ('qarzdor', 'Qarzdor'), ('kutilmoqda', 'Kutilmoqda')], default='tolangan', max_length=20),
        ),
        migrations.AddField(
            model_name='user',
            name='muddat_bloklash',
            field=models.BooleanField(default=True),
        ),
    ]
