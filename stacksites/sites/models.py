# -*- coding: utf-8 -*-
from datetime import datetime

from stacksites.database import db, CRUDMixin
from .utils import upload_index_for_new_site, make_s3_path, get_files_data, delete_site_from_s3, transfer_landing_demo


class Site(CRUDMixin, db.Model):
    __tablename__ = 'site'
    name = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime(), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, user, temp_file_id=None):
        self.name = name
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.user = user
        if temp_file_id is not None:
            transfer_landing_demo(temp_file_id, user.username, name)
        else:
            upload_index_for_new_site(user.username, name)

    def update_time(self):
        self.updated_at = datetime.utcnow()
        self.save()

    def get_files(self):
        return get_files_data(self.user.username, self.name)

    def delete_site(self):
        delete_site_from_s3(self.user.username, self.name)
        self.delete()

    def __repr__(self):
        username = self.user or ""
        return "<Site ({0}, user: {1})>".format(self.name, username)
