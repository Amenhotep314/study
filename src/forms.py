"""Implements classes to represent webforms. Also implements custom field validations to ensure that
good data is always submitted. With a couple exceptions, everything should be validated at the form
level.
"""

from flask_wtf import FlaskForm
from flask_login import current_user
from flask_babel import _, lazy_gettext as _l
import wtforms
from wtforms.validators import *
from werkzeug.security import check_password_hash

from .models import *


# Custom Validators
class EmailUnique(object):
    """Ensure that an email is not in the database."""
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
    """Ensure that an email is not in the database, unless it belongs to the current user. Useful for
    users changing their own email addresses.
    """
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
    """Ensures that an email is in the database."""
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
    """Ensures that a password matches the hash stored for the current user."""
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
    """Ensures that one date is later than another."""
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
    """Ensures that one field has a greater numerical value than another."""
    def __init__(self, value, message=None):
        self.value = value
        self.message = message

    def __call__(self, form, field):
        if not (float(field.data) > self.value):
            if not self.message:
                self.message = _l("%(field)s must be greater than %(value)s.", field=field.label.text, value=str(self.value))
            raise wtforms.ValidationError(message=self.message)


class LessThan(object):
    """Ensures that one field has a lesser numerical value than another."""
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
    """Form for new users to sign up for the website."""

    # Emails must be unique
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

    # Passwords must be at least 8 characters long
    password = wtforms.PasswordField(_l("Password"), validators=[
        InputRequired(_l("Please fill out this field.")),
        Length(min=8, max=100, message=_l("Please enter a value between %(min)d and %(max)d characters long."))
    ])
    # And the two password fields must match
    password_confirm = wtforms.PasswordField(_l("Confirm Password"), validators=[
        InputRequired(_l("Please fill out this field.")),
        EqualTo('password', message=_l("Inputs must match."))
    ])
    timezone = wtforms.SelectField(_l("Timezone"), validators=[InputRequired(_l("Please fill out this field."))])
    language = wtforms.SelectField(_l("Language"), validators=[InputRequired(_l("Please fill out this field."))])


class LogIn(FlaskForm):
    """Form for existing users to log in. Handles password verification."""

    email = wtforms.EmailField(_l("Email"), validators=[InputRequired(_l("Please fill out this field.")), EmailExists()])
    password = wtforms.PasswordField(_l("Password"), validators=[InputRequired("Please fill out this field."), PasswordValid()])
    # Try to store a cookie to preserve the session. At some point, I need a cookie policy.
    remember = wtforms.BooleanField(_l("Remember login?"))


class SettingsForm(FlaskForm):
    """Form for users to change the values the entered when they signed up."""

    # Email can only be their current email or something unique in the database
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

    # Assigned to a default at sign up, but configurable later
    theme = wtforms.SelectField(_l("Theme"), validators=[InputRequired(_l("Please fill out this field."))])


class ChangePasswordForm(FlaskForm):
    """Form for users to change their password."""

    password = wtforms.PasswordField(_l("New Password"), validators=[
        InputRequired(_l("Please fill out this field.")),
        Length(min=8, max=100, message=_l("Please enter a value between %(min)d and %(max)d characters long."))
    ])
    password_confirm = wtforms.PasswordField(_l("Confirm New Password"), validators=[
        InputRequired(_l('Please fill out this field.')),
        EqualTo('password', message=_l('Inputs must match.'))
    ])


class ToDoForm(FlaskForm):
    """Form to create and edit todo items."""

    name = wtforms.StringField(_l("Name"), validators=[
        InputRequired(_l('Please fill out this field.')),
        Length(max=100, message=_l('Please enter something shorter.'))
    ])

    # Optional fields, description and due date
    description = wtforms.StringField(_l("Description (optional)"), validators=[Length(max=100, message=_l('Please enter something shorter.'))])
    finish_datetime = wtforms.DateField(_l("Finish by Date (optional)"), validators=[Optional()])

    # For users to mark if the todo is already done
    completed = wtforms.BooleanField(_l("Complete?"))


class SemesterForm(FlaskForm):
    """Form to create and edit semesters."""

    name = wtforms.StringField(_l("Name"), validators=[
        InputRequired(_l('Please fill out this field.')),
        Length(max=100, message=_l('Please enter something shorter.'))
    ])

    # Must end after it starts
    start_datetime = wtforms.DateField(_l("Start Date"), validators=[InputRequired(_l('Please fill out this field.'))])
    end_datetime = wtforms.DateField(_l("End Date"), validators=[InputRequired(_l('Please fill out this field.')), DateAfter("start_datetime")])


class CourseForm(FlaskForm):
    """Form to create and edit courses."""

    name = wtforms.StringField(_l("Name"), validators=[
        InputRequired(_l('Please fill out this field.')),
        Length(max=100, message=_l('Please enter something shorter.'))
    ])
    short_name = wtforms.StringField(_l("Short Name (optional)"), validators=[Length(max=100, message=_l('Please enter something shorter.'))])
    credits = wtforms.IntegerField(_l("Credits"), validators=[InputRequired(_l('Please fill out this field.'))])

    # Optional color from a list of choices found in util.py. If left blank, will be set to default server-side.
    color = wtforms.SelectField(_l("Color"), choices=[], validate_choice=False, validators=[Optional()])
    semester = wtforms.SelectField(_l("Semester"), choices=[], coerce=int, validate_choice=False, validators=[InputRequired(_l('Please fill out this field.'))])


class AssignmentForm(FlaskForm):
    """Form to create and edit assignments."""

    name = wtforms.StringField(_l("Name"), validators=[
        InputRequired(_l('Please fill out this field.')),
        Length(max=100, message=_l('Please enter something shorter.'))
    ])
    due_date = wtforms.DateField(_l("Due Date"), validators=[InputRequired(_l('Please fill out this field.'))])

    # Due date is optional
    due_time = wtforms.TimeField(_l("Due Time (optional)"), validators=[Optional()])
    completed = wtforms.BooleanField(_l("Complete?"))

    # Course id must be an integer
    course = wtforms.SelectField(_l("Course"), choices=[], coerce=int, validate_choice=False, validators=[InputRequired(_l('Please fill out this field.'))])


class SelectStudyForm(FlaskForm):
    """Form to select a course or assignment to study."""

    choice = wtforms.SelectField(_l("Choice"), choices=[], coerce=int, validate_choice=False, validators=[InputRequired(_l('Please fill out this field.'))])


class ConfirmDelete(FlaskForm):
    """Form to ask a user to confirm that they want to delete something permenantly."""

    confirmation = wtforms.StringField(_l("Confirmation"), validators=[
        InputRequired(_l('Please fill out this field.')),
        AnyOf([_l("I understand.")], message=_l('You must enter "I understand." to proceed.'))
    ])