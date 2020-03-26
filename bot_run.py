from pyrogram import Client
from bot_tools.config import get_token, get_session_name, BOT_CFG
import peeweedbevolve
from models.db_models import db


app = Client(session_name=get_session_name(), bot_token=get_token(), config_file=BOT_CFG)


if __name__ == "__main__":
    peeweedbevolve.evolve(db, interactive=False, ignore_tables=['basemodel'])
    app.run()




