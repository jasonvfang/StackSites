# -*- coding: utf-8 -*-
import os
import base64

from flask import url_for
from flask.ext.mail import Message


def send_password_reset_email(user):
    reset_link = url_for(
                    'users.reset_password',
                    token = user.get_reset_token(),
                    _external=True
                 )
    msg = """
Click the link below to reset your FlaskCities password. 

{0}""".format(str(reset_link))
    send_email("Reset your password", msg, str(user.email))


def send_confirmation_email(user):
    activation_link = url_for(
                        'users.activate',
                        token=str(user.get_activation_token()),
                        _external=True
                      )
    msg = """
Click the link below to activate your account with FlaskCities! 

{0}""".format(str(activation_link))
    send_email("Confirm your account", msg, str(user.email))


def send_email(subject, body, address):
    from flaskcities.app import mail
    msg = Message(subject, recipients=[address])
    msg.body = body
    mail.send(msg)


def generate_secure_token(length=30):
    return base64.urlsafe_b64encode(os.urandom(length))[:30]