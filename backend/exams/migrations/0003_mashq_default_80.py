from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('exams', '0002_shopmahsulot_adminamallog_cointarix_finaltest_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mashq',
            name='otish_bali_foiz',
            field=models.PositiveIntegerField(default=80),
        ),
    ]
