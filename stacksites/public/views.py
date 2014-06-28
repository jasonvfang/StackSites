# -*- coding: utf-8 -*-
import random
import mimetypes
import requests
from flask import (Blueprint, request, render_template, flash,
                   url_for, redirect, session, jsonify, Response, make_response, current_app, abort)
from flask.ext.login import login_user, login_required, logout_user, current_user

from stacksites.users.forms import LoginForm
from stacksites.users.models import User
from stacksites.utils import is_auth, is_post_and_valid
from stacksites.sites.forms import NewSiteForm
from stacksites.sites.utils import update_temp_in_s3, make_s3_path_for_temp, make_s3_path
from stacksites.sites.models import Site

blueprint = Blueprint('public', __name__, static_folder="../static")


def view_site_home(username, filename):

    if filename is not None:
        user = User.query.filter_by(username=username).first()
        
        if '.' in filename:
            
            if request.referrer is None:
                abort(404)

            ref = request.referrer.split('/')
            site_name = ref[-1] or 'home'
            
            site = filter(lambda site: site.name == site_name, user.sites)

            if not site:
                abort(404)
            else:
                site = site[0]

            if current_app.debug:
                return redirect(url_for('sites.view_file', username=username, site_id=site.id, filename=filename))
            else:
                return redirect(url_for('sites.view_file', username=username, site_id=site.id, filename=filename, _scheme='https', _external=True))
        
        else:
            site = filter(lambda site: site.name == filename, user.sites)

            if site:
                target = make_s3_path(username, filename, 'index.html')
                return make_response(requests.get(target).content)
            else:
                abort(404)

    site_name = 'home'
    target = make_s3_path(username, site_name, 'index.html')
    return make_response(requests.get(target).content)


def home():
    if is_auth():
        return redirect(url_for('public.user_dashboard'))
    form = LoginForm()

    if session.get('temp_file_id') is None:
        session['create_new_temp_file'] = True
        session['temp_file_id'] = '%030x' % random.randrange(16**30)

    return render_template('public/index.html', loginForm=form)


def save_temp_file(temp_file_id):
    file_data = request.json.get('data')

    from stacksites.sites.utils import upload_to_s3
    update_temp_in_s3(temp_file_id, file_data)

    session['create_new_temp_file'] = ''

    return jsonify({'status': 'success'})


def view_temp_file(temp_file_id):
    s3_path = make_s3_path_for_temp(temp_file_id)
    mimetype = mimetypes.guess_type(s3_path)[0]
    return Response(response=requests.get(s3_path).content, mimetype=mimetype)


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
