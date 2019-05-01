from lostandfound import db,login_manager
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin
from flask import current_app


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

"""
Database models
"""
class User(db.Model,UserMixin):
	__tablename__ = 'users'
	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(20),unique=True,nullable=False)
	email = db.Column(db.String(100),unique=True,nullable=False)
	profile_image = db.Column(db.String(20),nullable=False,default='default.jpg')
	phone = db.Column(db.String(10),unique=True,nullable=False)
	password = db.Column(db.String(60),nullable=False)
	#Relationhips
	lostitems = db.relationship('LostItem',backref='owner',lazy=True)
	founditems = db.relationship('FoundItem',backref='finder',lazy=True)

	#generate password reset token
	def get_reset_token(self,expires_sec=1800):
		s = Serializer(current_app.config['SECRET_KEY'],expires_sec)
		return s.dumps({'user_id':self.id}).decode('utf-8')
	
	#verify password reset token
	@staticmethod
	def verify_reset_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)

	def __repr__(self):
		return f"User('{self.username}','{self.email}','{self.phone}')"


class LostItem(db.Model):
	__tablename__ = 'lostitems'
	__searchable__ = ['name','place_lost','description']
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(100),nullable=False)
	place_lost = db.Column(db.String(30),nullable=False)
	date_reported = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
	item_image = db.Column(db.String(20),nullable=False,default='default.png')
	description = db.Column(db.Text,nullable=False)
	user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)

	def __repr__(self):
		return f"LostItem('{self.name}','{self.description}','{self.place_lost}')"

class FoundItem(db.Model):
	__tablename__ = 'founditems'
	__searchable__ = ['name','place_found','description']
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(100),nullable=False)
	place_found = db.Column(db.String(30),nullable=False)
	description = db.Column(db.Text,nullable=False)
	date_reported = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
	item_image = db.Column(db.String(20),nullable=False,default='default.png')
	user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)

	def __repr__(self):
		return f"FoundItem('{self.name}','{self.description}','{self.place_found}')"
