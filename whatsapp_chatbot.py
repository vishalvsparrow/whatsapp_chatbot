# now: datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import requests
from PIL import Image, ImageDraw
from io import BytesIO
import db
import sqlite3
import math
import json

app = Flask(__name__)

@app.route("/")
def hello():
	return "Hello World!"

def get_message_text(message_type_id, message_id, user_name=None, file=None):
	if file is None:
		file = 'messages.json'
	message_text = None
	with open(file) as f:
		data = json.load(f)
	for m in data[0]['messages']:
		if m['message_type'] == str(message_type_id) and m['message_id'] == str(message_id):
			message_text = m['text']
	if user_name is not None:
		return 'Hey {}! \n'.format(user_name) + message_text
	else:
		return message_text

def get_end_message_id(message_type_id, file=None):
	if file is None:
		file = 'messages.json'
	with open(file) as f:
		data = json.load(f)
	a = []
	for m in data[0]['messages']:
		if m['message_type'] == str(message_type_id):
			a.append(int(m['message_id']))
	return(max(a))

def check_valid_user_name(response):
	return not (any(map(response.lower().__contains__, ['?', 'hi', 'hello', 'what', 'repeat', 'why', 'none'])) or response.lower() == 'no')

def check_word_in_response(response, words = []):
	return any(map(response.lower().__contains__, words))

def check_help_response(response, help_words = ['help', 'how to use this']):
	return any(map(response.lower().__contains__, help_words))

def check_repeat_response(response, repeat_words = ['repeat', 'huh', 'say that again']):
	return any(map(response.lower().__contains__, repeat_words))

def check_feedback_response(response, feedback_words = ['feedback', 'suggestion']):
	return any(map(response.lower().__contains__, feedback_words))

