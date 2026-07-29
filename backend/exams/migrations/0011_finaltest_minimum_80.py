from django.db import migrations, models


def enforce_minimum_80(apps, schema_editor):
    FinalTest = apps.get_model('exams', 'FinalTest')
    FinalTest.objects.filter(otish_bali_foiz__lt=80).update(otish_bali_foiz=80)


class Migration(migrations.Migration):
    dependencies = [
        ('exams', '0010_live_competition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='finaltest',
            name='otish_bali_foiz',
            field=models.PositiveIntegerField(default=80),
        ),
        migrations.RunPython(enforce_minimum_80, migrations.RunPython.noop),
    ]
