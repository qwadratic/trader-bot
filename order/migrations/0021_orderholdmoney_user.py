# Generated by Django 3.0.5 on 2020-07-27 00:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0018_remove_userflag_requisites_for_trade'),
        ('order', '0020_auto_20200724_0630'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderholdmoney',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='HoldMoney', to='user.TelegramUser'),
        ),
    ]
