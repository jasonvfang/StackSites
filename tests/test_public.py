# -*- coding: utf-8 -*-
import os
import unittest
import tempfile

import flask

from utils import BaseTestCase
from stacksites import app as stacksites_app


class TestHomePage(BaseTestCase):

    def test_landing(self):
        res = self.client.get('/')
        self.assertEquals(res.status_code, 200)
        # just filler
        self.assertTrue('users/login' in res.data)
        self.assertTrue('users/register' in res.data)
        self.assertTrue('users/login_help' in res.data)
