# -*- coding: utf-8 -*-
from flask import (Blueprint, request, render_template, flash,
                   url_for, redirect)
from flask.ext.login import login_user, login_required, logout_user, current_user

from .forms import RegisterForm, LoginForm
from .models import User
from flaskcities.extensions import login_manager

blueprint = Blueprint('users', __name__, url_prefix='/users')


@blueprint.route("/login", methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user)
        flash("You are logged in!", 'success')
        redirect_url = request.args.get('next') or url_for('public.home')
        return redirect(redirect_url)
    else:
        flash('there was a problem', 'error')
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
        
        
        
@login_manager.user_loader
def load_user(id):
    return User.get_by_id(int(id))