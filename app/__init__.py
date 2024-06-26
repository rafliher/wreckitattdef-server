# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from config import Config
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import datetime
from flask_apscheduler import APScheduler

app = Flask(__name__, template_folder='../templates')
app.static_folder = '../static'
app.config.from_object(Config)

db = SQLAlchemy(app)

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
jwt = JWTManager(app)

CORS(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize APScheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

from app import models, views, controllers
from app.controllers import main_controller, auth_controller, user_controller, challenge_controller, tick_controller

# Example job to call next_tick every tick duration
def execute_next_tick():
    with app.app_context():
        config = models.Config.query.first()
        if config and config.challenge_started:
            print(tick_controller.next_tick())

def schedule_next_tick():
    with app.app_context():
        config = models.Config.query.first()
        if config and config.challenge_started and not tick_controller.tick_started:
            tick_duration_seconds = config.tick_duration_seconds
            scheduler.add_job(func=execute_next_tick, trigger='interval', id="next_tick_job", seconds=tick_duration_seconds)
            tick_controller.tick_started = True

def schedule_listener():
    with app.app_context():
        scheduler.add_job(func=schedule_next_tick, trigger='interval', id="start_tick", seconds=2)

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))

# push context manually to app
with app.app_context():
    try:
        schedule_listener()  # Start scheduling initially
        # Check if an admin user exists
        admin_user = models.User.query.filter_by(is_admin=True).first()

        # If no admin user exists, create one
        if not admin_user:
            admin = models.User(username='admin', password_hash=generate_password_hash('admin'), is_admin=True, host_ip="")
            db.session.add(admin)
            db.session.commit()
            
        # Check if a configuration row exists
        config = models.Config.query.first()

        # If no configuration exists, create one
        if not config:
            default_config = models.Config(challenge_started=False, ticks_count=0, tick_duration_seconds=60)  # Adjust default values as needed
            db.session.add(default_config)
            db.session.commit()
    except Exception as e:
        print(e)
        print("Did you python init_db.py yet?")