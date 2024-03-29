# Generated by Django 3.0.5 on 2020-06-15 23:25

import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TempOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_operation', models.CharField(max_length=255, null=True)),
                ('trade_currency', models.CharField(max_length=255, null=True)),
                ('amount', models.DecimalField(decimal_places=0, max_digits=40, null=True)),
                ('min_limit', models.DecimalField(decimal_places=0, max_digits=40, null=True)),
                ('max_limit', models.DecimalField(decimal_places=0, max_digits=40, null=True)),
                ('currency_rate', models.DecimalField(decimal_places=0, max_digits=40, null=True)),
                ('payment_currency', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), default=list, size=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='temp_order', to='user.TelegramUser')),
            ],
            managers=[
                ('object', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_operation', models.CharField(max_length=255)),
                ('trade_currency', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=0, max_digits=40)),
                ('currency_rate', models.DecimalField(decimal_places=0, max_digits=40)),
                ('payment_currency', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='user.TelegramUser')),
            ],
            managers=[
                ('object', django.db.models.manager.Manager()),
            ],
        ),
    ]
