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

    name = wtforms.StringField("Name", validators=[validators.InputRequired(), validators.Length(max=100)])
    start_date = wtforms.DateField("Start Date", validators=[validators.InputRequired()])
    end_date = wtforms.DateField("End Date", validators=[validators.InputRequired(), After("start_date")])


class CourseForm(FlaskForm):

    name = wtforms.StringField("Name", validators=[validators.InputRequired(), validators.Length(max=100)])
    short_name = wtforms.StringField("Short Name", validators=[validators.Length(max=100)])
    credits = wtforms.IntegerField("Credits", validators=[validators.InputRequired()])
    semester = wtforms.SelectField("Semester", choices=[], coerce=int, validate_choice=False, validators=[validators.InputRequired()])