# Generated by Django 3.0.5 on 2020-11-23 22:35

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0026_remove_orderholdmoney_fee'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
