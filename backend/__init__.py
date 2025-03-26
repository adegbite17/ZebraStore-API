from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
import psycopg2


app = Flask(__name__)
CORS(app)

# database_path = r'C:\Users\USER\sqlite\fazemart.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/ZebraStore'
app.config['SECRET_KEY'] = 'c6f444bd3ed1'
app.config['FLUTTERWAVE_SECRET_KEY'] = 'FLWSECK_TEST-c559611b2da9d557e7854416e17cb208-X'
app.config['FLUTTERWAVE_PUBLIC_KEY'] = 'FLWPUBK_TEST-94f249780c523996043addef2efe367c-X'

app.config['FLUTTERWAVE_BASE_URL'] = 'https://api.flutterwave.com/v3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'aaa84d2a6a9b0215c9113cf5'  # Replace with a strong secret key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# initializing app
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Binding extensions to the app
# db.init_app(app)
# bcrypt.init_app(app)

from .models import *

login_manager = LoginManager(app)
login_manager.login_view = 'account_login'  # Adjust to your login route

from . import routes, admin_routes

with app.app_context():
    db.create_all()

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({'error': 'Unauthorized'}), 401


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

