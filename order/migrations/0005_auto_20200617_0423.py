# Generated by Django 3.0.5 on 2020-06-17 01:23

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_auto_20200616_0637'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='requisites',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='temporder',
            name='requisites',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
    ]
