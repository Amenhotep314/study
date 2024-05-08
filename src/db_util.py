from flask_login import current_user
from functools import cache
import datetime

from . import db
from . import util
from .models import *


def current_todos(past=False):

    todos = ToDo.query.filter_by(user_id=current_user.id, completed=past).all()
    if past:
        todos.sort(key=lambda x: x.finish_datetime if x.finish_datetime else x.created, reverse=True)
        return todos

    dated = list(filter(lambda x: bool(x.finish_datetime), todos))
    dated.sort(key=lambda x: x.finish_datetime)
    undated = list(filter(lambda x: not bool(x.finish_datetime), todos))
    undated.sort(key=lambda x: x.created)
    return dated + undated


def active_todos():

    todos = current_todos()
    ans = []
    now = util.utc_now()

    for todo in todos:
        if (not todo.finish_datetime) or (util.utc_datetime_from_naive_utc_datetime(todo.finish_datetime) > now):
            ans.append(todo)

    return ans


def overdue_todos():

    todos = current_todos()
    ans = []
    now = util.utc_now()

    for todo in todos:
        if todo.finish_datetime and util.utc_datetime_from_naive_utc_datetime(todo.finish_datetime) <= now:
            ans.append(todo)

    return ans


# @cache
def current_semester():

    semesters = Semester.query.filter_by(user_id=current_user.id).all()
    if not semesters:
        return None

    now = util.utc_now()
    semesters.sort(reverse=True, key = lambda x: x.end_datetime)
    if util.utc_datetime_from_naive_utc_datetime(semesters[0].end_datetime) < now:
        return None
    else:
        return semesters[0]


# @cache
def current_courses():

    courses = Course.query.filter_by(user_id=current_user.id, semester_id=current_semester().id).all()
    courses.sort(key=lambda x: x.name)
    return courses


# @cache
def current_assignments(courses=None, past=False):

    if courses:
        assignments = []
        for course in courses:
            assignments.extend(Assignment.query.filter_by(user_id=current_user.id, course_id=course.id, completed=past).all())
    else:
        assignments = Assignment.query.filter_by(user_id=current_user.id, completed=past).all()

    assignments.sort(key=lambda x: x.due_datetime, reverse=past)
    return assignments


def active_assignments(courses=None):

    assignments = current_assignments(courses)
    ans = []
    now = util.utc_now()

    for assignment in assignments:
        if util.utc_datetime_from_naive_utc_datetime(assignment.due_datetime) > now:
            ans.append(assignment)

    return ans


def overdue_assignments(courses=None):

    assignments = current_assignments(courses)
    ans = []
    now = util.utc_now()

    for assignment in assignments:
        if util.utc_datetime_from_naive_utc_datetime(assignment.due_datetime) <= now:
            ans.append(assignment)

    return ans


def start_study_session(course, assignment=None):

    stop_study_session()
    if assignment:
        assignment_id = assignment.id
    else:
        assignment_id = None

    new_study_session = StudySession(
        created = util.utc_now(),
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


# @cache
def current_study_session():

    study_session = StudySession.query.filter_by(user_id=current_user.id, end_datetime=None).first()
    return study_session


def study_time(start_datetime=None, end_datetime=None, semesters=None, courses=None, assignments=None):

    assert sum(bool(x) for x in [semesters, courses, assignments]) <= 1
    if not start_datetime:
        start_datetime = current_user.created
        start_datetime = util.utc_datetime_from_naive_utc_datetime(start_datetime)
    if not end_datetime:
        end_datetime = util.utc_now()

    if semesters:
        ids = [semester.id for semester in semesters]
        study_sessions = StudySession.query.filter((StudySession.user_id==current_user.id) & (StudySession.end_datetime!=None) & (StudySession.start_datetime >= start_datetime) & (StudySession.start_datetime < end_datetime) & (StudySession.semester_id.in_(ids))).all()
    elif courses:
        ids = [course.id for course in courses]
        study_sessions = StudySession.query.filter((StudySession.user_id==current_user.id) & (StudySession.end_datetime!=None) & (StudySession.start_datetime >= start_datetime) & (StudySession.start_datetime < end_datetime) & (StudySession.course_id.in_(ids))).all()
    elif assignments:
        ids = [assignment.id for assignment in assignments]
        study_sessions = StudySession.query.filter((StudySession.user_id==current_user.id) & (StudySession.end_datetime!=None) & (StudySession.start_datetime >= start_datetime) & (StudySession.start_datetime < end_datetime) & (StudySession.assignment_id.in_(ids))).all()
    else:
        study_sessions = StudySession.query.filter((StudySession.user_id==current_user.id) & (StudySession.end_datetime!=None) & (StudySession.start_datetime >= start_datetime) & (StudySession.start_datetime < end_datetime)).all()

    total = datetime.timedelta(0)
    for study_session in study_sessions:
        total += study_session.end_datetime - study_session.start_datetime

    return total


def deep_delete_current_user():

    semesters = Semester.query.filter_by(user_id=current_user.id).all()
    for semester in semesters:
        deep_delete_semester(semester)

    todos = ToDo.query.filter_by(user_id=current_user.id).all()
    for todo in todos:
        deep_delete_todo(todo)

    db.session.delete(current_user)
    db.session.commit()
    invalidate_caches()


def deep_delete_todo(todo):

    db.session.delete(todo)
    db.session.commit()


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

    study_sessions = StudySession.query.filter_by(user_id=current_user.id, course_id=course.id).all()
    for study_session in study_sessions:
        deep_delete_study_session(study_session)

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

    names = args if args else globals().keys()
    for func in names:
        try:
            globals()[func].cache_clear()
        except:
            pass