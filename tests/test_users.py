# -*- coding: utf-8 -*-

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

    def test_existing_user(self):
        pass

    def test_nonexistent_user(self):
        pass

    def test_invalid_credentials(self):
        pass
