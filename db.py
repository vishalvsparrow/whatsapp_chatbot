import sqlite3
from sqlite3 import Error
import datetime

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def get_user_count(conn, whatsapp_number):

	sql_select = "SELECT message_count from users WHERE whatsapp_number = ?"
	cur = conn.cursor()
	cur.execute(sql_select, (whatsapp_number,))

	rows = cur.fetchall()
	#print(rows, "rows")
	if not rows:
		rows = 0
	else:
		rows = rows[0][0]

	return rows

def add_user_name(conn, whatsapp_number, name):
	sql_update = "UPDATE users SET name = name WHERE whatsapp_number = ?"
	cur = conn.cursor()

	cur.execute(sql_update, (whatsapp_number,))
	conn.commit()

def increment_user_count(conn, whatsapp_number):

	sql_update = "UPDATE users SET message_count = message_count+1 WHERE whatsapp_number = ?"	
	cur = conn.cursor()

	cur.execute(sql_update, (whatsapp_number,))
	conn.commit()

# Initialize a user with default message count = 1 and create a blank state 
def create_user(conn, whatsapp_number, message_count=1):
	try:
		sql_insert = "INSERT OR IGNORE INTO users(whatsapp_number, message_count) VALUES(?, ?)"
		sql_insert_state = "INSERT OR IGNORE INTO user_state(whatsapp_number) VALUES (?)"
	except e:
		print(e)
	cur = conn.cursor()

	cur.execute(sql_insert, (whatsapp_number,message_count,))
	cur.execute(sql_insert_state, (whatsapp_number,))
	conn.commit()

def reset_user_state(conn, whatsapp_number):
	sql = "UPDATE user_state SET message_id_array = '', message_type_id_array = '' where whatsapp_number = ?"
	cur = conn.cursor()
	cur.execute(sql, (whatsapp_number,))
	conn.commit()

def get_user_state_message_array(conn, whatsapp_number):
	sql = "SELECT message_id_array FROM user_state WHERE whatsapp_number = ?"
	cur = conn.cursor()
	cur.execute(sql, (whatsapp_number,))
	rows = cur.fetchall()

	if not rows:
		rows = None
	else:
		rows = rows[0][0]

	return rows

def get_user_state_message_type_array(conn, whatsapp_number):
	sql = "SELECT message_type_id_array FROM user_state WHERE whatsapp_number = ?"
	cur = conn.cursor()
	cur.execute(sql, (whatsapp_number,))
	rows = cur.fetchall()

	if not rows:
		rows = None
	else:
		rows = rows[0][0]

	return rows

def update_user_state_message_array(conn, whatsapp_number, message_id, modified_date=None):
	if modified_date is None:
		modified_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	message_id = str(message_id)
	message_id = ','+message_id

	sql_insert = "INSERT OR IGNORE INTO user_state(whatsapp_number, message_id_array) VALUES (?, ?)"

	sql = "UPDATE user_state SET message_id_array = message_id_array || ?, modified_date = ? WHERE whatsapp_number = ?"
	cur = conn.cursor()
	cur.execute(sql, (message_id, modified_date, whatsapp_number,))
	cur.execute(sql_insert, (whatsapp_number, message_id, ))
	conn.commit()

def update_user_state_message_type_array(conn, whatsapp_number, message_type_id):
	message_type_id = str(message_type_id)
	message_type_id = ','+message_type_id

	sql_insert = "INSERT OR IGNORE INTO user_state(whatsapp_number, message_type_id_array) VALUES (?, ?)"

	sql = "UPDATE user_state SET message_type_id_array = message_type_id_array || ? WHERE whatsapp_number = ?"
	cur = conn.cursor()
	cur.execute(sql, (message_type_id, whatsapp_number,))
	cur.execute(sql_insert, (whatsapp_number,message_type_id, ))
	conn.commit()

#def update_user_state(conn, whatsapp_number, message_id)

# get message rank by message_id, message_type_id (AKA module) 
def get_message_order(conn, message_id, message_type_id=None):
	cur = conn.cursor()
	#print(message_id, message_type_id)
	if message_type_id is None:
		query = "SELECT rank FROM message_order WHERE message_id = ?"
		cur.execute(query, (message_id,))
	elif message_type_id is not None:
		query = "SELECT rank FROM message_order WHERE message_id = ? AND message_type_id = ?"
		cur.execute(query, (message_id, message_type_id))

	rows = cur.fetchall()

	if not rows:
		rows = None
	else:
		rows = rows[0][0]

	return rows

# get message text by id

def get_message_text(conn, message_id):
	cur = conn.cursor()
	query = "SELECT DISTINCT message_text FROM messages WHERE message_id = ?"
	cur.execute(query, (message_id,))
	rows = cur.fetchall()
	if not rows:
		rows = None
	else:
		rows = rows[0][0]
	return rows


