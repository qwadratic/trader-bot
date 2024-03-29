# Generated by Django 3.0.5 on 2020-06-15 23:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
        ('trade', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(max_length=255, unique=True)),
                ('last_block', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Text',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('text', models.TextField()),
                ('text_ru', models.TextField(null=True)),
                ('text_en', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CashFlowStatement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_operation', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=0, default=0, max_digits=40)),
                ('tx_fee', models.DecimalField(decimal_places=0, default=0, max_digits=40)),
                ('currency', models.CharField(max_length=255)),
                ('fee_currency', models.CharField(max_length=255, null=True)),
                ('tx_hash', models.CharField(max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('trade', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='trade.Trade')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.TelegramUser')),
            ],
        ),
    ]
