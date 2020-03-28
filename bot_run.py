from apscheduler.schedulers.background import BackgroundScheduler
from pyrogram import Client
from bot_tools.config import get_token, get_session_name, BOT_CFG
import peeweedbevolve

from jobs.ref import job_check_ref
from model import db


app = Client(session_name=get_session_name(), bot_token=get_token(), config_file=BOT_CFG)

shed = BackgroundScheduler()
shed.add_job(job_check_ref, 'interval', hours=2)

shed.start()

if __name__ == "__main__":
    db.evolve(interactive=False, ignore_tables=['basemodel'])
    app.run()




