from flask_wtf import FlaskForm
from flask_login import current_user
from flask_babel import _, lazy_gettext as _l
import wtforms
from wtforms.validators import *
from werkzeug.security import check_password_hash

from .models import *


# Custom Validators
class EmailUnique(object):

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        email = field.data
        user = User.query.filter_by(email=email).first()
        if user:
            if not self.message:
                self.message = _l("A user with that email already exists.")
            raise wtforms.ValidationError(message=self.message)


class EmailUniqueLoggedIn(object):

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        email = field.data
        user = User.query.filter_by(email=email).first()
        if user and user.email!=current_user.email:
            if not self.message:
                self.message = _l("A user with that email already exists.")
            raise wtforms.ValidationError(message=self.message)


class EmailExists(object):

    def __init__(self, message=None):
        self.message = message
    def __call__(self, form, field):
        email = field.data
        user = User.query.filter_by(email=email).first()
        if not user:
            if not self.message:
                self.message = _l("Please check your email address and try again.")
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
                    self.message = _l("Invalid password. Please try again.")
                raise wtforms.ValidationError(message=self.message)


class DateAfter(object):

    def __init__(self, other, message=None):
        self.other = other
        self.message = message

    def __call__(self, form, field):
        other = form[self.other]
        if not (field.data.toordinal() > other.data.toordinal()):
            if not self.message:
                self.message = _l("%(this_field)s must be later than %(other_field)s.", this_field=field.label.text, other_field=other.label.text)
            raise wtforms.ValidationError(message=self.message)


class GreaterThan(object):

    def __init__(self, value, message=None):
        self.value = value
        self.message = message

    def __call__(self, form, field):
        if not (float(field.data) > self.value):
            if not self.message:
                self.message = _l("%(field)s must be greater than %(value)s.", field=field.label.text, value=str(self.value))
            raise wtforms.ValidationError(message=self.message)


class LessThan(object):

    def __init__(self, value, message=None):
        self.value = value
        self.message = message

    def __call__(self, form, field):
        if not (float(field.data) < self.value):
            if not self.message:
                self.message = _l("%(field)s must be less than %(value)s.", field=field.label.text, value=str(self.value))
            raise wtforms.ValidationError(message=self.message)


# Forms
class SignUp(FlaskForm):

    email = wtforms.EmailField(_l("Email"), validators=[
        InputRequired(_l("Please fill out this field.")),
        Email(_l("Please enter an email.")),
        EmailUnique()
    ])
    firstname = wtforms.StringField(_l("First Name"), validators=[
        InputRequired(_l("Please fill out this field.")),
        Length(max=100, message=_l("Please enter something shorter."))
    ])
    lastname = wtforms.StringField(_l("Last Name"), validators=[
        InputRequired(_l("Please fill out this field.")),
        Length(max=100, message=_l("Please enter something shorter."))
    ])
    password = wtforms.PasswordField(_l("Password"), validators=[
        InputRequired(_l("Please fill out this field.")),
        Length(min=8, max=100, message=_l("Please enter a value between %(min)d and %(max)d characters long."))
    ])
    password_confirm = wtforms.PasswordField(_l("Confirm Password"), validators=[
        InputRequired(_l("Please fill out this field.")),
        EqualTo('password', message=_l("Inputs must match."))
    ])
    timezone = wtforms.SelectField(_l("Timezone"), validators=[InputRequired(_l("Please fill out this field."))])
    language = wtforms.SelectField(_l("Language"), validators=[InputRequired(_l("Please fill out this field."))])


class LogIn(FlaskForm):

    email = wtforms.EmailField(_l("Email"), validators=[InputRequired(_l("Please fill out this field.")), EmailExists()])
    password = wtforms.PasswordField(_l("Password"), validators=[InputRequired("Please fill out this field."), PasswordValid()])
    remember = wtforms.BooleanField(_l("Remember login?"))


