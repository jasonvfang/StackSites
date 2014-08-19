# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import pytest
import flask

import utils
from stacksites.users.models import User


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
            'email': 'starlord@gmail.com',
            'password': 'ihaveaplan'
        })
        user.activate()

        yield user

        user.delete_self()

    def login(self, data, client):
        return client.post('/users/login', data=data, follow_redirects=True)

    def test_existing_user(self, client, user):
        res = self.login(data={
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
        res = self.login(data={
            'creds': 'rocket',
            'password': 'ohyeaah'
        }, client=client)

        assert "We didn&#39;t recognize that email address or username." in res.data

    def test_invalid_credentials(self, client, user):
        res = self.login(data={
            'creds': 'starlord',
            'password': 'ihaveaplan2'
        }, client=client)

        assert 'Wrong password' in res.data


class TestPasswordReset(object):

    @pytest.yield_fixture
    def user(request):
        user = User.create(**{
            'username': 'starlord',
            'email': 'starlord@gmail.com',
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
            'email': 'starlord@gmail.com',
            'password': 'ihaveaplan2',
            'confirm': 'ihaveaplan2'
        }
        res = client.post(reset_url, data=reset_data, follow_redirects=True)

        assert res.status_code == 200
        assert 'Your password has been reset.' in res.data
        assert user.check_password('ihaveaplan2') is True

        res = client.post(reset_url, data={
            'email': 'starlord@gmail.com',
            'password': 'thatsnotareallaugh',
            'confirm': 'thatsnotareallaugh'
        }, follow_redirects=True)

        assert 'Invalid or expired password reset token.' in res.data
        assert not user.check_password('thatsnotareallaugh')

    def test_reset_same_password(self, client, user):
        reset_url = flask.url_for('users.reset_password', token=user.get_reset_token(), _external=False)

        res = client.post(reset_url, data={
            'email': 'starlord@gmail.com',
            'password': 'ihaveaplan',
            'confirm': 'ihaveaplan'
        }, follow_redirects=True)

        assert 'You cannot use the same password.' in res.data

    def test_reset_expired(self, client, user):
        reset_url = flask.url_for('users.reset_password', token=user.get_reset_token(), _external=False)

        user.password_reset_expiration = datetime.utcnow() - timedelta(hours=1)
        user.save()

        res = client.post(reset_url, data={
            'email': 'starlord@gmail.com',
            'password': 'thatsnotareallaugh',
            'confirm': 'thatsnotareallaugh'
        }, follow_redirects=True)

        assert 'Invalid or expired password reset token.' in res.data
        assert not user.check_password('thatsnotareallaugh')
