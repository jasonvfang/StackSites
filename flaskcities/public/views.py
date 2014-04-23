# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, url_for, redirect

from forms import NewSiteForm

blueprint = Blueprint('public', __name__)

@blueprint.route('/')
def home():
    form = NewSiteForm()
    return render_template('public/home.html', form=form)