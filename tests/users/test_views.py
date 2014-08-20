# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import pytest
import flask

from tests import utils
from stacksites.users.models import User


def login(data, client):
    return client.post('/users/login', data=data, follow_redirects=True)


class TestRegistration(object):

    def test_create_delete_new_valid_user(self, client, s3_bucket, registration_data):
        assert User.query.count() == 0
        assert not utils.user_folder_exists(s3_bucket, registration_data['username'])

        res = client.post('/users/register', data=registration_data, follow_redirects=True)
        user = User.get_by_id(1)

        assert res.status_code == 200
        assert User.query.count() == 1
        assert utils.user_folder_exists(s3_bucket, user.username)

        user.delete_self()

        assert User.query.count() == 0
        assert not utils.user_folder_exists(s3_bucket, registration_data['username'])

    def test_create_existing_valid_user(self, client, registration_data):
        assert User.query.count() == 0

        res = client.post('/users/register', data=registration_data, follow_redirects=True)

        assert User.query.count() == 1

        res = client.post('/users/register', data=registration_data, follow_redirects=True)

        assert User.query.count() == 1

        user = User.get_by_id(1)
        user.delete_self()

        assert User.query.count() == 0

    def test_invalid_user(self, client, registration_data):
        registration_data['confirm'] = 'ihaveaplan2'
        assert User.query.count() == 0

        res = client.post('/users/register', data=registration_data, follow_redirects=True)

        assert User.query.count() == 0


class TestLogin(object):

    @pytest.yield_fixture(scope='class')
    def user(request):
        user = User.create(**{
            'username': 'starlord',
            'email': 'starlord@example.com',
            'password': 'ihaveaplan'
        })
        user.activate()

        yield user

        user.delete_self()

    def test_existing_user(self, client, user):
        res = login(data={
            'creds': 'starlord',
            'password': 'ihaveaplan'
        }, client=client)

        assert res.status_code == 200
        assert 'Your Sites' in res.data

        res = client.post('/users/logout', follow_redirects=True)

        assert res.status_code == 200
        assert 'users/login' in res.data
        assert 'users/register' in res.data
        assert 'users/login_help' in res.data

    def test_nonexistent_user(self, client):
        res = login(data={
            'creds': 'rocket',
            'password': 'ohyeaah'
        }, client=client)

        assert "We didn&#39;t recognize that email address or username." in res.data

    def test_invalid_credentials(self, client, user):
        res = login(data={
            'creds': 'starlord',
            'password': 'ihaveaplan2'
        }, client=client)

        assert 'Wrong password' in res.data


class TestPasswordReset(object):

    @pytest.yield_fixture
    def user(request):
        user = User.create(**{
            'username': 'starlord',
            'email': 'starlord@example.com',
            'password': 'ihaveaplan'
        })
        user.activate()

        yield user

        user.delete_self()

    def test_reset_existing_user(self, user, client):
        reset_url = flask.url_for('users.reset_password', token=user.get_reset_token(), _external=False)
        res = client.get(reset_url)

        assert res.status_code == 200
        assert 'resetForm' in res.data

        reset_data = {
            'email': 'starlord@example.com',
            'password': 'ihaveaplan2',
            'confirm': 'ihaveaplan2'
        }
        res = client.post(reset_url, data=reset_data, follow_redirects=True)

        assert res.status_code == 200
        assert 'Your password has been reset.' in res.data
        assert user.check_password('ihaveaplan2') is True

        res = client.post(reset_url, data={
            'email': 'starlord@example.com',
            'password': 'thatsnotareallaugh',
            'confirm': 'thatsnotareallaugh'
        }, follow_redirects=True)

        assert 'Invalid or expired password reset token.' in res.data
        assert not user.check_password('thatsnotareallaugh')

    def test_reset_same_password(self, client, user):
        reset_url = flask.url_for('users.reset_password', token=user.get_reset_token(), _external=False)

        res = client.post(reset_url, data={
            'email': 'starlord@example.com',
            'password': 'ihaveaplan',
            'confirm': 'ihaveaplan'
        }, follow_redirects=True)

        assert 'You cannot use the same password.' in res.data

    def test_reset_expired(self, client, user):
        reset_url = flask.url_for('users.reset_password', token=user.get_reset_token(), _external=False)

        user.password_reset_expiration = datetime.utcnow() - timedelta(hours=1)
        user.save()

        res = client.post(reset_url, data={
            'email': 'starlord@example.com',
            'password': 'thatsnotareallaugh',
            'confirm': 'thatsnotareallaugh'
        }, follow_redirects=True)

        assert 'Invalid or expired password reset token.' in res.data
        assert not user.check_password('thatsnotareallaugh')


class TestChangeSettings(object):

    @pytest.yield_fixture(scope='function')
    def user(request):
        user = User.create(**{
            'username': 'starlord',
            'email': 'starlord@example.com',
            'password': 'ihaveaplan'
        })
        user.activate()

        yield user

        user.delete_self()

    @pytest.yield_fixture(scope='function')
    def other_user(request):
        user = User.create(**{
            'username': 'rocket',
            'email': 'rocket@example.com',
            'password': 'youdonthaveaplan'
        })
        user.activate()
        yield user
        user.delete_self()

    def login(self, client):
        return login(data={
            'creds': 'starlord@example.com',
            'password': 'ihaveaplan'
        }, client=client)

    def logout(self, client):
        return client.post('/users/logout', follow_redirects=True)

    def test_change_email(self, client, user):
        res = self.login(client)

        res = client.post('/users/change_email', data={'email': 'noonecaresgroot@example.com'}, follow_redirects=True)

        assert user.email == 'noonecaresgroot@example.com'

        res = self.logout(client)

        res = client.post('/users/login', data={
            'creds': 'noonecaresgroot@example.com',
            'password': 'ihaveaplan'
        }, follow_redirects=True)

        assert 'Your Sites' in res.data

    def test_change_email_different_user(self, client, user, other_user):
        res = self.login(client)

        res = client.post('/users/change_email', data={'email': 'rocket@example.com'}, follow_redirects=True)

        assert 'That email address is being used by another user.' in res.data
        assert user.email != 'rocket@example.com'

    def test_change_password(self, client, user):
        res = self.login(client)

        assert 'Your Sites' in res.data

        res = client.post('/users/change_password', data={
            'old_password': 'ihaveaplan',
            'new_password': 'ihaveaplanb',
            'confirm_new': 'ihaveaplanb'
        }, follow_redirects=True)

        assert 'Your password has been changed.' in res.data

        res = login(data={
            'creds': 'starlord@example.com',
            'password': 'ihaveaplanb'
        }, client=client)

        assert 'Your Sites' in res.data
