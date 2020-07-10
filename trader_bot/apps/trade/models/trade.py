from django.contrib.postgres.fields import JSONField
from django.db.models import Model, ForeignKey, CharField, BooleanField, DecimalField, DateTimeField, CASCADE

from django.utils import timezone
from django.utils.translation import gettext as _

from trader_bot.apps.order.models import Order
from trader_bot.apps.user.models import TelegramUser


class Trade(Model):
    #  TODO временная заглушка на статус
    order = ForeignKey(Order, on_delete=CASCADE)
    user = ForeignKey(TelegramUser, related_name='trade', on_delete=CASCADE)
    status = CharField(max_length=255, null=True)
    payment_currency = CharField(max_length=255)
    amount = DecimalField(max_digits=40, decimal_places=0, default=0)
    price_trade = DecimalField(max_digits=40, decimal_places=0, default=0)
    type_trade = CharField(max_length=255, null=True)
    tx_hash = CharField(max_length=255, null=True)
    created_at = DateTimeField(auto_now_add=True)


class HoldMoney(Model):
    trade = ForeignKey(Trade, on_delete=CASCADE)
    amount = DecimalField(max_digits=40, decimal_places=0, default=0)

