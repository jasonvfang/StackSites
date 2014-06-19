# -*- coding: utf-8 -*-
import re

from flask_wtf import Form
from flask.ext.login import current_user
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired

from .models import Site
from stacksites.form_utils import has_upper_nonalpha

EXTRA_WHITESPACE = "The site name you entered had an extra space (which was removed). If you don't know what that means, then don't worry."

ALLOWED_FILE_EXTS = [
    'jpg', 'png', 'svg', 'gif', 'bmp', 'webp',
    'html', 'js', 'css'
]

FILES_ALLOWED_MSG = 'You can only upload files with one of the following extensions:\n' + ' '.join(ALLOWED_FILE_EXTS)


class NewSiteForm(Form):
    name = TextField('Name', validators=[DataRequired('You have to enter a name for your site.'),
                                         Length(min=3, max=20, message='The site name must be between 3 and 20 characters long.')])

    notify = []

    def validate(self):
        initial_validation = super(NewSiteForm, self).validate()
        if not initial_validation:
            return False

        if ' ' in self.name.data:
            self.notify.append((EXTRA_WHITESPACE, 'info'))
            self.name.data = self.name.data.strip()

        if not self.name.data:
            self.name.errors.append('The site name cannot be made entirely of spaces.')
            return False

        results = has_upper_nonalpha(self.name.data, 'site name')
        if results:
            self.name.errors.extend(results)
            return False

        matching_sites = filter(lambda site: site.name == self.name.data, current_user.sites)
        if len(matching_sites) > 0:
            self.name.errors.append('A site with that name already exists under your account.')
            return False
        return True

    def __repr__(self):
        return "<NewSiteForm ({0})>".format(self.name)


class UploadFilesForm(Form):
    files = FileField('files', validators=[FileRequired("You must select a file."),
                                           FileAllowed(ALLOWED_FILE_EXTS, FILES_ALLOWED_MSG)])
