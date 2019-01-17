from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('secrets.py')

db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


import shooter.views
