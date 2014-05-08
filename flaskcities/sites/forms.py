# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired


ALLOWED_FILE_EXTS = [
    'jpg', 'png', 'svg', 'gif', 'bmp', 'webp',
    'html', 'js', 'css'
]

FILES_ALLOWED_MSG = 'You can only upload files with one of the following extensions:\n' + ' '.join(ALLOWED_FILE_EXTS)


class NewSiteForm(Form):
    name = TextField('Name', validators=[DataRequired('You have to enter a name for your site.'),
                     Length(min=3, max=20)])
            
    def __repr__(self):
        return "<NewSiteForm ({0})>".format(self.name)


class UploadFilesForm(Form):
    files = FileField('files', validators=[FileRequired("You must select a file."),
                       FileAllowed(ALLOWED_FILE_EXTS, FILES_ALLOWED_MSG)])
