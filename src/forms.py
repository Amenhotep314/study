from flask_wtf import FlaskForm
import wtforms
from wtforms import validators
from flask_login import current_user

from .models import *


class After(object):

    def __init__(self, other, message=None):
        self.other = other
        self.message = message

    def __call__(self, form, field):
        other = form[self.other]
        if not (field.data.toordinal() > other.data.toordinal()):
            if not self.message:
                self.message = field.gettext(field.label.text + " must be later than " + other.label.text + ".")
            raise wtforms.ValidationError(message=self.message)


class SemesterForm(FlaskForm):

    name = wtforms.StringField("Name", validators=[validators.InputRequired()])
    start_date = wtforms.DateField("Start Date", validators=[validators.InputRequired()])
    end_date = wtforms.DateField("End Date", validators=[validators.InputRequired(), After("start_date")])