from config import *
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

UPLOAD_FOLDER = "./images"
   
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_object(__name__)
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
#login_manager.anonymous_user = AnonymousUserMixIn()

from views import *
from models import *
db.create_all()
