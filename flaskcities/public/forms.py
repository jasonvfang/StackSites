# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired

from flaskcities.users.models import User


class LoginForm(Form):
    creds = TextField('Email or Username',
                      validators=[
                          DataRequired("You forgot to enter your username or email.")
                      ])
    password = PasswordField('Password',
                             validators=[
                                 DataRequired("You forgot to enter your password.")
                             ])

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        self.user = User.query.filter_by(email=self.creds.data).first()
        if not self.user:
            self.user = User.query.filter_by(username=self.creds.data).first()
            if not self.user:
                self.creds.errors.append("We didn't recognize that email address or username.")
                return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append("Wrong password.")
            return False

        # Uncomment when user activation by email works
        # if not self.user.active:
        #     self.username.errors.append("User not activated yet, please check your email.")
        #     return False
        return True
