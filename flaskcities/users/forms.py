# -*- coding: utf-8 -*-
from flask.ext.login import current_user
from flask_wtf import Form
from wtforms import TextField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from flaskcities.users.models import User
from flaskcities.form_utils import has_upper_nonalpha

EXTRA_WHITESPACE = "The username you entered had an extra space (which was removed). If you don't know what that means, then don't worry."


class ChangeEmailForm(Form):
    email = TextField('Email',
                       validators=[DataRequired("You must enter an email address."), Email()])

    def validate(self):
        initial_validation = super(ChangeEmailForm, self).validate()
        if not initial_validation:
            return False
        if current_user.email == self.email.data:
            self.email.errors.append('That is the same email address. Please enter a different email address.')
            return False
        conflicts = User.query.filter_by(email=self.email.data).all()
        if conflicts:
            self.email.errors.append('That email address is being used by another user. Please enter a different email address.')
            return False
        return True



class ChangePasswordForm(Form):
    old_password = PasswordField('Old Password', validators=[DataRequired('You must enter your current password.')])
    new_password = PasswordField('New Password', validators=[DataRequired('You must enter your new password.')])
    confirm_new = PasswordField('Confirm Password', validators=[DataRequired('Please re-type the password entered above.'),
                                EqualTo('new_password', message='Passwords must match.')])

    def validate(self):
        initial_validation = super(ChangePasswordForm, self).validate()
        if not initial_validation:
            return False
        if not current_user.check_password(self.old_password.data):
            self.old_password.errors.append('The old password you entered is incorrect.')
            return False
        if current_user.check_password(self.new_password.data):
            self.new_password.errors.append('You cannot use the same password as your new password.')
            return False
        return True


class RegisterForm(Form):
    username = TextField('Username', validators=[DataRequired("You must enter a username."), 
                         Length(min=2, max=25)])
    email = TextField('Email',
                       validators=[DataRequired("You must enter an email address."), Email(), Length(min=6, max=40)])
    password = PasswordField('Password',
                             validators=[DataRequired("You must enter a password."), Length(min=6, max=40)])
    confirm = PasswordField('Verify password',
                            validators=[DataRequired("Please re-type the password entered above."), EqualTo('password', message='Passwords must match.')])
    
    notify = []

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False

        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("That email address has already been registered.")
            return False

        # if the username has an extra space, notify and remove it, but don't cause a fuss
        if ' ' in self.username.data:
            self.notify.append((EXTRA_WHITESPACE, 'info'))
            self.username.data = self.username.data.strip()

        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append("That username has already been taken.")
            return False

        results = has_upper_nonalpha(self.username.data, 'username')
        if results:
            self.username.errors.extend(results)
            return False
        
        self.user = user
        return True 


class LoginForm(Form):
    creds = TextField('Email or Username', 
                       validators=[
                       DataRequired("You forgot to enter your username or email.")
                       ])
    password = PasswordField('Password',
                              validators=[
                              DataRequired("You forgot to enter your password.")
                              ])
    activated = BooleanField("Account Status")

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        # some mobile keyboards have a tendency to add whitespace
        self.creds.data = self.creds.data.strip()
        self.user = User.query.filter_by(email=self.creds.data).first()
        if not self.user:
            self.user = User.query.filter_by(username=self.creds.data).first()
            if not self.user:
                self.creds.errors.append("We didn't recognize that email address or username.")
                return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append("Wrong password.")
            return False

        if not self.user.active:
            self.activated.errors.append("Your account has not been activated yet. \
             Please check your inbox for the activation email or resend one.")
            return False

        return True


class ResendConfirmationForm(Form):
    creds = TextField("Email or Username",
                      validators=[DataRequired("You must enter your email address or username.")])

    def __init__(self, *args, **kwargs):
        super(ResendConfirmationForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        initial_validation = super(ResendConfirmationForm, self).validate()
        if not initial_validation:
            return False

        self.user = User.query.filter_by(email=self.creds.data).first()
        if not self.user:
            self.user = User.query.filter_by(username=self.creds.data).first()
            if not self.user:
                self.creds.errors.append("We didn't recognize that email address or username. Please try again.")
                return False

        if self.user.active:
            self.creds.errors.append("This account has already been activated.")
            return False

        return True


class ForgotPasswordForm(Form):
    email = TextField("Email",
                      validators=[DataRequired("You must enter your email address.")])

    def __init__(self, *args, **kwargs):
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        initial_validation = super(ForgotPasswordForm, self).validate()
        if not initial_validation:
            return False

        self.user = User.query.filter_by(email=self.email.data).first()
        if not self.user:
            self.email.errors.append("We didn't recognize that email address. Please try again.")
            return False
        return True


class ResetPasswordForm(Form):
    email = TextField("Email", validators=[DataRequired("You must enter your email address."), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired("You must enter a password."),
                             Length(min=6, max=40)])
    confirm = PasswordField('Verify password',
                            validators=[DataRequired("Please re-type the password entered above."),
                            EqualTo('password', message='Passwords must match.')])

    def __init__(self, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        initial_validation = super(ResetPasswordForm, self).validate()
        if not initial_validation:
            return False
        return True