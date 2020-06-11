from django.contrib.postgres.fields import JSONField
from django.db.models import Model, ForeignKey, CharField, BooleanField, DecimalField, DateTimeField, CASCADE

from django.utils import timezone
from django.utils.translation import gettext as _

from trader_bot.apps.order.models import Order
from trader_bot.apps.user.models import User


class Trade(Model):
    order = ForeignKey(Order, on_delete=CASCADE)
    user = ForeignKey(User, related_name='trade', on_delete=CASCADE)
    status = CharField(max_length=255)
    payment_currency = CharField(max_length=255)
    amount = DecimalField(max_digits=40, decimal_places=0, default=0)
    deposite = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)


class HoldMoney(Model):
    trade = ForeignKey(Trade, on_delete=CASCADE)
    amount = DecimalField(max_digits=40, decimal_places=0, default=0)

