# -*- coding: utf-8 -*-
from flask import (Blueprint, request, render_template, flash,
                   url_for, redirect)
from flask.ext.login import login_user, login_required, logout_user, current_user

from flaskcities.users.forms import LoginForm

blueprint = Blueprint('public', __name__, static_folder="../static")


@blueprint.route("/", methods=["GET"])
def home():
    form = LoginForm()
    return render_template('public/index.html', loginForm=form)