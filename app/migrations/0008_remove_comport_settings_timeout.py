# Generated by Django 4.2.4 on 2024-04-12 11:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_alter_comport_settings_timeout'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comport_settings',
            name='timeout',
        ),
    ]