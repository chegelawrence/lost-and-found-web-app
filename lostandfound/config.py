import os
"""
class contains the app configuration variables
"""
class Config:
	SECRET_KEY = '78B68A047A3DE46BDF4FB7398FD271BE1DFE44BEF7BF8343A6E6842D3DCAFEB6'
	SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	#twilio api
	AUTHY_API_KEY = '*****'
	WHOOSH_BASE = 'site.db'
	MAIL_SERVER = 'smtp.googlemail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USERNAME = '*****'
	MAIL_PASSWORD = '*****'
