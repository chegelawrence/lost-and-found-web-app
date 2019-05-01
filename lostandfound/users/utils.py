import os
import secrets
from flask import current_app
from PIL import Image
from lostandfound import mail
from flask_mail import Message
from flask import url_for

#Update user profile picture
def save_profile_picture(profile_picture):
	random_hex = secrets.token_hex(8)
	_,f_ext = os.path.splitext(profile_picture.filename)
	picture_fn = random_hex + f_ext
	full_picture_path = os.path.join(current_app.root_path,'static/profile_pics',picture_fn)
	output_size = (120,120)
	i = Image.open(profile_picture)
	i.thumbnail(output_size)
	i.save(full_picture_path)

	return picture_fn

def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request',
		sender='noreply@mmulostandfound.com',
		recipients=[user.email])
	msg.body = f"""
	Visit the following link to reset your password:
	{url_for('users.reset_token',token=token,_external=True)}

	Ignore this if you did not make the request and no changes will be made.
	"""
	#send message
	mail.send(msg)