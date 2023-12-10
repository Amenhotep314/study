from flask_login import current_user
from functools import cache

from . import db
from . import util
from .models import *


@cache
def current_semester():

    semesters = Semester.query.filter_by(user_id=current_user.id).all()
    if not semesters:
        return None
    now = util.utc_now()
    semesters.sort(reverse=True, key = lambda x: x.start_datetime)

    for semester in semesters:
        start = util.utc_datetime_from_naive_utc_datetime(semester.start_datetime)
        end = util.utc_datetime_from_naive_utc_datetime(semester.end_datetime)
        if (start <= now) and (now <= end):
            return semester

    return semesters[0]


@cache
def current_courses():

    courses = Course.query.filter_by(user_id=current_user.id, semester_id=current_semester().id).all()
    return courses


@cache
def current_assignments(*courses, past=False):

    if courses:
        assignments = []
        for course in courses:
            assignments.extend(Assignment.query.filter_by(user_id=current_user.id, course_id=course.id, completed=past).all())
    else:
        assignments = Assignment.query.filter_by(user_id=current_user.id, completed=past).all()

    assignments.sort(key=lambda x: x.due_datetime, reverse=True)
    return assignments


def active_assignments(*courses):

    assignments = current_assignments(courses) if courses else current_assignments()
    ans = []
    now = util.utc_now()

    for assignment in assignments:
        if util.utc_datetime_from_naive_utc_datetime(assignment.due_datetime) <= now:
            ans.append(assignment)

    return assignments


def overdue_assignments(*courses):

    assignments = current_assignments(courses) if courses else current_assignments()
    ans = []
    now = util.utc_now()

    for assignment in assignments:
        if util.utc_datetime_from_naive_utc_datetime(assignment.due_datetime) > now:
            ans.append(assignment)

    return assignments


def start_study_session(course, assignment=None):

    stop_study_session()
    if assignment:
        assignment_id = assignment.id
    else:
        assignment_id = None

    new_study_session = StudySession(
        user_id = current_user.id,
        semester_id = current_semester().id,
        course_id = course.id,
        assignment_id=assignment_id,
        start_datetime = util.utc_now()
    )

    db.session.add(new_study_session)
    db.session.commit()


def stop_study_session():

    # There should never be more than one open at once, but let's be sure:
    study_sessions = StudySession.query.filter_by(user_id=current_user.id, end_datetime=None).all()
    for study_session in study_sessions:
        study_session.end_datetime = util.utc_now()

    db.session.commit()
    invalidate_caches("current_study_session")


@cache
def current_study_session():

    study_session = StudySession.query.filter_by(user_id=current_user.id, end_datetime=None).first()
    return study_session


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

    study_sessions = StudySession.query.filter_by(user_id=current_user.id, semester_id=semester.id).all()
    for study_session in study_sessions:
        deep_delete_study_session(study_session)

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
    invalidate_caches("current_assignments")


def deep_delete_study_session(study_session):

    db.session.delete(study_session)
    db.session.commit()
    invalidate_caches("current_study_session")


def invalidate_caches(*args):

    names = args if args else globals().keys
    for func in names:
        try:
            globals()[func].cache_clear()
        except:
            pass