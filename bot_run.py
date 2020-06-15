from apscheduler.schedulers.background import BackgroundScheduler
from pyrogram import Client
from bot_tools.config import get_token, get_session_name, BOT_CFG
import peeweedbevolve

from jobs.check_refill import check_refill_bip, check_refill_eth
from jobs.ref import job_check_ref
from jobs.spreadsheet import json_get
from model import db


app = Client(session_name=get_session_name(), bot_token=get_token(), config_file=BOT_CFG)

shed = BackgroundScheduler()
shed.add_job(job_check_ref, 'interval', hours=2)
shed.add_job(check_refill_bip, 'interval', seconds=5, args=[app])
shed.add_job(check_refill_eth, 'interval', seconds=10, args=[app])
shed.add_job(json_get, 'interval', hours=24) #update Text data from spreadsheets

shed.start()

if __name__ == "__main__":
    db.evolve(interactive=False, ignore_tables=['basemodel'])
    app.run()




