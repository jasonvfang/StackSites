# -*- coding: utf-8 -*-
from flask import flash
from flask.ext.login import current_user


def flash_errors(form, category="warning"):
    '''Flash all errors for a form.'''
    for field, errors in form.errors.items():
        for error in errors:
            flash("{0}".format(error), category)


def is_auth():
    return current_user and current_user.is_authenticated()