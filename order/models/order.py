import uuid

from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models import Model, CharField, ForeignKey, CASCADE, DecimalField, DateTimeField, OneToOneField,\
    BooleanField, Manager, UUIDField
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
            self.get(user=kwargs['user']).delete()
            return self.create(**kwargs)


class TempOrder(Model):
    objects = DeleteAndCreateManager()

    user = OneToOneField('user.TelegramUser', related_name='temp_order', on_delete=CASCADE)
    type_operation = CharField(null=True, max_length=255)
    trade_currency = CharField(null=True, max_length=255)
    amount = DecimalField(max_digits=40, decimal_places=0, null=True)
    currency_rate = DecimalField(max_digits=40, decimal_places=0, null=True)
    payment_currency_rate = JSONField(default=dict)
    payment_currency = ArrayField(CharField(max_length=50), size=10, default=list)
    requisites = JSONField(default=dict)
    status = CharField(max_length=255, default='close')


class ParentOrder(Model):
    order_id = UUIDField(default=uuid.uuid4)
    user = ForeignKey('user.TelegramUser', related_name='parentOrders', on_delete=CASCADE)
    type_operation = CharField(null=True, max_length=255)
    trade_currency = CharField(null=True, max_length=255)
    amount = DecimalField(max_digits=40, decimal_places=0)
    currency_rate = DecimalField(max_digits=40, decimal_places=0, null=True)
    payment_currency = ArrayField(CharField(max_length=50), size=10, default=list)
    payment_currency_rate = JSONField(default=dict)
    requisites = JSONField(default=dict)
    status = CharField(max_length=255, default='open')
    created_at = DateTimeField(auto_now_add=True)


class Order(Model):
    objects = GetOrNoneManager()

    parent_order = ForeignKey('order.ParentOrder', related_name='orders', on_delete=CASCADE)
    type_operation = CharField(max_length=255)
    trade_currency = CharField(max_length=255)
    amount = DecimalField(max_digits=40, decimal_places=0)
    currency_rate = DecimalField(max_digits=40, decimal_places=0)
    payment_currency = CharField(max_length=255)
    requisites = CharField(max_length=255)
    status = CharField(max_length=255, default='open')
    mirror = BooleanField(default=False)


class OrderHoldMoney(Model):
    order = ForeignKey('order.ParentOrder', related_name='holdMoney', on_delete=CASCADE)
    user = ForeignKey('user.TelegramUser', related_name='holdMoney', on_delete=CASCADE)
    currency = CharField(max_length=255)
    amount = DecimalField(max_digits=40, decimal_places=0)
