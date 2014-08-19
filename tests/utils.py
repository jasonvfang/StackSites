# -*- coding: utf-8 -*-

from stacksites.sites.utils import get_bucket


def user_folder_exists(bucket, username):
    return bucket.get_key('{}/home/index.html'.format(username)) is not None
