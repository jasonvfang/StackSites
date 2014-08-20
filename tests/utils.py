# -*- coding: utf-8 -*-


def user_folder_exists(bucket, username):
    return bucket.get_key('{}/home/index.html'.format(username)) is not None
