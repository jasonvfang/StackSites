# -*- coding: utf-8 -*-


class TestHomePage(object):

    def test_landing(self, client, s3_bucket):
        res = client.get('/')

        assert res.status_code == 200
        assert 'users/login' in res.data
        assert 'users/register' in res.data
        assert 'users/login_help' in res.data
        assert s3_bucket is not None
