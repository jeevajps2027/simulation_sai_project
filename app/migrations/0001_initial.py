# Generated by Django 4.2.4 on 2024-02-05 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='find',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('probe_id', models.CharField(max_length=50, unique=True)),
                ('low_ref', models.JSONField(default=list)),
                ('low_count', models.JSONField(default=list)),
                ('high_ref', models.JSONField(default=list)),
                ('high_count', models.JSONField(default=list)),
                ('coefficent', models.JSONField(default=list)),
            ],
        ),
        migrations.CreateModel(
            name='parameterValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_id', models.CharField(max_length=255)),
                ('parameter_name', models.CharField(max_length=255)),
                ('single_radio', models.BooleanField(default=False)),
                ('analog_zero', models.FloatField(blank=True, null=True)),
                ('reference_value', models.FloatField(blank=True, null=True)),
                ('double_radio', models.BooleanField(default=False)),
                ('high_mv', models.FloatField(blank=True, null=True)),
                ('low_mv', models.FloatField(blank=True, null=True)),
                ('probe_no', models.FloatField()),
                ('measurement_mode', models.CharField(max_length=50)),
                ('nominal', models.FloatField()),
                ('usl', models.FloatField()),
                ('lsl', models.FloatField()),
                ('mastering', models.FloatField()),
                ('step_no', models.FloatField()),
                ('hide_checkbox', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='readings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('probe_id', models.CharField(max_length=50, unique=True)),
                ('low_ref', models.JSONField(default=list)),
                ('low_count', models.JSONField(default=list)),
                ('high_ref', models.JSONField(default=list)),
                ('high_count', models.JSONField(default=list)),
                ('coefficent', models.JSONField(default=list)),
            ],
        ),
        migrations.CreateModel(
            name='TableFiveData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vendor_code', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='TableFourData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operator_no', models.CharField(max_length=100)),
                ('operator_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='TableOneData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('part_name', models.CharField(max_length=100)),
                ('customer_name', models.CharField(max_length=100)),
                ('part_model', models.CharField(max_length=100)),
                ('part_no', models.CharField(max_length=100)),
                ('hide', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='TableThreeData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_no', models.CharField(max_length=100)),
                ('machine_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='TableTwoData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch_no', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='viewvalues',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_id', models.CharField(max_length=255)),
                ('parameter_name', models.CharField(max_length=255)),
            ],
        ),
    ]
