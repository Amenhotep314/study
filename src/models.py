from flask_login import UserMixin
from datetime import datetime
import pytz

from . import db


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.now(pytz.utc))

    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    timezone = db.Column(db.String(100), default="Canada/Eastern")


class Semester(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.now(pytz.utc))

    user_id = db.Column(db.Integer)

    name = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)


class Course(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.now(pytz.utc))

    user_id = db.Column(db.Integer)
    semester_id = db.Column(db.Integer)

    name = db.Column(db.String(100))
    short_name = db.Column(db.String(100))
    credits = db.Column(db.Integer)


class Assignment(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.now(pytz.utc))

    user_id = db.Column(db.Integer)
    course_id = db.Column(db.Integer)

    name = db.Column(db.String(100))
    due_date = db.Column(db.Date)
    # est_time = db.Column(db.Float)
    # importance = db.Column(db.Integer)
    completed = db.Column(db.Boolean)