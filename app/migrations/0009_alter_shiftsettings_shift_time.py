# Generated by Django 4.2.4 on 2024-06-01 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_alter_shiftsettings_shift_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shiftsettings',
            name='shift_time',
            field=models.TimeField(),
        ),
    ]
