# -*- coding: utf-8 -*-
import os


def _setup_envvars():
    with open('.env', 'r') as f:
        for line in f:
            split = line.split('=')
            os.environ[split[0]] = split[1].replace('\n', '')


class Config(object):
    _setup_envvars()

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ourincrediblejourney'
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT') or 587
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    BUCKET_NAME = 'flaskcities'
    TEMP_BUCKET_NAME = 'flaskcities-temp'
    BCRYPT_LEVEL = 13
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class ProdConfig(Config):
    ENV = 'prod'
    DEBUG = False
    ASSETS_DEBUG = False
    SERVER_NAME = 'stacksites.org'


class DevConfig(Config):
    ENV = 'dev'
    DEBUG = True
    DB_NAME = 'dev.db'
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    ASSETS_DEBUG = True
    SERVER_NAME = '127.0.0.1.xip.io:5000'


class TestConfig(DevConfig):
    TESTING = True

    def __init__(self, db_path):
        self.db_path = db_path
        self.SQLALCHEMY_DATABASE_URI = 'sqlite:///{path}'.format(path=self.db_path)
