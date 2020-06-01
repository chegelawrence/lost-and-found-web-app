import os
import secrets
from flask import current_app
from PIL import Image
import requests
import json
import tensorflow as tf
import pusher

import numpy as np

#Update user profile picture
def save_item_picture(item_picture):
	random_hex = secrets.token_hex(8)
	_,f_ext = os.path.splitext(item_picture.filename)
	picture_fn = random_hex + f_ext
	full_picture_path = os.path.join(current_app.root_path,'static/item_pics',picture_fn)
	output_size = (120,120)
	i = Image.open(item_picture)
	i.thumbnail(output_size)
	i.save(full_picture_path)

	return picture_fn

#delete the item image from the filesystem
def delete_item_picture(item_picture):
	if item_picture != "default.png":
		try:
			os.remove(os.path.join(current_app.root_path,'static/item_pics',item_picture))
		except:
			pass

def sendPushNotification():
	pusher_client = pusher.Pusher(app_id=u'708780', key=u'1774431e5feb87294873', secret=u'******', cluster=u'us2',ssl=True)
	return pusher_client


#predict what image user has uploaded
class PredictImage:
	def __init__(self,image):
		self.image = image

	def makeInference(self):
		item_picture = tf.keras.preprocessing.image\
		.load_img(path=os.path.join(current_app.root_path,'static/item_pics',self.image)\
			,target_size=(150,150))

		#convert image to a numpy tensor and normalize
		item_picture = tf.keras.preprocessing.image.img_to_array(img=item_picture) / 255.0
		item_picture = item_picture.reshape((1,150,150,3))

		#These are the image classes for which the model was trained to classify
		classes = ['bag','glasses','heels','jacket','keys','laptop','phone','purse','sandals','shoe','sweater','wallet','watch']
		data = json.dumps({"signature_name": "serving_default", "instances": item_picture.tolist()})

		#Make a post request to the tensorflow serving api endpoint
		headers = {"content-type": "application/json"}
		json_response = requests.post('http://localhost:9001/v1/models/ItemImageClassifier:predict', data=data, headers=headers)
		predictions = json.loads(json_response.text)['predictions']
		#What did the model predict
		return classes[np.argmax(predictions)]
