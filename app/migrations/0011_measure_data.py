# Generated by Django 4.2.4 on 2024-06-06 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_alter_shiftsettings_shift_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='measure_data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('part_model', models.CharField(max_length=100)),
                ('operator', models.CharField(max_length=100)),
                ('machine', models.CharField(max_length=100)),
                ('shift', models.CharField(max_length=100)),
            ],
        ),
    ]
