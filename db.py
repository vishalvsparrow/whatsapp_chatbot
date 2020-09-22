import sqlite3
from sqlite3 import Error

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

def select_rows(conn, whatsapp_number):

	sql_select = "SELECT count from users WHERE whatsapp_number = ?"

	cur = conn.cursor()

	cur.execute(sql_select, (whatsapp_number,))

	rows = cur.fetchall()
	print(rows, "rows")
	if not rows:
		rows = 0
	else:
		rows = rows[0][0]

	print(rows)

	return rows

def insert_rows(conn, whatsapp_number, count):

	sql_update = "UPDATE users SET count = ? WHERE whatsapp_number = ?"
	
	cur = conn.cursor()

	cur.execute(sql_update, (count+1, whatsapp_number,))
	conn.commit()

def create_row(conn, whatsapp_number, count):

	sql_create = "INSERT INTO users(whatsapp_number, count) VALUES(?, ?)"
	
	cur = conn.cursor()

	cur.execute(sql_create, (whatsapp_number,count,))
	conn.commit()

if __name__ == '__main__':

	database = r"user.db"
	
	conn = create_connection(r"user.db")

	create_table(conn, "CREATE TABLE IF NOT EXISTS users (whatsapp_number text, count integer ); ")