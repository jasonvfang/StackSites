import os
import time
import logging
from flask import Flask

from flaskcities import public, users, sites
from .extensions import db, bcrypt, login_manager
from .settings import DevConfig


def create_app(config_object=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_object)
    register_blueprints(app)
    register_extensions(app)
    # register_loggers(app)
    return app
    

def register_blueprints(app):
    app.register_blueprint(public.views.blueprint)
    app.register_blueprint(users.views.blueprint)
    app.register_blueprint(sites.views.blueprint)


def register_extensions(app):
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)


def register_loggers(app):
    if not os.path.exists(os.path.join(os.getcwd(), 'errors')):
        os.mkdir('errors')
    fmt = logging.Formatter('\n\n%(asctime)s:%(levelname)s - %(module)s:%(funcName)s - %(message)s\n\n',
                            datefmt='%m/%d/%g@%H:%M')
    fh = logging.FileHandler(os.path.join(os.getcwd(), 
                             "errors/{0}.log".format(time.strftime("%m-%d-%g@%H:%M"))))
    fh.setLevel(logging.ERROR)
    fh.setFormatter(fmt)
    app.logger.addHandler(fh)

import views