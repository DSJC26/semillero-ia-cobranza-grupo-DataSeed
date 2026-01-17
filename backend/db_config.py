import pymysql

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456",
    "database": "chat_ds",
    "port": 3306,
    "cursorclass": pymysql.cursors.DictCursor,
}

'''''def get_connection():
    return pymysql.connect(**DB_CONFIG)'''
def get_connection():
    raise Exception("BD real aún no configurada")
