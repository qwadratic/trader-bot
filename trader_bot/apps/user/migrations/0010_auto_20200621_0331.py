# Generated by Django 3.0.5 on 2020-06-21 00:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_auto_20200620_0407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userflag',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='flags', to='user.TelegramUser'),
        ),
    ]