@app.route("/chat", methods = ['POST', 'PUT'])
def chat():
	
	conn = db.create_connection("whatsapp_chatbot.db")
	resp = MessagingResponse()

	next_word_list = ['more', 'next', 'yes', 'go on']

	# get user's phone number and set it as the key for our new user
	if not request.form.get('From'):
		return 'No phone number found'
	else:
		whatsapp_number = request.form.get('From').split(':+')[1]	
	
	db.create_user(conn, whatsapp_number)

	#db.reset_user_state(conn, whatsapp_number)

	# get the user response and store it in response_received
	response = request.form.get('Body')
	db.insert_response(conn, response, whatsapp_number)

	# get the last message id and type we sent to the user from user_state
	last_message_dict = db.get_last_message_dict(conn, whatsapp_number)	

	# get the actual last message id and type we sent to the user
	helper_message_dict = db.get_helper_message_dict(conn, whatsapp_number)

	user_name = None
	# get user_name if exists
	user_name = db.get_user_name(conn, whatsapp_number)
	print(helper_message_dict, 'helper dict')

	print(last_message_dict, '<----- last message')
	print(last_message_dict['message_type_id'])

	# if this is user's first message
	if not last_message_dict or last_message_dict['message_type_id'] is None or last_message_dict['message_id'] is None:
		# send the first intro message to the user
		message_id = 1
		message_type_id = 2
		# update the message sent to user
		db.insert_message(conn, message_id, message_type_id, whatsapp_number)
		# send the message
		resp.message(get_message_text(message_type_id, message_id))
		return str(resp)

	# if the user asked for help
	if check_help_response(response):
		message_id = 0
		message_type_id = 0
		db.insert_message(conn, message_id, message_type_id, whatsapp_number)
		# send the message
		resp.message(get_message_text(message_type_id, message_id))
		return str(resp)	

	# if the user gave a feedback
	if check_help_response(response):
		message_id = 0
		message_type_id = 4
		#db.insert_message(conn, message_id, message_type_id, whatsapp_number)
		# send the message
		resp.message(get_message_text(message_type_id, message_id))
		return str(resp)

	# if the user asked to repeat the last message
	if check_repeat_response(response):
		message_id = last_message_dict['message_id']
		message_type_id = last_message_dict['message_type_id']
		#db.insert_message(conn, message_id, message_type_id, whatsapp_number)
		# send the message
		resp.message(get_message_text(message_type_id, message_id))
		return str(resp)

	# if the last message was of share identity type
	if last_message_dict['message_type_id'] == '4':

		# if we asked the user's name again
		if last_message_dict['message_id'] == '2':
			print(response, '<--- user_name??')
			if check_valid_user_name(response):

				# record the user name
				user_name = response.strip()
				# update user name in the users table
				db.add_user_name(conn, whatsapp_number, user_name)
				# send the second intro message to the user
				message_id = 2
				message_type_id = 2
				resp.message(get_message_text(message_type_id, message_id, user_name))
				return str(resp)
			else:
				print(response, '<--- not a valid user name')
				# Ask user's name again
				message_id = 2
				message_type_id = 4
				db.insert_message(conn, message_id, message_type_id, whatsapp_number)
				resp.message(get_message_text(message_type_id, message_id))
				return str(resp)

	# if the last message was of intro type
	if last_message_dict['message_type_id'] == '2':
		# if we sent the first intro message to the user
		if last_message_dict['message_id'] == '1':

			# if the user refused to give us their name
			if not check_valid_user_name(response):
				print(response, '<--- not a valid user name')
				# Ask user's name again
				message_id = 2
				message_type_id = 4
				db.insert_message(conn, message_id, message_type_id, whatsapp_number)
				resp.message(get_message_text(message_type_id, message_id))
				return str(resp)

			# record the user name
			user_name = response.strip()
			# update user name in the users table
			db.add_user_name(conn, whatsapp_number, user_name)

			# send the second intro message to the user
			message_id = 2
			message_type_id = 2
			db.insert_message(conn, message_id, message_type_id, whatsapp_number)

			resp.message(get_message_text(message_type_id, message_id, user_name))
			return str(resp)

		# if we sent the second intro message to the user
		if last_message_dict['message_id'] == '2':
			# check if the user selected option 1 to know more: 
			if str(response) == '1':
				print('user selected 1')
				# send the third intro message 
				message_id = 3
				message_type_id = 2
				db.insert_message(conn, message_id, message_type_id, whatsapp_number)
				resp.message(get_message_text(message_type_id, message_id))
				return str(resp)

			if str(response) == '2':
				# send the coming soon message for quiz 
				message_id = 1 # coming soon
				message_type_id = 3 # quiz
				db.insert_message(conn, message_id, message_type_id, whatsapp_number)
				resp.message(get_message_text(message_type_id, message_id))
				return str(resp)

			if str(response) == '3':
				# share social media handles 
				message_id = 1 # share identity 
				message_type_id = 4 # share the IG handle
				db.insert_message(conn, message_id, message_type_id, whatsapp_number)
				resp.message(get_message_text(message_type_id, message_id))
				return str(resp)

		# if we sent the third intro message to the user
		if last_message_dict['message_id'] == '3':
			# check if user wants to know more: 
			if check_word_in_response(response, next_word_list):
					# send the fourth intro message 
					message_id = 4
					message_type_id = 2
					db.insert_message(conn, message_id, message_type_id, whatsapp_number)
					resp.message(get_message_text(message_type_id, message_id))
					return str(resp)

		# if we sent the fourth intro message to the user
		if last_message_dict['message_id'] == '4':
			# check if user wants to know more: 
			if check_word_in_response(response, next_word_list):
					# send the fifth intro message 
					message_id = 5
					message_type_id = 2
					db.insert_message(conn, message_id, message_type_id, whatsapp_number)
					resp.message(get_message_text(message_type_id, message_id))
					return str(resp)


	# if the last message was of Helper type and for HELP
	if helper_message_dict:
		
		# if the user wanted to reset the conversation 
		if helper_message_dict['message_id_helper'] == '0':
			if any(map(response.lower().__contains__, ['reset', 'start over'])):
				# reset user state
				print('reset user state')
				db.reset_user_state(conn, whatsapp_number)

				# send the second intro message to the user
				message_type_id=2 # Introduction type
				message_id=1 # The first hello message to ask the name again
				
				# update the message sent to user
				db.insert_message(conn, message_id, message_type_id, whatsapp_number)
				# send the message to user
				resp.message(get_message_text(message_type_id, message_id))
				return str(resp)


	# default message: Introduction message

	# send the second intro message to the user
	print('default response')
	message_id = 2
	message_type_id = 2
	db.insert_message(conn, message_id, message_type_id, whatsapp_number)

	print(db.get_user_name(conn, whatsapp_number), 'name???')
	resp.message(get_message_text(message_type_id, message_id, user_name))
	return str(resp)

	#resp.message('Hello there! Your number is %s' % whatsapp_number)
	
	#print(resp)

	#return str(resp)


if __name__ == "__main__":
	app.run(host='127.0.0.1',port=5000,debug=True)