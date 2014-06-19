# -*- coding: utf-8 -*-
from flask import Flask
import os
import time

from stacksites import public, users, sites
from stacksites.assets import assets
from stacksites.settings import ProdConfig, DevConfig
from stacksites.extensions import (db, bcrypt, login_manager,
                                    migrate, mail, SSLify, csrf)


def create_app():
    app = Flask(__name__)
    config_object = DevConfig if os.environ.get('DEBUG') == 'True' else ProdConfig
    app.config.from_object(config_object)
    register_blueprints(app)
    register_extensions(app)
    return app


def register_extensions(app):
    assets.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.session_protection = 'strong'
    migrate.init_app(app, db)
    mail.init_app(app)
    sslify = SSLify(app)
    csrf.init_app(app)
    init_db(app)
    return None


def register_blueprints(app):
    app.register_blueprint(public.views.blueprint)
    app.register_blueprint(users.views.blueprint)
    app.register_blueprint(sites.views.blueprint)
    return None


def init_db(app):
    from stacksites.users import models
    from stacksites.sites import models
    db.init_app(app)
    with app.app_context():
        db.create_all()
