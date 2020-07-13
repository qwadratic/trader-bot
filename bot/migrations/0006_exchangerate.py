# Generated by Django 3.0.5 on 2020-07-13 00:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0005_auto_20200712_1939'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(max_length=255)),
                ('value', models.DecimalField(decimal_places=0, default=0, max_digits=40)),
                ('source', models.CharField(max_length=255)),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('time',),
            },
        ),
    ]