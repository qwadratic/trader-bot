# Generated by Django 3.0.5 on 2020-06-29 17:35

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0012_auto_20200629_2034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegramuser',
            name='cache',
            field=django.contrib.postgres.fields.jsonb.JSONField(verbose_name=dict),
        ),
    ]
