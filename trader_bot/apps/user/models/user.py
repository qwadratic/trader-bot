from django.db.models import Model, IntegerField, CharField, DateTimeField, PositiveIntegerField, ForeignKey, CASCADE, \
    BooleanField, DecimalField, OneToOneField, Manager
from django.contrib.postgres.fields import JSONField

from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.translation import gettext as _, activate

from trader_bot.apps.bot.models.text import Text


class GetOrNoneManager(Manager):

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class TelegramUser(Model):
    objects = GetOrNoneManager()

    telegram_id = PositiveIntegerField(_('Telegram user ID'), unique=True)
    username = CharField(_('User name'), max_length=255, null=True)
    first_name = CharField(_('First name'), max_length=255,null=True)
    last_name = CharField(_('Last name'), max_length=255, null=True)
    last_activity = DateTimeField(_('Last activity'), null=True)
    created_at = DateTimeField(_('Registration date'), auto_now_add=True)
    cache = JSONField(default=dict(
        msg=dict(
            trade_menu=None,
            wallet_menu=None
        ),
        clipboard=dict(
            currency=None,
            requisites=list,
            active_trade=None
        )
    ))

    class Meta:
        verbose_name = 'Telegram User'

    def get_text(self, name):
        activate(self.settings.language)
        txt = Text.objects.get(name=name).text
        return txt


class UserFlag(Model):
    objects = GetOrNoneManager()

    user = OneToOneField(TelegramUser, related_name='flags', on_delete=CASCADE)
    await_requisites_for_order = BooleanField(default=False)
    await_currency_rate = BooleanField(default=False)
    await_requisite_for_order = BooleanField(default=False)
    await_amount_for_order = BooleanField(default=False)

    temp_currency = CharField(null=True, max_length=255)
    requisites_for_trade = BooleanField(default=False)
    requisites_for_start_deal = BooleanField(default=False)
    await_amount_for_trade = BooleanField(default=False)
    await_currency_value = BooleanField(default=False)
    await_amount_for_deal = BooleanField(default=False)
    await_requisites_address = BooleanField(default=False)
    await_requisites_name = BooleanField(default=False)
    edit_requisite = BooleanField(default=False)


class UserSettings(Model):
    user = OneToOneField(TelegramUser, related_name='settings', on_delete=CASCADE)
    language = CharField(default='ru', max_length=255)
    currency = CharField(default='USD', max_length=255)
    announcement_id = PositiveIntegerField(null=True)
    active_deal = IntegerField(null=True)


class UserRef(Model):
    user = OneToOneField(TelegramUser, related_name='ref', on_delete=CASCADE)
    referrer = ForeignKey(TelegramUser, on_delete=CASCADE)
    ref_created_at = DateTimeField(auto_now_add=True)


class UserMsg(Model):
    user = OneToOneField(TelegramUser, related_name='msg', on_delete=CASCADE)
    trade_menu = PositiveIntegerField(null=True)
    wallet_menu = PositiveIntegerField(null=True)


class Wallet(Model):
    user = ForeignKey(TelegramUser, related_name='wallets', on_delete=CASCADE)
    currency = CharField(max_length=255)
    address = CharField(max_length=255)
    mnemonic = CharField(max_length=255, null=True)
    private_key = CharField(max_length=255)


class VirtualWallet(Model):
    user = ForeignKey(TelegramUser, related_name='virtual_wallets', on_delete=CASCADE)
    currency = CharField(max_length=255)
    balance = DecimalField(max_digits=40, decimal_places=0, default=0)


class UserPurse(Model):
    objects = GetOrNoneManager()

    user = ForeignKey(TelegramUser, related_name='requisites', on_delete=CASCADE)
    name = CharField(max_length=255, null=True)
    currency = CharField(max_length=255)
    address = CharField(max_length=255, null=True)
    status = CharField(max_length=255, default='invalid')



