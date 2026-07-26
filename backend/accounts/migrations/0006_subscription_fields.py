from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies=[('accounts','0005_user_token_version')]
    operations=[
      migrations.AddField(model_name='user', name='tarif', field=models.CharField(choices=[('standard','Standard'),('premium','Premium'),('vip','VIP')], default='standard', max_length=20)),
      migrations.AddField(model_name='user', name='tolov_holati', field=models.CharField(choices=[('tolangan',"To\'langan"),('kutilmoqda','Kutilmoqda'),('qarzdor','Qarzdor')], default='kutilmoqda', max_length=20)),
      migrations.AddField(model_name='user', name='obuna_boshlanishi', field=models.DateField(blank=True,null=True)),
      migrations.AddField(model_name='user', name='obuna_tugashi', field=models.DateField(blank=True,null=True)),
    ]
