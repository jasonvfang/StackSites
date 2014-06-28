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

    register_controllers()

    register_blueprints(app)

    register_extensions(app)

    return app


def register_controllers():
    from flask.ext.login import login_required

    public.views.blueprint.add_url_rule('/', subdomain='<username>', view_func=public.views.view_site_home, methods=['GET'], defaults={'filename': None})
    public.views.blueprint.add_url_rule('/<filename>', subdomain='<username>', view_func=public.views.view_site_home, methods=['GET'])
    public.views.blueprint.add_url_rule("/", view_func=public.views.home, methods=["GET"])
    public.views.blueprint.add_url_rule("/save_temp/<temp_file_id>", view_func=public.views.save_temp_file, methods=['POST'])
    public.views.blueprint.add_url_rule('/view_temp/<temp_file_id>', view_func=public.views.view_temp_file)
    public.views.blueprint.add_url_rule("/dash", methods=["GET", "POST"], view_func=login_required(public.views.user_dashboard))


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
