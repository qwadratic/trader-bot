# Generated by Django 3.0.5 on 2020-07-08 23:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0013_auto_20200628_0353'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_currency_rate',
            field=models.DecimalField(decimal_places=0, max_digits=40, null=True),
        ),
    ]
