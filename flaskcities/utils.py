# -*- coding: utf-8 -*-
from flask import flash


def flash_errors(form, category="warning"):
    '''Flash all errors for a form.'''
    for field, errors in form.errors.items():
        for error in errors:
            flash("{0}".format(error), category)
