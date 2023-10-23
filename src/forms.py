from flask_wtf import FlaskForm
import wtforms
from wtforms.validators import *
from flask_login import current_user
from werkzeug.security import check_password_hash

from .models import *


class EmailUnique(object):

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        email = field.data
        user = User.query.filter_by(email=email).first()
        if user:
            if not self.message:
                self.message = "A user with that email already exists."
            raise wtforms.ValidationError(message=self.message)


class EmailExists(object):

    def __init__(self, message=None):
        self.message = message
    def __call__(self, form, field):
        email = field.data
        user = User.query.filter_by(email=email).first()
        if not user:
            if not self.message:
                self.message = "Please check your email address and try again."
            raise wtforms.ValidationError(message=self.message)


class PasswordValid(object):

    def __init__(self, message=None):
        self.message = message
    def __call__(self, form, field):
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            if not check_password_hash(user.password, field.data):
                if not self.message:
                    self.message = "Invalid password. Please try again."
                raise wtforms.ValidationError(message=self.message)


class DateAfter(object):

    def __init__(self, other, message=None):
        self.other = other
        self.message = message

    def __call__(self, form, field):
        other = form[self.other]
        if not (field.data.toordinal() > other.data.toordinal()):
            if not self.message:
                self.message = field.gettext(field.label.text + " must be later than " + other.label.text + ".")
            raise wtforms.ValidationError(message=self.message)


class SignUp(FlaskForm):

    email = wtforms.EmailField("Email", validators=[InputRequired(), Email(), EmailUnique()])
    firstname = wtforms.StringField("First Name", validators=[InputRequired(), Length(max=100)])
    lastname = wtforms.StringField("Last Name", validators=[InputRequired(), Length(max=100)])
    password = wtforms.PasswordField("Password", validators=[InputRequired(), Length(min=8, max=100)])
    password_confirm = wtforms.PasswordField("Confirm Password", validators=[InputRequired(), EqualTo('password')])


class LogIn(FlaskForm):

    email = wtforms.EmailField("Email", validators=[InputRequired(), EmailExists()])
    password = wtforms.PasswordField("Password", validators=[InputRequired(), PasswordValid()])
    remember = wtforms.BooleanField("Remember login?")


class SemesterForm(FlaskForm):

    name = wtforms.StringField("Name", validators=[InputRequired(), Length(max=100)])
    start_date = wtforms.DateField("Start Date", validators=[InputRequired()])
    end_date = wtforms.DateField("End Date", validators=[InputRequired(), DateAfter("start_date")])


class CourseForm(FlaskForm):

    name = wtforms.StringField("Name", validators=[InputRequired(), Length(max=100)])
    short_name = wtforms.StringField("Short Name", validators=[Length(max=100)])
    credits = wtforms.IntegerField("Credits", validators=[InputRequired()])
    semester = wtforms.SelectField("Semester", choices=[], coerce=int, validate_choice=False, validators=[InputRequired()])


class ConfirmDelete(FlaskForm):

    confirmation = wtforms.StringField("Confirmation", validators=[InputRequired(), AnyOf(["I understand."])])