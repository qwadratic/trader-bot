# Generated by Django 3.0.5 on 2020-07-18 01:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0008_auto_20200711_0443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='status',
            field=models.CharField(default='open', max_length=255),
        ),
    ]