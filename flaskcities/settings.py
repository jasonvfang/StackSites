# -*- coding: utf-8 -*-
import os


class Config(object):
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
    BCRYPT_LEVEL = 13
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class ProdConfig(Config):
    ENV = 'prod'
    DEBUG = False
    ASSETS_DEBUG = False


class DevConfig(Config):
    ENV = 'dev'
    DEBUG = True
    DB_NAME = 'dev.db'
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    ASSETS_DEBUG = True