# Generated by Django 4.2.4 on 2024-05-23 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_measurementdata_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='measurementdata',
            name='date',
            field=models.CharField(max_length=100),
        ),
    ]