import os
from dotenv import load_dotenv

load_dotenv()


class DevelopmentConfig(object):
    DEBUG = True

    # PostgreSQL config
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    SCHEDULER_API_ENABLED = True

    # Mail config
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')


class ProductionConfig(object):
    DEBUG = False

    # PostgreSQL config
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    SCHEDULER_API_ENABLED = True

    # Mail config
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')


