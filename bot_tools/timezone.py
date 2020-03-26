from datetime import datetime
import pytz


def get_today_ddmmyyyy():
    tz = pytz.timezone('Europe/Kiev')
    now = datetime.now(tz)
    return now
