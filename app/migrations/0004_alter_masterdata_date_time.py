# Generated by Django 4.2.4 on 2024-03-06 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_masterdata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='masterdata',
            name='date_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
