# -*- coding: utf-8 -*-
import ipdb
import requests as r
from werkzeug import secure_filename
from flask.ext.login import login_required, current_user
from flask import Blueprint, render_template, url_for, redirect, make_response, request, jsonify

from .forms import NewSiteForm
from .models import Site
from .utils import upload_to_s3, make_s3_path
from flaskcities.utils import flash_errors

blueprint = Blueprint('sites', __name__, url_prefix='/sites', 
                      template_folder='../templates')


@blueprint.route('/new', methods=['POST'])
@login_required
def new_site():
    form = NewSiteForm()
    if form.validate_on_submit():
        name = form.name.data
        index = blueprint.open_resource('../templates/new_site.html')
        if index is not None:
            upload_to_s3(index, name, 'index.html')
        else:
            raise Exception, "Could not upload index resource to S3"
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
        return redirect(url_for('public.home'))
        
        
@blueprint.route('/<username>/<site_name>')
def view_site(username, site_name):
    target = make_s3_path(username, site_name, 'index.html')
    print 'view_site', target
    return make_response(r.get(target).text)


@blueprint.route('/manage/<int:site_id>', methods=['GET'])
def manage_site(site_id):
    site = Site.get_by_id(site_id)
    if site is None:
        flash('That site does not exist', 'error')
        return redirect(url_for('public.user_dashboard'))
    return render_template('sites/manage.html', site=site)

    
@blueprint.route('/upload/<int:site_id>', methods=['POST'])
def upload(site_id):
    site = Site.get_by_id(site_id)
    files = request.files.getlist("files[]")
    print 'files', files
    for file in files:
        print 'upload type', type(file)
        filename = secure_filename(file.filename)
        upload_to_s3(file, current_user.username, site.name, filename)
    return redirect(url_for('sites.manage_site', site_id=site_id))


@blueprint.route('/edit/<int:site_id>/<filename>')
def edit_file(site_id, filename):
    site = Site.get_by_id(site_id)
    s3_path = make_s3_path(current_user.username, site.name, filename)
    return render_template('sites/edit.html', s3_path=s3_path, filename=filename,
                            site=site)


@blueprint.route('/save/<int:site_id>')
def save_file(site_id):
    filename = request.args.get('filename')
    file_data = request.args.get('data')
    site_name = request.args.get('site_name')
    try:
        upload_to_s3(file_data, current_user.username,
                     site_name, filename, set_contents_from_str=True)
        return jsonify({'status': 'success'})
    except Exception, e:
        return jsonify({'status': 'error', 'error': str(e)})


@blueprint.route('/view/<int:site_id>/<filename>')
def view_file(site_id, filename):
    site = Site.get_by_id(site_id)
    s3_path = make_s3_path(current_user.username, site.name, filename)
    return make_response(r.get(s3_path).text)
