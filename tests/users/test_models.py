# -*- coding: utf-8 -*-

import flask
import pytest

from tests import utils
from stacksites.users.models import User


class TestUser(object):

    @pytest.yield_fixture
    def user(request, app):
        user = User.create(**{
            'username': 'starlord',
            'email': 'starlord@example.com',
            'password': 'ihaveaplan'
        })
        yield user
        user.delete_self()

    def test_password(self, user):
        user.activate()
        assert user.check_password('ihaveaplan') is True

        user.set_password('ihaveaplanb')
        user.save()

        assert user.check_password('ihaveaplan') is False
        assert user.check_password('ihaveaplanb') is True

    def test_activation(self, user, client):
        assert user.active is False

        activation_url = flask.url_for('users.activate', token=str(user.get_activation_token()), _external=False)
        res = client.get(activation_url, follow_redirects=True)

        assert 'Your account has been activated' in res.data
        assert user.active is True

    def test_home_site(self, user, s3_bucket):
        assert len(user.sites) == 1
        assert utils.user_folder_exists(s3_bucket, user.username)
