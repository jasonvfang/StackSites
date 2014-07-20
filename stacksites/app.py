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

    public_bp  = public.views.blueprint

    public_bp.add_url_rule('/', subdomain='<username>', view_func=public.views.view_site_home, methods=['GET'], defaults={'path': None})
    public_bp.add_url_rule('/<path>', subdomain='<username>', view_func=public.views.view_site_home, methods=['GET'])
    public_bp.add_url_rule('/<path:path>', subdomain='<username>', view_func=public.views.view_file_in_folder)
    public_bp.add_url_rule("/", view_func=public.views.home, methods=["GET"])
    public_bp.add_url_rule("/save_temp/<temp_file_id>", view_func=public.views.save_temp_file, methods=['POST'])
    public_bp.add_url_rule('/view_temp/<temp_file_id>', view_func=public.views.view_temp_file)
    public_bp.add_url_rule("/dash", methods=["GET", "POST"], view_func=login_required(public.views.user_dashboard))

    users_bp = users.views.blueprint

    users_bp.add_url_rule('/settings', methods=['GET'], view_func=login_required(users.views.settings))
    users_bp.add_url_rule('/change_email', methods=['POST'], view_func=login_required(users.views.change_email))
    users_bp.add_url_rule('/change_password', methods=['POST'], view_func=login_required(users.views.change_password))
    users_bp.add_url_rule('/login', methods=['POST'], view_func=users.views.login)
    users_bp.add_url_rule('/logout', methods=['POST'], view_func=login_required(users.views.logout))
    users_bp.add_url_rule('/register', methods=['GET', 'POST'], view_func=users.views.register)
    users_bp.add_url_rule('/activate/<token>', methods=['GET'], view_func=users.views.activate)
    users_bp.add_url_rule('/login_help', methods=['GET'], view_func=users.views.login_help)
    users_bp.add_url_rule('/resend', methods=['POST'], view_func=users.views.resend)
    users_bp.add_url_rule('/send_reset', methods=['POST'], view_func=users.views.send_password_reset)
    users_bp.add_url_rule('/reset/<token>', methods=['GET', 'POST'], view_func=users.views.reset_password)

    sites_bp = sites.views.blueprint

    sites_bp.add_url_rule('/<username>/<site_name>', view_func=sites.views.view_site)
    sites_bp.add_url_rule('/manage/<int:site_id>', view_func=login_required(sites.views.manage_site))
    sites_bp.add_url_rule('/manage/<int:site_id>/<path:folder_key>', view_func=login_required(sites.views.manage_site_folder))
    sites_bp.add_url_rule('/upload/<int:site_id>', methods=['POST'], view_func=login_required(sites.views.upload))
    sites_bp.add_url_rule('/upload/<int:site_id>/<path:folder_key>', methods=['POST'], view_func=login_required(sites.views.upload_in_folder))
    sites_bp.add_url_rule('/edit/<int:site_id>/<path:key>', view_func=login_required(sites.views.edit_file))
    sites_bp.add_url_rule('/save/<int:site_id>', methods=['POST'], view_func=login_required(sites.views.save_file))
    sites_bp.add_url_rule('/view/<username>/<int:site_id>/<path:key>', view_func=sites.views.view_file)
    sites_bp.add_url_rule('/delete/<int:site_id>/<path:key>', methods=['POST'], view_func=login_required(sites.views.delete_file))
    sites_bp.add_url_rule('/delete_folder/<int:site_id>/<path:folder_key>', methods=['POST'], view_func=login_required(sites.views.delete_folder))
    sites_bp.add_url_rule('/delete_site/<int:site_id>', methods=['POST'], view_func=login_required(sites.views.delete_site))


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
