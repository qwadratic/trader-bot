# Generated by Django 3.0.5 on 2020-08-28 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0022_userflag_await_replenishment_for_trade'),
    ]

    operations = [
        migrations.AddField(
            model_name='userflag',
            name='in_trade',
            field=models.BooleanField(default=False),
        ),
    ]
