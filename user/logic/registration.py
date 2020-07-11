from typing import Optional

from pyrogram import User

from user.logic.core import create_wallets_for_user
from user.models import TelegramUser, UserMsg, UserFlag, UserSettings


def register_user(tg_user: User, auto_language: str = None, auto_currency: str = None) -> Optional[TelegramUser]:
    """
    Регистрирует юзера или возвращает None, если такой уже есть
    При регистрации для юзера создаются настройки, кошельки и служебные флаги

    Можно передать язык/валюту (используется при регистрации по рефке на ордер, чтобы юзер мог сразу торговать)
    """
    user, is_created = TelegramUser.objects.get_or_create(
        telegram_id=tg_user.id,
        defaults={
            'username': tg_user.username,
            'first_name': tg_user.first_name,
            'last_name': tg_user.last_name
        })
    not_empty_settings = {
        field: value for field, value in [
            ('user', user),
            ('language', auto_language),
            ('currency', auto_currency)
        ] if value is not None
    }
    if is_created:
        UserMsg.objects.create(user=user)
        UserFlag.objects.create(user=user)
        UserSettings.objects.create(**not_empty_settings)
        create_wallets_for_user(user)

    return user if is_created else None
