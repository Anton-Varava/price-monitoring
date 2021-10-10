import os
from dotenv import load_dotenv

load_dotenv()


class Configuration:
    DEBUG = True

    # PostgreSQL config
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = '<s6W1PfGYre!(3m|aNF">^jTBN^k#.'