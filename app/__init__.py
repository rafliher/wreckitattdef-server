# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from config import Config

app = Flask(__name__, template_folder='../templates')
app.static_folder = '../static'
app.config.from_object(Config)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app import models, views, controllers
from app.controllers import main_controller, auth_controller, user_controller, challenge_controller

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))

# push context manually to app
with app.app_context():
    try:
        # Check if an admin user exists
        admin_user = models.User.query.filter_by(is_admin=True).first()

        # If no admin user exists, create one
        if not admin_user:
            admin = models.User(username='admin', password_hash=generate_password_hash('admin'), is_admin=True, host_ip="")
            db.session.add(admin)
            db.session.commit()
    except Exception as e:
        print(e)
        print("Did you python init_db.py yet?")