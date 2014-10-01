# -*- coding: utf-8 -*-

import pytest
import requests

from stacksites.users.models import User
from stacksites.sites.models import Site
from stacksites.sites import utils


class TestSites(object):

    @pytest.yield_fixture
    def user(request, app):
        user = User.create(**{
            'username': 'starlord',
            'email': 'starlord@example.com',
            'password': 'ihaveaplan'
        })
        yield user
        user.delete_self()

    @pytest.yield_fixture
    def site(request, app, user):
        site = Site.create(name='test', user=user)
        yield site
        site.delete_site()

    def test_new_site(self, site, user):
        assert site in user.sites

        files = site.get_files()
        assert len(files) == 1
        index_file = files[0]
        assert 'index.html' == index_file['name']

    def test_new_site_temp_file(self, user):
        # Create file in temp file S3 bucket
        utils.update_temp_in_s3('xkcd', 'hello, world')

        # Make sure data in S3 matches
        temp_file_url = utils.make_s3_path_for_temp('xkcd')
        temp_file_data = requests.get(temp_file_url).content
        assert temp_file_data == 'hello, world'

        site = Site.create(
            name='test_with_temp_file',
            user=user,
            temp_file_id='xkcd'
        )

        assert site in user.sites

        # Make sure data in new site on S3 matches
        files = site.get_files()
        index_file = files[0]
        index_file_url = utils.make_s3_path(user.username, site.name, index_file['key'])
        index_file_data = requests.get(index_file_url).content

        assert index_file_data == temp_file_data


