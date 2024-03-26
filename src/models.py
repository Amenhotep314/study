from flask_login import UserMixin

from . import db
from . import util


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime)

    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(500))
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    timezone = db.Column(db.String(100), default="Canada/Eastern")
    language = db.Column(db.String(2), default="en")
    theme = db.Column(db.String(100), default="greensboro_winter")


class ToDo(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime)

    user_id = db.Column(db.Integer)

    name = db.Column(db.String(100))
    description = db.Column(db.String(100))
    finish_datetime = db.Column(db.DateTime)
    completed = db.Column(db.Boolean)


class Semester(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime)

    user_id = db.Column(db.Integer)

    name = db.Column(db.String(100))
    start_datetime = db.Column(db.DateTime)
    end_datetime = db.Column(db.DateTime)


class Course(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime)

    user_id = db.Column(db.Integer)
    semester_id = db.Column(db.Integer)

    name = db.Column(db.String(100))
    short_name = db.Column(db.String(100))
    credits = db.Column(db.Integer)
    color = db.Column(db.String(7))


class Assignment(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime)

    user_id = db.Column(db.Integer)
    course_id = db.Column(db.Integer)

    name = db.Column(db.String(100))
    due_datetime = db.Column(db.DateTime)
    # est_time = db.Column(db.Float)
    # importance = db.Column(db.Integer)
    completed = db.Column(db.Boolean)


class StudySession(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime)

    user_id = db.Column(db.Integer)
    semester_id = db.Column(db.Integer)
    course_id = db.Column(db.Integer)
    assignment_id = db.Column(db.Integer, default=None)

    start_datetime = db.Column(db.DateTime)
    end_datetime = db.Column(db.DateTime, default=None)