# -*- coding: utf-8 -*-
from flask import (Blueprint, request, render_template, flash,
                   url_for, redirect, session)
from flask.ext.login import login_user, login_required, logout_user, current_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime

from flaskcities.users.forms import (RegisterForm, LoginForm, ResendConfirmationForm,
                                     ForgotPasswordForm, ResetPasswordForm, ChangeEmailForm, ChangePasswordForm)
from flaskcities.users.utils import send_confirmation_email, send_password_reset_email
from flaskcities.extensions import login_manager
from flaskcities.utils import flash_errors
from flaskcities.users.models import User

blueprint = Blueprint('users', __name__, url_prefix='/users', static_folder="../static")


@blueprint.route('/settings', methods=['GET'])
def settings(emailForm=None, passwordForm=None):
    if emailForm is None:
        emailForm = ChangeEmailForm()
    if passwordForm is None:
        passwordForm = ChangePasswordForm()
    return render_template('users/settings.html', emailForm=emailForm,
                           passwordForm=passwordForm)


@blueprint.route('/change_email', methods=['POST'])
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        new_email = form.email.data
        current_user.email = new_email
        current_user.save()
        flash('Your email address has been changed to {0}'.format(new_email), 'success')
        return redirect(url_for('users.settings'))
    return settings(emailForm=form)


@blueprint.route('/change_password', methods=['POST'])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.set_password(form.new_password.data)
        current_user.save()
        flash('Your password has been changed.', 'success')
        return redirect(url_for('users.settings'))
    return settings(passwordForm=form)


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


@blueprint.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('public.home'))


@blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if current_user and current_user.is_authenticated():
        flash("You already have an account.", 'info')
        return redirect(url_for('public.home'))

    if form.validate_on_submit():
        temp_file_id = session.get('temp_file_id')
        new_user = User.create(username=form.username.data,
                               email=form.email.data,
                               password=form.password.data, temp_file_id=temp_file_id)
        send_confirmation_email(new_user)
        flash("Your account has been created. Please check your inbox for an activation email.", 'warning')
        if form.notify:
            for notification in form.notify:
                flash(notification[0], notification[1])
        return redirect(url_for('public.home'))
    return render_template('users/register.html', form=form)


@blueprint.route("/activate/<token>")
def activate(token):
    user = User.query.filter_by(activation_token=token).first()
    if user is None:
        flash("Invalid activation link.", 'danger')
        return redirect(url_for('users.login_help'))
    if user.active:
        return redirect(url_for('public.user_dashboard'))
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
    if not current_user.is_anonymous():
        flash('You cannot reset your password if you are already logged in.', 'info')
        return redirect(url_for('users.login_help'))
    else:
        form = ResetPasswordForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is None:
                flash('The email address you entered does not belong to any user.', 'danger')
                return redirect(url_for('users.reset_password',
                                        token=token,
                                        form=ResetPasswordForm()))
            if not user.reset_password(token) or not user.password_reset_expiration > datetime.utcnow():
                flash('Invalid or expired password reset token.', 'danger')
                return redirect(url_for('users.login_help'))

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
