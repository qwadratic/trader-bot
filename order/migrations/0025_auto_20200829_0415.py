# Generated by Django 3.0.5 on 2020-08-29 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0024_orderholdmoney_fee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderholdmoney',
            name='fee',
            field=models.DecimalField(decimal_places=0, max_digits=40),
        ),
    ]
