# -*- coding: utf-8 -*-


from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()


from flask.ext.bcrypt import Bcrypt
bcrypt = Bcrypt()


from flask.ext.login import LoginManager
login_manager = LoginManager()