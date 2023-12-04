from flask_login import current_user
from datetime import date
from functools import cache

from . import db
from . import util
from .models import *


@cache
def current_semester():

    semesters = Semester.query.filter_by(user_id=current_user.id).all()
    if not semesters:
        return None

    now = datetime.now(tz=util.current_user_timezone()).date().toordinal()
    semesters.sort(reverse=True, key = lambda x: x.end_date.toordinal())
    for semester in semesters:
        if semester.start_date.date().toordinal() <= now <= semester.end_date.date().toordinal():
            return semester

    return semesters[0]


@cache
def current_courses():

    courses = Course.query.filter_by(user_id=current_user.id, semester_id=current_semester().id).all()
    return courses



def deep_delete_current_user():

    semesters = Semester.query.filter_by(user_id=current_user.id).all()
    for semester in semesters:
        deep_delete_semester(semester)

    db.session.delete(current_user)
    db.session.commit()
    invalidate_caches()


def deep_delete_semester(semester):

    courses = Course.query.filter_by(user_id=current_user.id, semester_id=semester.id).all()
    for course in courses:
        deep_delete_course(course)

    db.session.delete(semester)
    db.session.commit()
    invalidate_caches("current_semester")


def deep_delete_course(course):

    assignments = Assignment.query.filter_by(user_id=current_user.id, course_id=course.id)
    for assignment in assignments:
        deep_delete_assignment(assignment)

    db.session.delete(course)
    db.session.commit()
    invalidate_caches("current_courses")


def deep_delete_assignment(assignment):

    db.session.delete(assignment)
    db.session.commit()


def invalidate_caches(*args):

    names = args if args else globals().keys
    for func in names:
        try:
            globals()[func].cache_clear()
        except:
            pass