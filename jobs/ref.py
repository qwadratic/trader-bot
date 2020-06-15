from model import UserRef
import datetime as dt


def job_check_ref():
    (UserRef
     .delete()
     .where(dt.datetime.utcnow() - UserRef.ref_created_at > dt.timedelta(30))
     .execute())

