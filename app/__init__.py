from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os

from app.config import DevelopmentConfig, ProductionConfig

from apscheduler.schedulers.background import BackgroundScheduler


load_dotenv()

app = Flask(__name__)
config = DevelopmentConfig() if os.getenv('FLASK_ENV') == 'development' else ProductionConfig()
app.config.from_object(config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
scheduler = BackgroundScheduler()
login_manager = LoginManager(app)
login_manager.login_view = 'sign_in'
login_manager.login_message_category = 'info'

from app import routes
from app import scheduled_tasks



