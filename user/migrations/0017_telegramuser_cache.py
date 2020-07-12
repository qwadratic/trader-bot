# Generated by Django 3.0.5 on 2020-07-12 17:51

import django.contrib.postgres.fields.jsonb
from django.db import migrations
import user.models.user


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0016_remove_telegramuser_cache'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramuser',
            name='cache',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=user.models.user._default_telegramuser_cache),
        ),
    ]