# -*- coding: utf-8 -*-

import unittest

import utils
from stacksites.users.models import User


class TestRegistration(utils.BaseTestCase):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.registration_data = {
            'username': 'starlord',
            'email': 'starlord@gmail.com',
            'password': 'ihaveaplan',
            'confirm': 'ihaveaplan'
        }

    def test_create_delete_new_valid_user(self):
        self.assertEqual(User.query.count(), 0)
        self.assertFalse(utils.user_folder_exists(self.s3_bucket, self.registration_data['username']))

        res = self.client.post('/users/register', data=self.registration_data, follow_redirects=True)
        user = User.get_by_id(1)

        self.assertEquals(res.status_code, 200)
        self.assertEqual(User.query.count(), 1)
        self.assertTrue(utils.user_folder_exists(self.s3_bucket, user.username))

        user.delete_self()

        self.assertEqual(User.query.count(), 0)
        self.assertFalse(utils.user_folder_exists(self.s3_bucket, self.registration_data['username']))

    def test_create_existing_valid_user(self):
        pass

    def test_invalid_user(self):
        pass
