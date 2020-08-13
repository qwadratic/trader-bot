import threading

from pyrogram import Client

from config.settings import TG_API_ID, TG_API_HASH, TG_API_TOKEN

import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from django.core.management import BaseCommand

from bot.jobs import check_refill_bip, check_refill_eth, update_exchange_rates, get_update_exchange_rates_interval
from bot.jobs.withdrawal import verification_withdrawal_requests


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Start telegram client'

    def handle(self, **options):
        app = Client(
            'session_main',
            api_id=TG_API_ID, api_hash=TG_API_HASH, bot_token=TG_API_TOKEN,
            plugins={'root': 'bot/handlers'})

        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            check_refill_bip,
            trigger=CronTrigger(second='*/5'),
            id='check_refill_bip',
            max_instances=1,
            replace_existing=True
        )
        logger.info('Added job "check_refill_bip".')

        scheduler.add_job(
            check_refill_eth,
            trigger=CronTrigger(second='*/20'),
            id='check_refill_eth',
            max_instances=1,
            replace_existing=True
        )
        logger.info('Added job "check_refill_eth".')

        scheduler.add_job(
            update_exchange_rates,
            trigger=CronTrigger(minute=f'*/{get_update_exchange_rates_interval()}'),
            id='update_exchange_rates',
            max_instances=1,
            replace_existing=True
        )
        logger.info('Added job "update_exchange_rates".')

        scheduler.add_job(
            verification_withdrawal_requests,
            trigger=CronTrigger(minute='*/10'),
            id='verification_withdrawal_requests',
            max_instances=1,
            replace_existing=True
        )
        logger.info('Added job "verification_withdrawal_requests".')

        try:
            logger.info('Starting scheduler...')
            scheduler.start()
        except KeyboardInterrupt:
            logger.info('Stopping scheduler...')
            scheduler.shutdown()
            logger.info('Scheduler shut down successfully!')

        scheduler.start()
        app.run()