def get_last_response_time(conn, whatsapp_number):
	
	cur = conn.cursor()
	query = "SELECT MAX(response_datetime) FROM response_received WHERE whatsapp_number = ?"

	cur.execute(query, (whatsapp_number,)) 
	rows = cur.fetchall()

	if not rows:
		rows = None
	else:
		rows = rows[0][0] 

	return rows

def get_last_response(conn, whatsapp_number):
	#last_message_time = get_last_message_time(conn, whatsapp_number)
	cur = conn.cursor()
	query = "SELECT a.response_text FROM response_received a INNER JOIN (SELECT whatsapp_number, MAX(response_datetime) AS max_response_datetime FROM response_received WHERE whatsapp_number = ? GROUP BY whatsapp_number) b ON a.response_datetime = b.max_response_datetime AND a.whatsapp_number = b.whatsapp_number"
	cur.execute(query, (whatsapp_number,))
	rows = cur.fetchall()
	if not rows:
		rows = None
	else:
		rows = rows[0][0]
	return rows

def get_last_message_time(conn, whatsapp_number):
	
	cur = conn.cursor()
	query = "SELECT MAX(message_datetime) FROM message_sent WHERE whatsapp_number = ?"

	cur.execute(query, (whatsapp_number,)) 
	rows = cur.fetchall()
	#print(rows)
	if not rows:
		rows = None
	else:
		rows = rows[0][0] 

	return rows

def get_last_message(conn, whatsapp_number):
	#last_message_time = get_last_message_time(conn, whatsapp_number)
	cur = conn.cursor()
	query = "SELECT c.message_text FROM message_sent a INNER JOIN (SELECT whatsapp_number, MAX(message_datetime) AS max_message_datetime FROM message_sent WHERE whatsapp_number = ? GROUP BY whatsapp_number) b ON a.message_datetime = b.max_message_datetime AND a.whatsapp_number = b.whatsapp_number INNER JOIN (SELECT DISTINCT id, message_text FROM messages) c ON a.message_id = c.id"
	cur.execute(query, (whatsapp_number,))
	rows = cur.fetchall()
	if not rows:
		rows = None
	else:
		rows = rows[0][0]
	return rows

def insert_message(conn, message_id, whatsapp_number, message_datetime = None):
	cur = conn.cursor()

	if message_datetime is None:
		query = "INSERT INTO message_sent(message_id, whatsapp_number) VALUES(?, ?)"
		cur.execute(query, (message_id, whatsapp_number,))
	elif message_datetime is not None:
		query = "INSERT INTO message_sent(message_datetime, message_id, whatsapp_number) VALUES(?, ?, ?)"
		cur.execute(query, (message_datetime, message_id, whatsapp_number,))

	conn.commit()

def insert_response(conn, response_text, whatsapp_number, response_datetime = None):
	cur = conn.cursor()

	if response_datetime is None:
		query = "INSERT INTO response_received(response_text, whatsapp_number) VALUES(?, ?)"
		cur.execute(query, (response_text, whatsapp_number,))
	elif response_datetime is not None:
		query = "INSERT INTO response_received(response_datetime, response_text, whatsapp_number) VALUES(?, ?, ?)"
		cur.execute(query, (response_datetime, response_text, whatsapp_number,))

	conn.commit()


if __name__ == '__main__':

	database = r"whatsapp_chatbot.db"
	
	conn = create_connection(database)

	create_table(conn, "CREATE TABLE IF NOT EXISTS users (whatsapp_number integer PRIMARY KEY, name TEXT, message_count INTEGER ); ")
	create_table(conn, "CREATE TABLE IF NOT EXISTS messages (ID INTEGER PRIMARY KEY AUTOINCREMENT, message_text TEXT, message_type_id INTEGER ); ")
	create_table(conn, "CREATE TABLE IF NOT EXISTS message_type (ID INTEGER PRIMARY KEY AUTOINCREMENT, message_type_description TEXT); ")
	create_table(conn, "CREATE TABLE IF NOT EXISTS message_sent (ID INTEGER PRIMARY KEY AUTOINCREMENT, message_datetime DATETIME NOT NULL DEFAULT (DATETIME(CURRENT_TIMESTAMP)), whatsapp_number TEXT, message_id INTEGER); ")	
	create_table(conn, "CREATE TABLE IF NOT EXISTS response_received (ID INTEGER PRIMARY KEY AUTOINCREMENT, response_datetime DATETIME NOT NULL DEFAULT (DATETIME(CURRENT_TIMESTAMP)), whatsapp_number TEXT, response_text TEXT); ")	
	create_table(conn, "CREATE TABLE IF NOT EXISTS user_state (whatsapp_number INTEGER PRIMARY KEY AUTOINCREMENT, message_type_id_array TEXT DEFAULT '', message_id_array TEXT DEFAULT '', modified_date DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP))); ")
	create_table(conn, "CREATE TABLE IF NOT EXISTS message_order (message_id INTEGER, message_type_id INTEGER, rank INTEGER, PRIMARY KEY (message_id, message_type_id), FOREIGN KEY(message_id) REFERENCES messages(ID), FOREIGN KEY(message_type_id) REFERENCES message_type(ID)); ")


