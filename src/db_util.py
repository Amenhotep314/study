"""Miscellaneous utility functions for interacting with, reaeding from, and writing to the database."""

from flask_login import current_user
from functools import cache
import datetime

from . import db
from . import util
from .models import *


def current_todos(past=False):
    """Gets all todos that are not completed.
    Args:
        past: A boolean indicating whether to get past todos instead. Default False

    Returns:
        A list of ToDo objects
    """

    todos = ToDo.query.filter_by(user_id=current_user.id, completed=past).all()
    if past:
        # Sort completed todos by finish date if possible, otherwise by when they were created. Reverse it.
        todos.sort(key=lambda x: x.finish_datetime if x.finish_datetime else x.created, reverse=True)
        return todos

    # Isolate the todos with due dates and sort them by due date.
    dated = list(filter(lambda x: bool(x.finish_datetime), todos))
    dated.sort(key=lambda x: x.finish_datetime)
    # Isolate the todos without due dates and sort them by when they were created.
    undated = list(filter(lambda x: not bool(x.finish_datetime), todos))
    undated.sort(key=lambda x: x.created)
    return dated + undated


def active_todos():
    """Gets all todos that are not completed and have not passed their due date.

    Returns:
        A list of ToDo objects
    """

    todos = current_todos()
    ans = []
    now = util.utc_now()

    for todo in todos:
        # Get todos that either have no due date or have a future due date
        if (not todo.finish_datetime) or (util.utc_datetime_from_naive_utc_datetime(todo.finish_datetime) > now):
            ans.append(todo)

    return ans


def overdue_todos():
    """Gets all todos that are not completed and have passed their due date.

    Returns:
        A list of ToDo objects
    """
    todos = current_todos()
    ans = []
    now = util.utc_now()

    for todo in todos:
        # Get todos that have due dates that have passed
        if todo.finish_datetime and util.utc_datetime_from_naive_utc_datetime(todo.finish_datetime) <= now:
            ans.append(todo)

    return ans


# @cache
def current_semester():
    """Selects the best candidate for the current semester.

    Returns:
        A Semester object
    """

    semesters = Semester.query.filter_by(user_id=current_user.id).all()
    if not semesters:
        return None

    now = util.utc_now()
    semesters.sort(reverse=True, key = lambda x: x.end_datetime)
    # If the most recent semester has ended, return nothing.
    if util.utc_datetime_from_naive_utc_datetime(semesters[0].end_datetime) < now:
        return None
    else:
        return semesters[0]


# @cache
def current_courses():
    """Gets the user's current courses.

    Returns:
        A list of Course objects
    """

    courses = Course.query.filter_by(user_id=current_user.id, semester_id=current_semester().id).all()
    # Alphabetize them
    courses.sort(key=lambda x: x.name)
    return courses


# @cache
def current_assignments(courses=None, past=False):
    """Gets the user's incomplete assignments. Optionally gets completed assignments instead.
    Can be constrained by course.

    Args:
        courses: A list of Course objects to constrain the search. Default None
        past: A boolean indicating whether to get past assignments instead. Default False

    Returns:
        A list of Assignment objects
    """

    if courses:
        assignments = []
        for course in courses:
            assignments.extend(Assignment.query.filter_by(user_id=current_user.id, course_id=course.id, completed=past).all())
    else:
        assignments = Assignment.query.filter_by(user_id=current_user.id, completed=past).all()

    # Sort by due date, soonest if they are current, latest if they are past
    assignments.sort(key=lambda x: x.due_datetime, reverse=past)
    return assignments


def active_assignments(courses=None):
    """Gets the user's incomplete assignments that are not overdue. Can be constrained by course.

    Args:
        courses: A list of Course objects to constrain the search. Default None

    Returns:
        A list of Assignment objects
    """

    assignments = current_assignments(courses)
    ans = []
    now = util.utc_now()

    for assignment in assignments:
        # Select the incomplete assignments that have not passed their due date
        if util.utc_datetime_from_naive_utc_datetime(assignment.due_datetime) > now:
            ans.append(assignment)

    return ans


def overdue_assignments(courses=None):
    """Gets the user's incomplete assignments that are overdue. Can be constrained by course.

    Args:
        courses: A list of Course objects to constrain the search. Default None

    Returns:
        A list of Assignment objects
    """

    assignments = current_assignments(courses)
    ans = []
    now = util.utc_now()

    for assignment in assignments:
        # Select the incomplete assignments that have passed their due date
        if util.utc_datetime_from_naive_utc_datetime(assignment.due_datetime) <= now:
            ans.append(assignment)

    return ans


