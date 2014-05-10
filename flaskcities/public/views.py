# -*- coding: utf-8 -*-
from flask import (Blueprint, request, render_template, flash,
                   url_for, redirect)
from flask.ext.login import login_user, login_required, logout_user, current_user

from flaskcities.users.forms import LoginForm
from flaskcities.utils import is_auth, is_post_and_valid
from flaskcities.sites.forms import NewSiteForm
from flaskcities.sites.models import Site

blueprint = Blueprint('public', __name__, static_folder="../static")


@blueprint.route("/", methods=["GET"])
def home():
    if is_auth():
        return redirect(url_for('public.user_dashboard'))
    form = LoginForm()
    return render_template('public/index.html', loginForm=form)


@blueprint.route("/dash", methods=["GET", "POST"])
@login_required
def user_dashboard():
    form = NewSiteForm()
    if is_post_and_valid(form):
        site = Site(form.name.data, current_user)
        site.save()
        if form.notify:
            for notification in form.notify:
                flash(notification[0], notification[1])
        return redirect(url_for('public.user_dashboard'))
    return render_template('public/dash.html', form=form)
