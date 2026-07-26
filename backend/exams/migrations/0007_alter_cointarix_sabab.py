from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('exams', '0006_listening_faollik_bildirishnoma_speaking_transcript'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cointarix',
            name='sabab',
            field=models.CharField(
                choices=[
                    ('mashq', 'Mashq yakunlandi'),
                    ('gate_test', 'Gate Test topshirildi'),
                    ('final_test', 'Final Test topshirildi'),
                    ('shop', "Do'kondan xarid"),
                    ('soz_oyini', "So'z o'yini"),
                    ('streak', 'Kunlik faollik bonusi'),
                    ('admin', "Admin tomonidan qo'lda berilgan"),
                ],
                max_length=20,
            ),
        ),
    ]
