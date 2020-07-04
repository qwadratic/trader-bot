# Generated by Django 3.0.5 on 2020-06-23 20:54

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_auto_20200618_0633'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='mirror',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='order_id',
            field=models.UUIDField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='temporder',
            name='order_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_currency',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='order',
            name='requisites',
            field=models.CharField(max_length=255),
        ),
    ]