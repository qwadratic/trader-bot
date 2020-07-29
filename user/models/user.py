from typing import Optional

from django.db.models import Model, IntegerField, CharField, DateTimeField, PositiveIntegerField, ForeignKey, CASCADE, \
    BooleanField, DecimalField, OneToOneField, Manager
from django.contrib.postgres.fields import JSONField

from django.utils.translation import gettext as _, activate

from bot.models import Text


class GetOrNoneManager(Manager):

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None

def _default_telegramuser_cache():
        return {
                'msg': {
                    'trade_menu': None,
                    'wallet_menu': None
                },
                'clipboard': {
                    'currency': None,
                    'requisites': [],
                    'active_trade': None
                }
            }

def _default_telegramuser_cache():
    return {
        'msg': {
            'trade_menu': None,
            'wallet_menu': None,
            'last_temp_order': None
        },
        'clipboard': {
            'currency': None,
            'requisites': [],
            'active_trade': None,
            'deposit_currency': {}
        }
    }


class TelegramUser(Model):
    objects = GetOrNoneManager()

    telegram_id = PositiveIntegerField(_('Telegram user ID'), unique=True)
    username = CharField(_('User name'), max_length=255, null=True)
    first_name = CharField(_('First name'), max_length=255, null=True)
    last_name = CharField(_('Last name'), max_length=255, null=True)
    last_activity = DateTimeField(_('Last activity'), null=True)
    created_at = DateTimeField(_('Registration date'), auto_now_add=True)
    cache = JSONField(default=_default_telegramuser_cache)

    class Meta:
        verbose_name = 'Telegram User'

    def get_text(self, name):
        activate(self.settings.language)
        txt = Text.objects.get(name=name).text
        return txt

    def update_referrer(self, invited_by: Optional['TelegramUser']) -> bool:
        if invited_by is None or self.id == invited_by.id:
            return False
        UserRef.objects.update_or_create(user=self, defaults={'referrer': invited_by})
        return True

    def get_balance(self, currency, cent2unit=False, round=False):
        from bot.helpers.shortcut import to_units, round_currency

        wallet = self.virtual_wallets.get(currency=currency)
        balance = wallet.balance

        hold_money = self.holdMoney.filter(currency=currency)

        if hold_money.count() > 0:

            for hm in hold_money:
                balance -= hm.amount

        if cent2unit:
            balance = to_units(currency, balance)

        if round:
            balance = round_currency(currency, balance)

        return balance


class UserFlag(Model):
    objects = GetOrNoneManager()

    user = OneToOneField(TelegramUser, related_name='flags', on_delete=CASCADE)
    await_requisites_for_order = BooleanField(default=False)
    await_currency_rate = BooleanField(default=False)
    await_requisite_for_order = BooleanField(default=False)
    await_amount_for_order = BooleanField(default=False)
    await_amount_for_trade = BooleanField(default=False)
    await_tx_hash = BooleanField(default=False)
    await_requisites_address = BooleanField(default=False)
    await_requisites_name = BooleanField(default=False)
    edit_requisite = BooleanField(default=False)
    await_replenishment_for_order = BooleanField(default=False)


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

    def get_display_text(self, user):
        if self.name:
            return user.get_text(name='purse-requisite_info_with_name').format(
                name=self.name,
                address=self.address,
                currency=self.currency)

        return user.get_text(name='purse-requisite_info').format(
            address=self.address,
            currency=self.currency)

