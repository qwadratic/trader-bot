from bot_tools.config import get_db_settings


settings = get_db_settings()


db_conn = {
    'host': settings['DB_HOST'],
    'user': settings['DB_USER'],
    'database': settings['DB_NAME'],
    'password': settings['DB_PASS'],
    'autorollback': True,
}