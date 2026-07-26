from django.db import migrations, models


def unify_existing_values(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    User.objects.all().update(tarif='Yagona')
    User.objects.filter(tolov_holati__in=['qarzdor', 'kutilmoqda', 'tolanmagan']).update(
        tolov_holati='tolanmagan'
    )
    User.objects.exclude(tolov_holati='tolanmagan').update(tolov_holati='tolangan')


class Migration(migrations.Migration):
    dependencies = [('accounts', '0006_student_subscription_fields')]

    operations = [
        migrations.RunPython(unify_existing_values, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='user',
            name='tarif',
            field=models.CharField(blank=True, default='Yagona', max_length=80),
        ),
        migrations.AlterField(
            model_name='user',
            name='tolov_holati',
            field=models.CharField(
                choices=[('tolangan', "To'langan"), ('tolanmagan', "To'lanmagan")],
                default='tolangan',
                max_length=20,
            ),
        ),
    ]