class SettingsForm(FlaskForm):

    email = wtforms.EmailField(_l("Email"), validators=[
        InputRequired(_l("Please fill out this field.")),
        Email(_l("Please enter an email.")),
        EmailUniqueLoggedIn()
    ])
    firstname = wtforms.StringField(_l("First Name"), validators=[
        InputRequired(_l("Please fill out this field.")),
        Length(max=100, message=_l("Please enter something shorter."))
    ])
    lastname = wtforms.StringField(_l("Last Name"), validators=[
        InputRequired(_l("Please fill out this field.")),
        Length(max=100, message=_l("Please enter something shorter."))
    ])
    timezone = wtforms.SelectField(_l("Timezone"), validators=[InputRequired(_l("Please fill out this field."))])
    language = wtforms.SelectField(_l("Language"), validators=[InputRequired(_l("Please fill out this field."))])


class ChangePasswordForm(FlaskForm):

    password = wtforms.PasswordField(_l("New Password"), validators=[
        InputRequired(_l("Please fill out this field.")),
        Length(min=8, max=100, message=_l("Please enter a value between %(min)d and %(max)d characters long."))
    ])
    password_confirm = wtforms.PasswordField(_l("Confirm New Password"), validators=[
        InputRequired(_l('Please fill out this field.')),
        EqualTo('password', message=_l('Inputs must match.'))
    ])


class ToDoForm(FlaskForm):

    name = wtforms.StringField(_l("Name"), validators=[
        InputRequired(_l('Please fill out this field.')),
        Length(max=100, message=_l('Please enter something shorter.'))
    ])
    description = wtforms.StringField(_l("Description"), validators=[Length(max=100, message=_l('Please enter something shorter.'))])
    finish_datetime = wtforms.DateField(_l("Finish by Date"), validators=[Optional()])
    completed = wtforms.BooleanField(_l("Complete"))


class SemesterForm(FlaskForm):

    name = wtforms.StringField(_l("Name"), validators=[
        InputRequired(_l('Please fill out this field.')),
        Length(max=100, message=_l('Please enter something shorter.'))
    ])
    start_datetime = wtforms.DateField(_l("Start Date"), validators=[InputRequired(_l('Please fill out this field.'))])
    end_datetime = wtforms.DateField(_l("End Date"), validators=[InputRequired(_l('Please fill out this field.')), DateAfter("start_datetime")])


class CourseForm(FlaskForm):

    name = wtforms.StringField(_l("Name"), validators=[
        InputRequired(_l('Please fill out this field.')),
        Length(max=100, message=_l('Please enter something shorter.'))
    ])
    short_name = wtforms.StringField(_l("Short Name"), validators=[Length(max=100, message=_l('Please enter something shorter.'))])
    credits = wtforms.IntegerField(_l("Credits"), validators=[InputRequired(_l('Please fill out this field.'))])
    semester = wtforms.SelectField(_l("Semester"), choices=[], coerce=int, validate_choice=False, validators=[InputRequired(_l('Please fill out this field.'))])


class AssignmentForm(FlaskForm):

    name = wtforms.StringField(_l("Name"), validators=[
        InputRequired(_l('Please fill out this field.')),
        Length(max=100, message=_l('Please enter something shorter.'))
    ])
    due_date = wtforms.DateField(_l("Due Date"), validators=[InputRequired(_l('Please fill out this field.'))])
    due_time = wtforms.TimeField(_l("Due Time"), validators=[Optional()])
    completed = wtforms.BooleanField(_l("Complete"))
    course = wtforms.SelectField(_l("Course"), choices=[], coerce=int, validate_choice=False, validators=[InputRequired(_l('Please fill out this field.'))])


class SelectStudyForm(FlaskForm):

    choice = wtforms.SelectField(_l("Choice"), choices=[], coerce=int, validate_choice=False, validators=[InputRequired(_l('Please fill out this field.'))])


class ConfirmDelete(FlaskForm):

    confirmation = wtforms.StringField(_l("Confirmation"), validators=[
        InputRequired(_l('Please fill out this field.')),
        AnyOf([_l("I understand.")], message=_l('You must enter "I understand." to proceed.'))
    ])