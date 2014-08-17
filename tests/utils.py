# -*- coding: utf-8 -*-
import os
import tempfile
import unittest

from stacksites import app as stacksites_app
from stacksites.settings import TestConfig
from stacksites.sites.utils import get_bucket


class BaseTestCase(unittest.TestCase):
    db_file, db_path = tempfile.mkstemp()
    app = stacksites_app.create_app(config=TestConfig(db_path))
    app.config['WTF_CSRF_ENABLED'] = False

    client = app.test_client()

    with app.app_context():
        s3_bucket = get_bucket()

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()


def user_folder_exists(bucket, username):
    return bucket.get_key('{}/home/index.html'.format(username)) is not None
