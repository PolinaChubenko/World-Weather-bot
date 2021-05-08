import psycopg2
from queries import get_from_env

DATABASE_URL = get_from_env('DATABASE_URL')


def create_db():
    connection = None
    try:
        connection = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = connection.cursor()
        cursor.execute("""DROP DATABASE IF EXISTS chats_db""")
        creation = """CREATE TABLE chats_db (id SERIAL PRIMARY KEY, chat_id INTEGER, mode TEXT)"""
        cursor.execute(creation)
        cursor.close()
    except psycopg2.DatabaseError:
        pass
    finally:
        if connection is not None:
            connection.close()


def db_add_value(chat_id):
    connection = None
    try:
        connection = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = connection.cursor()
        cursor.execute("""SELECT COUNT(*) FROM chats_db WHERE chat_id = %s""", (chat_id,))
        exists = cursor.fetchone()
        if exists == (0,):
            cursor.execute("""INSERT INTO chats_db(chat_id, mode) VALUES(%s, %s)""", (chat_id, ''))
        cursor.close()
        connection.commit()
    except psycopg2.DatabaseError:
        connection.rollback()
    finally:
        if connection is not None:
            connection.close()


def db_change_value(chat_id, mode):
    connection = None
    try:
        connection = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = connection.cursor()
        cursor.execute("""UPDATE chats_db SET mode = %s WHERE chat_id = %s""", (mode, chat_id))
        cursor.close()
        connection.commit()
    except psycopg2.DatabaseError:
        connection.rollback()
    finally:
        if connection is not None:
            connection.close()


def db_get_value(chat_id):
    connection = None
    response = ''
    try:
        connection = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = connection.cursor()
        cursor.execute("""SELECT mode FROM chats_db WHERE chat_id = %s""", (chat_id,))
        mode = cursor.fetchone()
        response = mode[0]
        cursor.close()
        connection.commit()
    except psycopg2.DatabaseError:
        connection.rollback()
    finally:
        if connection is not None:
            connection.close()
        return response
