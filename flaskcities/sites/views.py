# -*- coding: utf-8 -*-
import ipdb
import requests as r
from flask import Blueprint, render_template, render_template_string, url_for, redirect, send_file

from flaskcities.public.forms import NewSiteForm
from .utils import upload_to_s3, get_index
from flaskcities.utils import flash_errors

blueprint = Blueprint('sites', __name__, url_prefix='/sites', 
                      template_folder='../templates')


@blueprint.route('/new', methods=['POST'])
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
        
        
@blueprint.route('/<site>')
def view_site(site):
    return render_template_string(r.get(get_index(site)).text)
    
        