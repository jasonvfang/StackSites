# -*- coding: utf-8 -*-
import ipdb
import requests as r
from flask.ext.login import login_required
from flask import Blueprint, render_template, render_template_string, url_for, redirect, send_file

from .forms import NewSiteForm
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
    return render_template_string(r.get(target).text)
    
        