def get_assignment_colors(assignments):
    """Gets the course colors associated with a list of assignment objects. Useful for helpful swatches and such.

    Args:
        assignments: A list of Assignment objects whose colors must be looked up.

    Returns:
        A tuple of color strings corresponding to the courses of the assignments.
    """

    colors = []
    for assignment in assignments:
        course = Course.query.filter_by(user_id=current_user.id, id=assignment.course_id).first()
        colors.append(course.color)

    return tuple(colors)


def fix_assignment_study_sessions(assignment):
    """Adjusts the courses to which study sessions belong to align them with the assignments to which
    study sessions belong.

    This is weird but necessary, because study sessions don't all belong to assignments, but they do
    all have courses. When an assignment is moved to a different course, the course ids of that assignment's
    study sessions must be changed manually to match the new course.

    Args:
        assignment: An Assignment object that has moved to a new course
    """

    study_sessions = StudySession.query.filter_by(user_id=current_user.id, assignment_id=assignment.id).all()
    for study_session in study_sessions:
        study_session.course_id = assignment.course_id
    db.session.commit()


def fix_course_study_sessions(course):
    """Adjusts the semesters to which study sessions belong to align them with the courses to which
    study sessions belong.

    See the above note, but for moving courses instead of assignments.

    Args:
        course: A Course object that has moved to a new semester
    """

    study_sessions = StudySession.query.filter_by(user_id=current_user.id, course_id=course.id).all()
    for study_session in study_sessions:
        study_session.semester_id = course.semester_id
    db.session.commit()


def start_study_session(course, assignment=None):
    """Starts a new study session for the user.

    Args:
        course: A Course object representing the course being studied
        assignment: An Assignment object representing the assignment being studied. Default None
    """

    # There must be only one at a time.
    stop_study_session()

    # Handle the optional nature of an assignment
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
    """Closes all open study sessions."""

    # There should never be more than one open at once, but let's be sure:
    study_sessions = StudySession.query.filter_by(user_id=current_user.id, end_datetime=None).all()
    for study_session in study_sessions:
        study_session.end_datetime = util.utc_now()

    db.session.commit()
    invalidate_caches("current_study_session")


# @cache
def current_study_session():
    """Gets the user's current study session.

    Returns
        A StudySession object
    """

    # Get the first study session that has not ended. There should be only one, but I want this to be
    # robust in case there's a problem.
    study_session = StudySession.query.filter_by(user_id=current_user.id, end_datetime=None).first()
    return study_session


def study_time(start_datetime=None, end_datetime=None, semesters=None, courses=None, assignments=None):
    """Calculates the total time studied across the provided search parameters. If no parameters
    are provided, calculates all-time study time. Only accepts one of semesters, courses, or assignments.

    Args:
        start_datetime: A datetime object representing the UTC start of the search period. Default None
        end_datetime: A datetime object representing the UTC end of the search period. Default None
        semesters: A list of Semester objects to constrain the search. Default None
        courses: A list of Course objects to constrain the search. Default None
        assignments: A list of Assignment objects to constrain the search. Default None

    Returns:
        A datetime.timedelta object representing the total study time
    """

    # Ensure that there is at most one constraint.
    assert sum(bool(x) for x in [semesters, courses, assignments]) <= 1

    # If times are not provided, look from the time of account creation to now.
    if not start_datetime:
        start_datetime = current_user.created
        start_datetime = util.utc_datetime_from_naive_utc_datetime(start_datetime)
    if not end_datetime:
        end_datetime = util.utc_now()

    # In general, check if each study session is owned by the user, has ended, falls within the search
    # period, and belongs to the provided semesters, courses, or assignments.
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

    # Sum the time deltas of all the study sessions.
    total = datetime.timedelta(0)
    for study_session in study_sessions:
        total += study_session.end_datetime - study_session.start_datetime

    return total


# These deletion functions define recursive behavior that removes all sub-objects from the db when
# a container is deleted.

def deep_delete_current_user():
    # Users contain semesters and todos
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
    # Semesters contain courses
    courses = Course.query.filter_by(user_id=current_user.id, semester_id=semester.id).all()
    for course in courses:
        deep_delete_course(course)

    db.session.delete(semester)
    db.session.commit()
    invalidate_caches("current_semester")


def deep_delete_course(course):
    # Courses contain assignments and study sessions
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


def deep_delete_calendar_event(calendar_event):
    db.session.delete(calendar_event)
    db.session.commit()


def deep_delete_study_session(study_session):
    db.session.delete(study_session)
    db.session.commit()
    invalidate_caches("current_study_session")


def invalidate_caches(*args):
    # This is not used at all. I want a caching behavior, but this one is a security vulerability because
    # cached objects can persist across sessions. I need to find a better way to cache. All save to
    # cache tags are commented out currently.
    names = args if args else globals().keys()
    for func in names:
        try:
            globals()[func].cache_clear()
        except:
            pass