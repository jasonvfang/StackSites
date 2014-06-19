# -*- coding: utf-8 -*-
import random
import mimetypes
import requests
from flask import (Blueprint, request, render_template, flash,
                   url_for, redirect, session, jsonify, Response)
from flask.ext.login import login_user, login_required, logout_user, current_user

from stacksites.users.forms import LoginForm
from stacksites.users.models import User
from stacksites.utils import is_auth, is_post_and_valid
from stacksites.sites.forms import NewSiteForm
from stacksites.sites.utils import update_temp_in_s3, make_s3_path_for_temp
from stacksites.sites.models import Site

blueprint = Blueprint('public', __name__, static_folder="../static")


@blueprint.route("/", methods=["GET"])
def home():
    if is_auth():
        return redirect(url_for('public.user_dashboard'))
    form = LoginForm()

    if not session.get('temp_file_id'):
        session['create_new_temp_file'] = True
        session['temp_file_id'] = '%030x' % random.randrange(16**30)
    else:
        session['create_new_temp_file'] = ''

    return render_template('public/index.html', loginForm=form)


@blueprint.route("/save_temp/<temp_file_id>", methods=['POST'])
def save_temp_file(temp_file_id):
    temp_file_id = temp_file_id
    file_data = request.json.get('data')
    from stacksites.sites.utils import upload_to_s3
    update_temp_in_s3(temp_file_id, file_data)
    return jsonify({'status': 'success'})


@blueprint.route('/view_temp/<temp_file_id>')
def view_temp_file(temp_file_id):
    s3_path = make_s3_path_for_temp(temp_file_id)
    mimetype = mimetypes.guess_type(s3_path)[0]
    return Response(response=requests.get(s3_path).content, mimetype=mimetype)


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
