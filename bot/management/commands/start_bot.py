from pyrogram import Client

from config.settings import TG_API_ID, TG_API_HASH, TG_API_TOKEN
from constance import config

import logging

from django.conf import settings

from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.schedulers.blocking import BlockingScheduler
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger
# from django_apscheduler.jobstores import DjangoJobStore
# from django_apscheduler.models import DjangoJobExecution


from django.core.management import BaseCommand

from bot.jobs import check_refill_bip, check_refill_eth, update_exchange_rates, check_refill_btc
from bot.jobs.withdrawal import verification_withdrawal_requests

#logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Start telegram client'

    def handle(self, **options):
        app = Client(
            'session_main',
            api_id=TG_API_ID, api_hash=TG_API_HASH, bot_token=TG_API_TOKEN,
            plugins={'root': 'bot/handlers'})

        shed = BackgroundScheduler()
        shed.add_job(check_refill_bip, 'interval', seconds=config.CRON_CHECK_REFILL_BIP_SEC, args=[app])
        shed.add_job(check_refill_eth, 'interval', seconds=config.CRON_CHECK_REFILL_ETH_SEC, args=[app])
        shed.add_job(update_exchange_rates, 'interval', minutes=config.CRON_UPDATE_EXCHANGE_RATES_MIN)
        shed.add_job(check_refill_btc, 'interval', seconds=config.CRON_CHECK_REFILL_BTC_SEC, args=[app])
        shed.add_job(verification_withdrawal_requests, 'interval', seconds=config.CRON_VERIFICATION_WITHDRAWAL_REQUESTS)

        shed.start()

        app.run()

        # scheduler.add_job(
        #     check_refill_bip,
        #     trigger=CronTrigger(second=f'*/{config.CRON_CHECK_REFILL_BIP_SEC}'),
        #     id='check_refill_bip',
        #     max_instances=1,
        #     replace_existing=True
        # )
        # logger.info('Added job "check_refill_bip".')
        #
        # scheduler.add_job(
        #     check_refill_eth,
        #     trigger=CronTrigger(second=f'*/{config.CRON_CHECK_REFILL_ETH_SEC}'),
        #     id='check_refill_eth',
        #     max_instances=1,
        #     replace_existing=True
        # )
        # logger.info('Added job "check_refill_eth".')
        #
        # scheduler.add_job(
        #     check_refill_btc,
        #     trigger=CronTrigger(second=f'*/{config.CRON_CHECK_REFILL_BTC_SEC}'),
        #     id='check_refill_btc',
        #     max_instances=1,
        #     replace_existing=True
        # )
        # logger.info('Added job "check_refill_btc".')
        #
        # scheduler.add_job(
        #     update_exchange_rates,
        #     trigger=CronTrigger(minute=f'*/{config.CRON_UPDATE_EXCHANGE_RATES_SEC}'),
        #     id='update_exchange_rates',
        #     max_instances=1,
        #     replace_existing=True
        # )
        # logger.info('Added job "update_exchange_rates".')
        #
        # scheduler.add_job(
        #     verification_withdrawal_requests,
        #     trigger=CronTrigger(minute=f'*/{config.CRON_VERIFICATION_WITHDRAWAL_REQUESTS}'),
        #     id='verification_withdrawal_requests',
        #     max_instances=1,
        #     replace_existing=True
        # )
        # logger.info('Added job "verification_withdrawal_requests".')
        #
        # try:
        #     logger.info('Starting scheduler...')
        #     # scheduler.start()
        # except KeyboardInterrupt:
        #     logger.info('Stopping scheduler...')
        #     scheduler.shutdown()
        #     logger.info('Scheduler shut down successfully!')