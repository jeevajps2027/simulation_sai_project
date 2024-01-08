# Generated by Django 4.2.4 on 2024-01-01 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='baTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch_no', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='maTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_no', models.CharField(max_length=100)),
                ('machine_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='opTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operator_no', models.CharField(max_length=100)),
                ('operator_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='paTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('part_name', models.CharField(max_length=100)),
                ('customer_name', models.CharField(max_length=100)),
                ('part_model', models.CharField(max_length=100)),
                ('part_no', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='veTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vendor_code', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
    ]
