from django.contrib.postgres.fields import JSONField
from django.db.models import Model, CharField, ForeignKey, CASCADE, DecimalField, DateTimeField, OneToOneField, Manager

from django.utils import timezone
from django.utils.translation import gettext as _

from trader_bot.apps.user.models import TelegramUser


class GetOrNoneManager(Manager):

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class TempOrder(Model):
    user = OneToOneField(TelegramUser, related_name='temporder', on_delete=CASCADE)
    type_operation = CharField(null=True, max_length=255)
    trade_currency = CharField(null=True, max_length=255)
    amount = DecimalField(max_digits=40, decimal_places=0, null=True)
    min_limit = DecimalField(max_digits=40, decimal_places=0, null=True)
    max_limit = DecimalField(max_digits=40, decimal_places=0, null=True)
    currency_rate = DecimalField(max_digits=40, decimal_places=0, null=True)
    payment_currency = JSONField(null=True, default=dict)


class Order(Model):
    object = GetOrNoneManager()

    user = ForeignKey(TelegramUser, related_name='orders', on_delete=CASCADE)
    type_operation = CharField(max_length=255)
    trade_currency = CharField(max_length=255)
    amount = DecimalField(max_digits=40, decimal_places=0)
    currency_rate = DecimalField(max_digits=40, decimal_places=0)
    payment_currency = JSONField(default=dict)
    created_at = DateTimeField(auto_now_add=True)
    status = CharField(max_length=255)

