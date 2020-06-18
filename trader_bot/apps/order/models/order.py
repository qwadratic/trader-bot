from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models import Model, CharField, ForeignKey, CASCADE, DecimalField, DateTimeField, OneToOneField, Manager

from django.utils import timezone
from django.utils.translation import gettext as _

from trader_bot.apps.user.models import TelegramUser

from django.db import IntegrityError


class GetOrNoneManager(Manager):

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class DeleteAndCreateManager(Manager):
    def delete_and_create(self, **kwargs):

        try:
            return self.create(**kwargs)
        except IntegrityError:
            self.get(**kwargs).delete()
            return self.create(**kwargs)


class TempOrder(Model):
    objects = DeleteAndCreateManager()

    user = OneToOneField(TelegramUser, related_name='temp_order', on_delete=CASCADE)
    type_operation = CharField(null=True, max_length=255)
    trade_currency = CharField(null=True, max_length=255)
    amount = DecimalField(max_digits=40, decimal_places=0, null=True)
    currency_rate = DecimalField(max_digits=40, decimal_places=0, null=True)
    payment_currency = ArrayField(CharField(max_length=50), size=10, default=list)
    requisites = JSONField(default=dict)


class Order(Model):
    objects = GetOrNoneManager()

    user = ForeignKey(TelegramUser, related_name='orders', on_delete=CASCADE)
    type_operation = CharField(max_length=255)
    trade_currency = CharField(max_length=255)
    amount = DecimalField(max_digits=40, decimal_places=0)
    currency_rate = DecimalField(max_digits=40, decimal_places=0)
    payment_currency = JSONField(default=dict)
    requisites = JSONField(default=dict)
    created_at = DateTimeField(auto_now_add=True)
    status = CharField(max_length=255)

