# -*- coding: utf-8 -*-
from flask import current_app
from flask.ext.login import UserMixin
from datetime import datetime, timedelta
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from flaskcities.database import db, CRUDMixin
from flaskcities.extensions import bcrypt
from flaskcities.sites.models import Site
from .utils import generate_secure_token


class User(UserMixin, CRUDMixin, db.Model):
    __tablename__ = 'user'
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    pwdhash = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    active = db.Column(db.Boolean())
    roles = db.Column(db.PickleType())

    activation_token = db.Column(db.String(30), unique=True)

    password_reset_token = db.Column(db.String(30), unique=True)
    password_reset_expiration = db.Column(db.DateTime())

    sites = db.relationship('Site', backref='user')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.created_at = datetime.utcnow()
        self.active = False
        self.roles = frozenset()
        self.set_password(password)
        self.sites.append(Site('home', self))

    def set_password(self, password):
        self.pwdhash = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.pwdhash, password)

    def get_activation_token(self):
        self.activation_token = generate_secure_token()
        self.save()
        return self.activation_token

    def activate(self):
        self.active = True
        self.save()
        return True

    def get_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        self.password_reset_expiration = datetime.utcnow() + timedelta(hours=1)
        self.save()
        return s.dumps({'reset': self.id})

    def reset_password(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        return True


    def has_role(self, role):
        return self.roles != None and role in self.roles

    def add_role(self, role):
        if self.roles:
            elems = [e for e in self.roles]
            elems.append(role)
            self.roles = frozenset(elems)
        else:
            self.roles = frozenset((role,))

    def __repr__(self):
        return "<User ({0}, id: {1})>".format(self.username, self.id)