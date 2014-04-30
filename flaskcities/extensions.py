# -*- coding: utf-8 -*-


from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()


from flask.ext.bcrypt import Bcrypt
bcrypt = Bcrypt()


from flask.ext.login import LoginManager
login_manager = LoginManager()


from flask.ext.migrate import Migrate
migrate = Migrate()


from flask.ext.mail import Mail
mail = Mail()