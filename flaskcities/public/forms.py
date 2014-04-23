from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired, EqualTo, Length


class NewSiteForm(Form):
    name = TextField('Name', validators=[DataRequired('You have to enter a \ name for your site.'),
                     Length(min=3, max=20)])
    def __init__(self, *args, **kwargs):
        super(NewSiteForm, self).__init__(*args, **kwargs)
    
    def validate(self):
        initial_validation = super(NewSiteForm, self).validate()
        if not initial_validation:
            return False
        return True
            
    def __repr__(self):
        return "<NewSiteForm ({0})>".format(self.name)