# Generated by Django 3.0.5 on 2020-06-23 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0008_remove_order_order_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_id',
            field=models.UUIDField(default=None),
        ),
    ]
