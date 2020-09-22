from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import requests
from PIL import Image, ImageDraw
from io import BytesIO
import db
import sqlite3
import math


app = Flask(__name__)

@app.route("/")
def hello():
	return "Hello World!"


def get_jargon():

	url = 'https://corporatebs-generator.sameerkumar.website/'
	resp = requests.get(url)
	resp = resp.json()['phrase']
	#print(resp)
	return resp

def post_image():

	url = 'https://corporatebs-generator.sameerkumar.website/'
	resp = requests.get(url)
	resp = resp.json()['phrase']
	#print(resp)
	return resp

def overlay(image):

	#print("image -->", image)
	jargon = get_jargon()

	memory_image = BytesIO(image)
	pil_image = Image.open(memory_image)

	## get image width and height

	W, H = pil_image.size
	#print(image)
	#print(pil_image)

	draw = ImageDraw.Draw(pil_image)

	w, h = draw.textsize(jargon)
	print("width and height of the text", w, h)

	draw.text(
		( (W-w)/2, (H-h)/2 ), jargon, fill = "black"
		)
	#print(new_image)
	pil_image.save('hello.png')
	return None

def update_user(sender_num='+16574457032'):

	conn = db.create_connection("user.db")
	
	current_count = db.select_rows(conn, sender_num)

	if current_count == 0:
		db.create_row(conn, sender_num, current_count)

	db.insert_rows(conn, sender_num, current_count)
	
	return current_count




@app.route("/sms", methods = ['POST', 'GET'])
def sms_reply():

	## get inbound message

	msg = request.form.get('Body')
	print(msg)
	## get sender's number

	sender_num = str(request.form.get('From')).split(':')[1]
	
	current_row = update_user(sender_num)

	## create list of Aye Aye urls

	media_list = ["https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Wild_aye_aye.jpg/330px-Wild_aye_aye.jpg", 
	"https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Aye-aye_at_night_in_the_wild_in_Madagascar.jpg/481px-Aye-aye_at_night_in_the_wild_in_Madagascar.jpg",
	"https://www.sciencenews.org/wp-content/uploads/2018/08/082018_BB-aye-aye-lemur_feat.jpg",
	"https://kids.sandiegozoo.org/sites/default/files/2019-12/Hero-shadow-aye-aye.jpg"
	]

	media_list_size = len(media_list)

	n = math.floor(current_row/media_list_size)

	index = current_row-(media_list_size*n)

	## create a reply

	resp = MessagingResponse()
	try:
		num_media = int(request.values.get("NumMedia"))
	except Exception:
		print(Exception)
		num_media = None

	if not num_media:
		msg_str = "Hello, I am Aye Aye. This is message number {} from you \n\n".format(current_row)
		msg = resp.message(msg_str)

		msg.media(media_list[index])

		return str(resp)


	else:
		filename = request.values['MessageSid']
		print(filename)
		print(request.values)
		with open('{}'.format(filename), 'wb') as f:
       	
			image_url = request.values['MediaUrl0']
			f.write(requests.get(image_url).content)

			overlay(requests.get(image_url).content)

		resp.message("Thanks :)")

	return str(resp) 

@app.route("/callback", methods = ['GET', 'POST'])
def callback():

	msg = request.get_data()
	print("this is callback ---->", msg)

	return None

#@app.route()

if __name__ == "__main__":
	app.run(debug=True)