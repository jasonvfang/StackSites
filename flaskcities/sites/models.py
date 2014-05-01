# -*- coding: utf-8 -*-
from datetime import datetime

from flaskcities.database import db, CRUDMixin
from .utils import upload_index_for_new_site, make_s3_path


class Site(CRUDMixin, db.Model):
    __tablename__ = 'site'
    name = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime(), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, username):
        self.name = name
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        upload_index_for_new_site(username, name)

    def update_time(self):
        self.updated_at = datetime.utcnow()
        self.save()

    def __repr__(self):
        username = self.user or ""
        return "<Site ({0}, user: {1})>".format(self.name, username)

