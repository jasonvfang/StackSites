# -*- coding: utf-8 -*-
import requests as r
import mimetypes
from werkzeug import secure_filename
from flask.ext.login import login_required, current_user
from flask import Response, Blueprint, render_template, url_for, redirect, make_response, request, jsonify, flash, current_app

from .forms import NewSiteForm, UploadFilesForm, CreateFolderForm
from .models import Site
from .utils import upload_to_s3, make_s3_path, owns_site, delete_s3_file, get_keys, create_folder_in_s3
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
            return redirect(url_for('sites.view_file', username=username, site_id=site.id, key=site_name, _scheme='https', _external=True))
        else:
            return redirect(url_for('sites.view_file', username=username, site_id=site.id, key=site_name))
    target = make_s3_path(username, site_name, 'index.html')
    return make_response(r.get(target).text)


def manage_site(site_id, folder_key=None, upload_form=None, create_folder_form=None):
    site = Site.get_by_id(site_id)
    owns_site(site)

    if upload_form is None:
        upload_form = UploadFilesForm()

    if create_folder_form is None:
        create_folder_form = CreateFolderForm()

    paths = None
    if folder_key:
        path_elems = [e for e in folder_key.split('/') if e]
        paths = [{elem: '/'.join(path_elems[:ind + 1])} for ind, elem in enumerate(path_elems)]
        paths = paths[2:]

    return render_template('sites/manage.html', site=site, upload_form=upload_form, create_folder_form=create_folder_form, image_exts=IMAGE_EXTS, folder_key=folder_key, paths=paths)


def manage_site_folder(*args, **kwargs):
    return manage_site(*args, **kwargs)


def upload(site_id, folder_key=None):
    site = Site.get_by_id(site_id)
    owns_site(site)
    form = UploadFilesForm()

    if form.validate_on_submit():
        files = request.files.getlist('files')

        for file in files:
            filename = folder_key + secure_filename(file.filename) if folder_key is not None else secure_filename(file.filename)
            upload_to_s3(file, current_user.username, site.name, filename)
        return redirect(url_for('sites.manage_site_folder', site_id=site_id, folder_key=folder_key))

    else:
        return manage_site_folder(site_id, upload_form=form, folder_key=folder_key)


def upload_in_folder(*args, **kwargs):
    return upload(*args, **kwargs)


def edit_file(site_id, key):
    site = Site.get_by_id(site_id)
    owns_site(site)
    s3_path = make_s3_path(current_user.username, site.name, key)
    return render_template('sites/edit.html', s3_path=s3_path, key=key, site=site, fname=key.split('/')[-1])


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


def view_file(username, site_id, key):
    site = Site.get_by_id(site_id)
    s3_path = make_s3_path(username, site.name, key)
    mimetype = mimetypes.guess_type(key)[0]
    return Response(response=r.get(s3_path).content, mimetype=mimetype)


def delete_file(site_id, folder_key):
    site = Site.get_by_id(site_id)
    owns_site(site)

    delete_s3_file(site.user.username, site.name, folder_key)

    folder_key = '/'.join(folder_key.split('/')[:-1]) + '/'
    return redirect(url_for('sites.manage_site_folder', site_id=site_id, folder_key=folder_key))


def _delete_folder(username, site_name, folder_key):
    for file_key in get_keys(username, site_name, folder_key):
        if file_key.name[-1] == '/':
            _delete_folder(username, site_name, file_key.name)
        else:
            delete_s3_file(username, site_name, file_key.name)

    delete_s3_file(username, site_name, folder_key)


def delete_folder(site_id, folder_key):
    site = Site.get_by_id(site_id)
    owns_site(site)

    username = site.user.username
    site_name = site.name

    _delete_folder(username, site_name, folder_key)

    folder_key = '/'.join(folder_key.split('/')[:-2]) + '/'
    return redirect(url_for('sites.manage_site_folder', site_id=site_id, folder_key=folder_key))


def delete_site(site_id):
    site = Site.get_by_id(site_id)
    owns_site(site)
    name = site.name
    site.delete_site()
    flash("Your site '{0}' has been permanently deleted.".format(name), 'info')
    return redirect(url_for('public.user_dashboard'))


def create_folder(site_id):
    site = Site.get_by_id(site_id)
    owns_site(site)

    form = CreateFolderForm()
    
    folder_key = '{}/{}'.format(site.user.username, site.name)
    if form.validate_on_submit():
        create_folder_in_s3(site.user.username, site.name, form.name.data, folder_key)
        return redirect(url_for('sites.manage_site', site_id=site.id))
    else:
        return manage_site(site_id=site_id, create_folder_form=form)


def create_folder_in_folder(site_id, folder_key):
    site = Site.get_by_id(site_id)
    owns_site(site)

    form = CreateFolderForm()

    if form.validate_on_submit():
        create_folder_in_s3(site.user.username, site.name, form.name.data, folder_key)
        folder_key = '/'.join(folder_key.split('/')[:-1]) + '/'
        return redirect(url_for('sites.manage_site_folder', site_id=site.id, folder_key=folder_key))
    else:
        return manage_site_folder(site_id=site_id, folder_key=folder_key, create_folder_form=form)
