from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from lostandfound.config import Config
import flask_whooshalchemy as wa



db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()

login_manager.session_protection = 'strong'
#tell the login manager where the login route is located
login_manager.login_view = 'users.index'
login_manager.login_message_category = 'warning'



def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(Config)
	db.init_app(app)
	bcrypt.init_app(app)
	login_manager.init_app(app)
	mail.init_app(app)
	from lostandfound.users.routes import users
	from lostandfound.items.routes import items
	from lostandfound.errors.handlers import errors
	from lostandfound.models import LostItem,FoundItem
	wa.whoosh_index(app,LostItem)
	wa.whoosh_index(app,FoundItem)
	#register blueprints
	app.register_blueprint(users)
	app.register_blueprint(items)
	app.register_blueprint(errors)

	return app