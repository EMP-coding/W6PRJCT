from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
import os

app = Flask(__name__)
if 'SECRET_KEY' in os.environ:
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

if 'DATABASE_URL' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models


