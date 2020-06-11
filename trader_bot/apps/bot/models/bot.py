from django.db.models import Model, CharField, PositiveIntegerField, DecimalField, ForeignKey, DateTimeField, CASCADE
from trader_bot.apps.user.models import User
from trader_bot.apps.trade.models import Trade


class Service(Model):
    currency = CharField(max_length=255, unique=True)
    last_block = PositiveIntegerField()


class CashFlowStatement(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    trade = ForeignKey(Trade, null=True, on_delete=CASCADE)
    type_operation = CharField(max_length=255)
    amount = DecimalField(max_digits=40, decimal_places=0, default=0)
    tx_fee = DecimalField(max_digits=40, decimal_places=0, default=0)
    currency = CharField(max_length=255)
    fee_currency = CharField(max_length=255, null=True)
    tx_hash = CharField(max_length=255, null=True)
    created_at = DateTimeField(auto_now_add=True)
