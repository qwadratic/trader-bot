# Generated by Django 3.0.5 on 2020-07-16 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0006_exchangerate'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_rate_interval', models.PositiveIntegerField(default=20)),
            ],
        ),
    ]