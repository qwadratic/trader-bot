# Generated by Django 3.0.5 on 2020-06-16 01:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20200616_0441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpurse',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requisite', to='user.TelegramUser'),
        ),
    ]
