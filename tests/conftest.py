# -*- coding: utf-8 -*-
import os
import tempfile

import pytest

from stacksites.settings import TestConfig
from stacksites import app as stacksites_app
from stacksites.sites.utils import get_bucket


@pytest.yield_fixture(scope='session')
def app():
    db_file, db_path = tempfile.mkstemp()
    app = stacksites_app.create_app(config=TestConfig(db_path))
    app.config['WTF_CSRF_ENABLED'] = False

    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()
    os.close(db_file)
    os.unlink(db_path)


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def s3_bucket(app):
    return get_bucket()


@pytest.fixture
def registration_data():
    return {
        'username': 'starlord',
        'email': 'starlord@gmail.com',
        'password': 'ihaveaplan',
        'confirm': 'ihaveaplan'
    }
