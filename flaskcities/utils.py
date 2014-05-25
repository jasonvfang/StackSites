# -*- coding: utf-8 -*-
from flask import flash, request
from flask.ext.login import current_user


def flash_errors(form, category="warning"):
    '''Flash all errors for a form.'''
    for field, errors in form.errors.items():
        for error in errors:
            flash("{0}".format(error), category)


def is_auth():
    return current_user and current_user.is_authenticated()


def is_post_and_valid(form):
    return request.method == 'POST' and form.validate_on_submit()
