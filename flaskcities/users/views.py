# -*- coding: utf-8 -*-
from flask import (Blueprint, request, render_template, flash,
                   url_for, redirect)
from flask.ext.login import login_user, login_required, logout_user, current_user
from datetime import datetime

from flaskcities.users.forms import RegisterForm, LoginForm, ResendConfirmationForm, ForgotPasswordForm, ResetPasswordForm
from flaskcities.users.utils import send_confirmation_email, send_password_reset_email
from flaskcities.extensions import login_manager
from flaskcities.utils import flash_errors
from flaskcities.users.models import User

blueprint = Blueprint('users', __name__, url_prefix='/users', static_folder="../static")


@blueprint.route("/login", methods=["POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user)
        redirect_url = request.args.get('next') or url_for('public.user_dashboard')
        return redirect(redirect_url)
    else:
        flash_errors(form)
        return redirect(url_for('public.home'))


@blueprint.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", 'info')
    return redirect(url_for('public.home'))


@blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if current_user and current_user.is_authenticated():
        flash("You already have an account.", 'info')
        return redirect(url_for('public.home'))

    if form.validate_on_submit():
        new_user = User.create(username=form.username.data,
                               email=form.email.data,
                               password=form.password.data)
        send_confirmation_email(new_user)
        flash("Your account has been created. Please check your inbox for an activation email.", 'warning')
        return redirect(url_for('public.home'))
    return render_template('users/register.html', form=form)


@blueprint.route("/activate/<token>")
def activate(token):
    user = User.query.filter_by(activation_token=token).first()
    if not user:
        flash("You tried to use an invalid confirmation link. If this was an accident, please resend one.", 'danger')
        return redirect(url_for('public.home'))
    else:
        user.activate()
        flash("Your account has been activated.", 'success')
        return redirect(url_for('public.home'))


@blueprint.route("/login_help", methods=["GET"])
def login_help(resendForm=None, passwordForm=None):
    if not resendForm:
        resendForm = ResendConfirmationForm()

    if not passwordForm:
        passwordForm = ForgotPasswordForm()
    return render_template('users/login_help.html',
                            resendForm=resendForm, passwordForm=passwordForm)


@blueprint.route("/resend", methods=["POST"])
def resend():
    resendForm = ResendConfirmationForm()
    if resendForm.validate_on_submit():
        user = resendForm.user
        send_confirmation_email(user)
        flash("Account confirmation email has been sent!", "info")
        return redirect(url_for('public.home'))
    else:
        return login_help(resendForm=resendForm)


@blueprint.route("/send_reset", methods=["POST"])
def send_password_reset():
    passwordForm = ForgotPasswordForm()
    if passwordForm.validate_on_submit():
        send_password_reset_email(passwordForm.user)
        flash("An email to reset your password has been sent to your inbox.", "info")
        return redirect(url_for('public.home'))
    else:
        return login_help(passwordForm=passwordForm)


@blueprint.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.query.filter_by(password_reset_token=token).first()

    if not user:
        flash("The link to reset your password is invalid.", 'warning')
        return redirect(url_for('public.home'))

    if not user.password_reset_expiration > datetime.utcnow():
        flash("The link to reset your password has expired.", 'warning')
        return redirect(url_for('users.login_help'))

    else:
        form = ResetPasswordForm()
        if form.validate_on_submit():
            if user.check_password(form.password.data):
                flash("You cannot use the same password. Please use a different \
                      password.", 'warning')
                return redirect(url_for('users.reset_password',
                                         token=token,
                                         form=ResetPasswordForm()))

            user.set_password(form.password.data)
            user.password_reset_expiration = datetime.utcnow()
            user.save()
            flash("Your password has been reset.", 'success')
            return redirect(url_for('public.home'))
        return render_template('users/reset_password.html', form=form)


@login_manager.user_loader
def load_user(id):
    return User.get_by_id(int(id))