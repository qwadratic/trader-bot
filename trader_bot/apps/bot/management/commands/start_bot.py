from django.core.management.base import BaseCommand
from pyrogram import Client

from trader_bot.config.settings import TG_API_ID, TG_API_HASH, TG_API_TOKEN


class Command(BaseCommand):
    help = 'Start telegram client'

    def handle(self, **options):
        app = Client(
            'session_main',
            api_id=TG_API_ID, api_hash=TG_API_HASH, bot_token=TG_API_TOKEN,
            plugins={'root': 'k'})
        app.run()
