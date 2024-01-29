# Generated by Django 4.2.4 on 2024-01-26 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_parametervalue'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parametervalue',
            name='analog_zero',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='parametervalue',
            name='high_mv',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='parametervalue',
            name='low_mv',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='parametervalue',
            name='lsl',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='parametervalue',
            name='mastering',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='parametervalue',
            name='nominal',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='parametervalue',
            name='probe_no',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='parametervalue',
            name='reference_value',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='parametervalue',
            name='step_no',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='parametervalue',
            name='usl',
            field=models.FloatField(),
        ),
    ]