from django.db.models import Manager, Model, CharField, PositiveIntegerField, DecimalField, ForeignKey, DateTimeField, CASCADE
from trader_bot.apps.user.models import TelegramUser
from trader_bot.apps.trade.models import Trade


class GetOrNoneManager(Manager):

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class Service(Model):
    objects = GetOrNoneManager()

    currency = CharField(max_length=255, unique=True)
    last_block = PositiveIntegerField()


class CashFlowStatement(Model):
    user = ForeignKey(TelegramUser, on_delete=CASCADE)
    trade = ForeignKey(Trade, null=True, on_delete=CASCADE)
    type_operation = CharField(max_length=255)
    amount = DecimalField(max_digits=40, decimal_places=0, default=0)
    tx_fee = DecimalField(max_digits=40, decimal_places=0, default=0)
    currency = CharField(max_length=255)
    fee_currency = CharField(max_length=255, null=True)
    tx_hash = CharField(max_length=255, null=True)
    created_at = DateTimeField(auto_now_add=True)
