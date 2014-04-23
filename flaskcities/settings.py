# -*- coding: utf-8 -*-
import os


class Config(object):
    SECRET_KEY = 'example_secret_key'
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    AWS_ACCESS_KEY = 'AKIAJHP7TYOMOZCKGWLQ'
    AWS_SECRET_KEY = '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'
    BUCKET_NAME = 'flaskcities'


class DevConfig(Config):
    DEBUG = True
    DB_NAME = 'dev.db'
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = "sqlite:///{0}".format(DB_PATH)
