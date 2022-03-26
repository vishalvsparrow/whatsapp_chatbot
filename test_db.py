# test.py

import db
import datetime
import random
import json
conn = db.create_connection('whatsapp_chatbot.db')

whatsapp_number = int('88800088')
text = "Hello there. I am glad to connect with your bot! %d" % (random.randint(0,50))

def test_user_count():

	result = db.get_user_count(conn, whatsapp_number)
	if result == 0:
		db.create_user(conn, whatsapp_number)
	else:
		db.increment_user_count(conn, whatsapp_number)

def test_response_time(conn, whatsapp_number):
	response_time = db.get_last_response_time(conn, whatsapp_number)
	print(response_time, 'response_time')
	message_time = db.get_last_message_time(conn, whatsapp_number)
	print(message_time, 'message_time')
	last_message = db.get_last_message(conn, whatsapp_number)
	print(last_message, 'last_message')	
	last_response = db.get_last_response(conn, whatsapp_number)
	print(last_response, 'last_response')

def test_message(conn, id, number, time=None):
	print('In test_message()')
	if time is not None:
		result = db.insert_message(conn, id, number, time)
	else:
		result = db.insert_message(conn, id, number)
	print(result)

def test_response(conn, text, number, time=None):
	print('In test_response()')
	if time is not None:
		result = db.insert_response(conn, text, number, time)
	else:
		result = db.insert_response(conn, text, number)
	print(result)

def test_message_order(conn, message_id=None, message_type_id=None):
	result = db.get_message_order(conn, message_id, message_type_id)
	print(result)

def test_user_state(conn, whatsapp_number, message_id=None):
	res = db.get_user_state_message_array(conn, whatsapp_number)
	if res is not None:
		res = res.split(',')
	
		if '' in res:
			res.remove('')
	
	print(res)
	print(res=='')

	db.update_user_state_message_array(conn, whatsapp_number, message_id)

#test_message(conn, 222, whatsapp_number, (datetime.datetime.now() - datetime.timedelta(days=random.randint(0,100))).strftime('%Y-%m-%d %H:%M:%S'))

# test_response(conn, text, whatsapp_number,
#  #(datetime.datetime.now() - datetime.timedelta(days=random.randint(0,100))).strftime('%Y-%m-%d %H:%M:%S')
#  )


#test_response_time(conn, whatsapp_number)

#test_message_order(conn, message_id = 12, message_type_id=40000)
#db.create_user(conn, whatsapp_number)
#db.reset_user_state(conn, whatsapp_number)
test_user_state(conn, whatsapp_number, 12)
#db.reset_user_state(conn, whatsapp_number)

#db.add_user_name(conn, whatsapp_number, 'Lee')
