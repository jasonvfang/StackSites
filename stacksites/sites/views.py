# -*- coding: utf-8 -*-
import ipdb
import requests as r
import mimetypes
from werkzeug import secure_filename
from flask.ext.login import login_required, current_user
from flask import Response, Blueprint, render_template, url_for, redirect, make_response, request, jsonify, flash, current_app

from .forms import NewSiteForm, UploadFilesForm
from .models import Site
from .utils import upload_to_s3, make_s3_path, owns_site, delete_s3_file
from stacksites.utils import flash_errors

IMAGE_EXTS = ['jpg', 'png', 'svg', 'gif', 'bmp', 'webp']

blueprint = Blueprint('sites', __name__, url_prefix='/sites', template_folder='../templates')


def view_site(username, site_name):
    if '.' in site_name:
        from stacksites.users.models import User
        ref = request.referrer.split('/')
        ref_site_name = ref[-1]
        user = User.query.filter_by(username=username).first()
        site = [site for site in user.sites if site.name == ref_site_name][0]
        if not current_app.debug:
            return redirect(url_for('sites.view_file', username=username, site_id=site.id, path=site_name, _scheme='https', _external=True))
        else:
            return redirect(url_for('sites.view_file', username=username, site_id=site.id, path=site_name))
    target = make_s3_path(username, site_name, 'index.html')
    return make_response(r.get(target).text)


def manage_site(site_id, form=None):
    site = Site.get_by_id(site_id)
    owns_site(site)

    if form is None:
        form = UploadFilesForm()

    return render_template('sites/manage.html', site=site, form=form, image_exts=IMAGE_EXTS, folder_prefix=None)


def manage_site_folder(site_id, folder_prefix):
    site = Site.get_by_id(site_id)
    owns_site(site)

    return render_template('sites/manage.html', site=site, form=UploadFilesForm(), image_exts=IMAGE_EXTS, folder_prefix=folder_prefix)


def upload(site_id):
    site = Site.get_by_id(site_id)
    owns_site(site)
    form = UploadFilesForm()
    if form.validate_on_submit():
        files = request.files.getlist('files')
        for file in files:
            filename = secure_filename(file.filename)
            upload_to_s3(file, current_user.username, site.name, filename)
        return redirect(url_for('sites.manage_site', site_id=site_id))
    else:
        return manage_site(site_id, form)


def edit_file(site_id, filename):
    site = Site.get_by_id(site_id)
    owns_site(site)
    s3_path = make_s3_path(current_user.username, site.name, filename)
    return render_template('sites/edit.html', s3_path=s3_path, filename=filename, site=site)


def save_file(site_id):
    site = Site.get_by_id(site_id)
    owns_site(site)
    filename = request.json.get('filename')
    file_data = request.json.get('data')
    site_name = request.json.get('site_name')
    try:
        upload_to_s3(file_data, current_user.username, site_name, filename, set_contents_from_str=True)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})


def view_file(username, site_id, path):
    site = Site.get_by_id(site_id)
    s3_path = make_s3_path(username, site.name, path)
    mimetype = mimetypes.guess_type(path)[0]
    return Response(response=r.get(s3_path).content, mimetype=mimetype)


def delete_file(site_id, filename):
    site = Site.get_by_id(site_id)
    owns_site(site)
    delete_s3_file(site.user.username, site.name, filename)
    return redirect(url_for('sites.manage_site', site_id=site_id))


def delete_site(site_id):
    site = Site.get_by_id(site_id)
    owns_site(site)
    name = site.name
    site.delete_site()
    flash("Your site '{0}' has been permanently deleted.".format(name), 'info')
    return redirect(url_for('public.user_dashboard'))
