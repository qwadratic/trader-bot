from bot_tools.config import get_db_settings


settings = get_db_settings()

db_conn = {
    'database': settings['DB_NAME'],
    'user': settings['DB_USER'],
    'password': settings['DB_PASS'],
    'host': settings['DB_HOST'],
    'charset': 'utf8mb4'
}