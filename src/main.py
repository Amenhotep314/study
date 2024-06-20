from flask import Blueprint, render_template, redirect, url_for, current_app, abort
from flask_login import login_required, current_user
from flask_babel import _, lazy_gettext as _l
from werkzeug.security import generate_password_hash
import pytz

from . import db
from . import db_util
from . import util
from .models import *
from .forms import *


main = Blueprint("main", __name__)
data = {"url": '/'}


@main.route("/serviceworker.js")
@login_required
def service_worker_load():

    return current_app.send_static_file('serviceworker.js')


@main.route("/home")
@login_required
def index():

    data['url'] =  url_for('main.index')

    overdue_assignments = db_util.overdue_assignments()
    active_assignments = db_util.active_assignments()
    overdue_assignment_dicts = util.local_dicts_from_naive_utc_queries(overdue_assignments)
    active_assignment_dicts = util.local_dicts_from_naive_utc_queries(active_assignments)
    overdue_todos = db_util.overdue_todos()
    active_todos = db_util.active_todos()
    overdue_todo_dicts = util.local_dicts_from_naive_utc_queries(overdue_todos)
    active_todo_dicts = util.local_dicts_from_naive_utc_queries(active_todos)

    if db_util.current_semester() and db_util.current_courses():
        main_message = _("Study Now")
    elif db_util.current_semester():
        main_message = _("Create Your First Course")
    else:
        main_message = _("Get Started Here")

    return render_template(
        "index.html",
        greeting=util.social_greeting(),
        main_message=main_message,
        overdue_assignments=overdue_assignment_dicts,
        active_assignments=active_assignment_dicts,
        overdue_todos=overdue_todo_dicts,
        active_todos=active_todo_dicts
    )


@main.route("/my_account")
@login_required
def view_self():

    data['url'] =  url_for('main.view_self')

    duration = util.utc_now() - pytz.utc.localize(current_user.created)
    hours = db_util.study_time()

    return render_template(
        "view_self.html",
        user=current_user,
        duration=duration.days,
        hours=hours
    )


@main.route("/settings", methods=['GET', 'POST'])
@login_required
def edit_self():

    form = SettingsForm()
    form.timezone.choices = [(timezone, timezone) for timezone in pytz.common_timezones]
    languages = util.language_options()
    form.language.choices = languages
    themes = util.theme_options()
    form.theme.choices = themes

    if form.validate_on_submit():

        current_user.email = form.email.data
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.timezone = form.timezone.data
        current_user.language = form.language.data
        current_user.theme = form.theme.data

        db.session.commit()
        return redirect(data['url'])

    form.email.data = current_user.email
    form.firstname.data = current_user.firstname
    form.lastname.data = current_user.lastname
    form.timezone.data = current_user.timezone
    form.language.data = current_user.language
    form.theme.data = current_user.theme

    return render_template(
        "edit_self.html",
        form=form,
    )


@main.route("/edit_password", methods=['GET', 'POST'])
@login_required
def edit_self_password():

    form = ChangePasswordForm()

    if form.validate_on_submit():
        password = form.password.data
        hashed_password = generate_password_hash(password, method='scrypt')
        current_user.password = hashed_password

        db.session.commit()
        return redirect(data['url'])

    return render_template(
        "edit_self.html",
        form=form
    )


@main.route("/todos")
@login_required
def view_todos():

    data['url'] =  url_for('main.view_todos')

    overdue_todos = db_util.overdue_todos()
    active_todos = db_util.active_todos()
    past_todos = db_util.current_todos(past=True)
    overdue_todo_dicts = util.local_dicts_from_naive_utc_queries(overdue_todos)
    active_todo_dicts = util.local_dicts_from_naive_utc_queries(active_todos)
    past_todo_dicts = util.local_dicts_from_naive_utc_queries(past_todos)

    return render_template(
        "view_todos.html",
        overdue_todos=overdue_todo_dicts,
        active_todos=active_todo_dicts,
        past_todos=past_todo_dicts
    )


@main.route("/create_todo", methods=['GET', 'POST'])
@login_required
def create_todo():

    form = ToDoForm()

    if form.validate_on_submit():

        if form.finish_datetime.data:
            finish_datetime = util.utc_datetime_from_naive_local_date(form.finish_datetime.data)
        else:
            finish_datetime = None

        new_todo = ToDo(
            created = util.utc_now(),
            user_id = current_user.id,
            name = form.name.data,
            description = form.description.data,
            finish_datetime = finish_datetime,
            completed = form.completed.data
        )
        db.session.add(new_todo)
        db.session.commit()
        return redirect(data['url'])

    return render_template(
        "create.html",
        form=form,
        title=_("To-Do"),
        action=url_for('main.create_todo'),
        methods=['GET', 'POST']
    )


@main.route("/todos/<int:todo_id>")
@login_required
def view_todo(todo_id):

    data['url'] =  url_for('main.view_todo', todo_id=todo_id)

    todo = db.first_or_404(ToDo.query.filter_by(user_id=current_user.id, id=todo_id))
    todo_dict = util.local_dict_from_naive_utc_query(todo)

    return render_template(
        "view_todo.html",
        todo=todo_dict
    )


@main.route("/todos/edit/<int:todo_id>", methods=['GET', 'POST'])
@login_required
def edit_todo(todo_id):

    todo = db.first_or_404(ToDo.query.filter_by(user_id=current_user.id, id=todo_id))
    form = ToDoForm()

    if form.validate_on_submit():

        if form.finish_datetime.data:
            finish_datetime = util.utc_datetime_from_naive_local_date(form.finish_datetime.data)
        else:
            finish_datetime = None

        todo.name = form.name.data
        todo.description = form.description.data
        todo.finish_datetime = finish_datetime
        todo.completed = form.completed.data
        db.session.commit()
        return redirect(data['url'])

    form.name.data = todo.name
    form.description.data = todo.description
    if todo.finish_datetime:
        form.finish_datetime.data = util.local_datetime_from_naive_utc_datetime(todo.finish_datetime).date()
    form.completed.data = todo.completed

    return render_template(
        "edit.html",
        form=form,
        action=url_for('main.edit_todo', todo_id=todo.id),
        delete_action=url_for('main.delete_todo', todo_id=todo.id),
        methods=['GET', 'POST']
    )


@main.route("/todos/delete/<int:todo_id>", methods=['GET', 'POST'])
@login_required
def delete_todo(todo_id):

    todo = db.first_or_404(ToDo.query.filter_by(user_id=current_user.id, id=todo_id))
    form = ConfirmDelete()

    if form.validate_on_submit():
        db_util.deep_delete_todo(todo)
        return redirect(url_for('main.index'))

    return render_template(
        "delete.html",
        form=form,
        target=todo,
        action=url_for('main.delete_todo', todo_id=todo.id),
        methods=['GET', 'POST']
    )


@main.route("/todos/complete/<int:todo_id>")
@login_required
def complete_todo(todo_id):

    todo = db.first_or_404(ToDo.query.filter_by(user_id=current_user.id, id=todo_id))
    todo.completed = True
    db.session.commit()
    return redirect(data['url'])


@main.route("/semesters")
@login_required
def view_semesters():

    data['url'] =  url_for('main.view_semesters')

    semesters = Semester.query.filter_by(user_id=current_user.id).all()
    semesters.sort(key=lambda x: x.start_datetime, reverse=True)
    semester_dicts = util.local_dicts_from_naive_utc_queries(semesters)

    return render_template("view_semesters.html", semesters=semester_dicts)


@main.route("/semesters/create", methods=['GET', 'POST'])
@login_required
def create_semester():

    form = SemesterForm()

    if form.validate_on_submit():

        start_datetime = util.utc_datetime_from_naive_local_date(form.start_datetime.data, eod=False)
        end_datetime = util.utc_datetime_from_naive_local_date(form.end_datetime.data)

        new_semester = Semester(
            created = util.utc_now(),
            user_id = current_user.id,
            name = form.name.data,
            start_datetime = start_datetime,
            end_datetime = end_datetime
        )
        db.session.add(new_semester)
        db.session.commit()
        db_util.invalidate_caches("current_semester", "current_courses")
        return redirect(data['url'])

    return render_template(
        "create.html",
        form=form,
        title=_("Semester"),
        action=url_for('main.create_semester'),
        methods=['GET', 'POST']
    )


@main.route("/semesters/<int:semester_id>")
@login_required
def view_semester(semester_id):

    data['url'] =  url_for('main.view_semester', semester_id=semester_id)

    semester = db.first_or_404(Semester.query.filter_by(user_id=current_user.id, id=semester_id))
    semester_dict = util.local_dict_from_naive_utc_query(semester)
    hours = db_util.study_time(semesters=[semester])
    courses = Course.query.filter_by(user_id=current_user.id, semester_id=semester.id).all()
    courses.sort(key=lambda x: x.name)

    return render_template(
        "view_semester.html",
        semester=semester_dict,
        hours=hours,
        courses=courses
    )


@main.route("/semesters/edit/<int:semester_id>", methods=['GET', 'POST'])
@login_required
def edit_semester(semester_id):

    semester = db.first_or_404(Semester.query.filter_by(user_id=current_user.id, id=semester_id))
    form = SemesterForm()

    if form.validate_on_submit():

        start_datetime = util.utc_datetime_from_naive_local_date(form.start_datetime.data, eod=False)
        end_datetime = util.utc_datetime_from_naive_local_date(form.end_datetime.data)

        semester.name = form.name.data
        semester.start_datetime = start_datetime
        semester.end_datetime = end_datetime

        db.session.commit()
        db_util.invalidate_caches("current_semester", "current_courses")

        return redirect(data['url'])

    form.name.data = semester.name
    form.start_datetime.data = util.local_datetime_from_naive_utc_datetime(semester.start_datetime).date()
    form.end_datetime.data = util.local_datetime_from_naive_utc_datetime(semester.end_datetime).date()

    return render_template(
        "edit.html",
        form=form,
        action=url_for('main.edit_semester', semester_id=semester.id),
        delete_action=url_for('main.delete_semester', semester_id=semester.id),
        methods=['GET', 'POST']
    )


@main.route("/semesters/delete/<int:semester_id>", methods=['GET', 'POST'])
@login_required
def delete_semester(semester_id):

    semester = db.first_or_404(Semester.query.filter_by(user_id=current_user.id, id=semester_id))
    form = ConfirmDelete()

    if form.validate_on_submit():
        db_util.deep_delete_semester(semester)
        return redirect(url_for('main.view_semesters'))

    return render_template(
        "delete.html",
        form=form,
        target=semester,
        action=url_for('main.delete_semester', semester_id=semester.id),
        methods=['GET', 'POST']
    )


@main.route("/courses")
@login_required
def view_courses():

    data['url'] =  url_for('main.view_courses')

    current_semester = db_util.current_semester()
    if current_semester:
        courses = db_util.current_courses()
        title = current_semester.name
    else:
        courses = []
        title = ""

    return render_template(
        "view_courses.html",
        courses=courses
    )


@main.route("/courses/create", methods=['GET', 'POST'])
@login_required
def create_course():

    if not db_util.current_semester():
        return redirect(url_for('main.create_semester'))

    form = CourseForm()
    form.semester.choices = [(semester.id, semester.name) for semester in Semester.query.filter_by(user_id=current_user.id).all()]
    form.color.choices = util.color_options()

    if form.validate_on_submit():
        new_course = Course(
            created = util.utc_now(),
            user_id = current_user.id,
            semester_id = form.semester.data,
            name = form.name.data,
            short_name = form.short_name.data,
            credits = form.credits.data,
            color = form.color.data
        )
        db.session.add(new_course)
        db.session.commit()
        db_util.invalidate_caches("current_courses")
        return redirect(data['url'])

    form.semester.data = db_util.current_semester().id

    return render_template(
        "create.html",
        form=form,
        title=_("Course"),
        action=url_for('main.create_course'),
        methods=['GET', 'POST']
    )


@main.route("/courses/<int:course_id>")
@login_required
def view_course(course_id):

    data['url'] =  url_for('main.view_course', course_id=course_id)

    course = db.first_or_404(Course.query.filter_by(user_id=current_user.id, id=course_id))
    hours = db_util.study_time(courses=[course])
    overdue_assignments = db_util.overdue_assignments(courses=[course])
    active_assignments = db_util.active_assignments(courses=[course])
    past_assignments = db_util.current_assignments(courses=[course], past=True)
    overdue_assignment_dicts = util.local_dicts_from_naive_utc_queries(overdue_assignments)
    active_assignment_dicts = util.local_dicts_from_naive_utc_queries(active_assignments)
    past_assignment_dicts = util.local_dicts_from_naive_utc_queries(past_assignments)

    return render_template(
        "view_course.html",
        course=course,
        hours=hours,
        overdue_assignments=overdue_assignment_dicts,
        active_assignments=active_assignment_dicts,
        past_assignments=past_assignment_dicts
    )


@main.route("/courses/edit/<int:course_id>", methods=['GET', 'POST'])
@login_required
def edit_course(course_id):

    course = db.first_or_404(Course.query.filter_by(user_id=current_user.id, id=course_id))
    form = CourseForm()
    form.semester.choices = [(semester.id, semester.name) for semester in Semester.query.filter_by(user_id=current_user.id).all()]
    form.color.choices = util.color_options()

    if form.validate_on_submit():
        if course.semester_id != form.semester.data:
            db_util.fix_course_study_sessions(course)

        course.semester_id = form.semester.data
        course.name = form.name.data
        course.short_name = form.short_name.data
        course.credits = form.credits.data
        course.color = form.color.data
        db.session.commit()
        db_util.invalidate_caches("current_courses")
        return redirect(data['url'])

    form.semester.data = course.semester_id
    form.name.data = course.name
    form.short_name.data = course.short_name
    form.credits.data = course.credits
    if course.color in [item[0] for item in util.color_options()]:
        form.color.data = course.color

    return render_template(
        "edit.html",
        form=form,
        action=url_for('main.edit_course', course_id=course.id),
        delete_action=url_for('main.delete_course', course_id=course.id),
        methods=['GET', 'POST']
    )


@main.route("/courses/delete/<int:course_id>", methods=['GET', 'POST'])
@login_required
def delete_course(course_id):

    course = db.first_or_404(Course.query.filter_by(user_id=current_user.id, id=course_id))
    form = ConfirmDelete()

    if form.validate_on_submit():
        db_util.deep_delete_course(course)
        return redirect(url_for('main.view_courses'))

    return render_template(
        "delete.html",
        form=form,
        target=course,
        action=url_for('main.delete_course', course_id=course.id),
        methods=['GET', 'POST']
    )


@main.route("/assignments/create", methods=['GET', 'POST'])
@login_required
def create_assignment():

    if not db_util.current_semester():
        return redirect(url_for('main.create_semester'))
    courses = db_util.current_courses()
    if not courses:
        return redirect(url_for('main.create_course'))

    form = AssignmentForm()
    form.course.choices = [(course.id, course.name) for course in courses]

    if form.validate_on_submit():

        if form.due_time.data:
            due_datetime = util.utc_datetime_from_naive_local_date_time(form.due_date.data, form.due_time.data)
        else:
            due_datetime = util.utc_datetime_from_naive_local_date(form.due_date.data)

        new_assignment = Assignment(
            created = util.utc_now(),
            user_id = current_user.id,
            course_id = form.course.data,
            name = form.name.data,
            due_datetime = due_datetime,
            # est_time = form.est_time.data,
            # importance = form.importance.data,
            completed = form.completed.data
        )
        db.session.add(new_assignment)
        db.session.commit()
        db_util.invalidate_caches("current_assignments")
        return redirect(data['url'])

    return render_template(
        "create.html",
        form=form,
        title=_("Assignment"),
        action=url_for('main.create_assignment'),
        methods=['GET', 'POST']
    )


@main.route("/assignments/<int:assignment_id>")
@login_required
def view_assignment(assignment_id):

    data['url'] =  url_for('main.view_assignment', assignment_id=assignment_id)

    assignment = db.first_or_404(Assignment.query.filter_by(user_id=current_user.id, id=assignment_id))
    assignment_dict = util.local_dict_from_naive_utc_query(assignment)
    hours = db_util.study_time(assignments=[assignment])

    return render_template("view_assignment.html", assignment=assignment_dict, hours=hours)


@main.route("/assignments/edit/<int:assignment_id>", methods=['GET', 'POST'])
@login_required
def edit_assignment(assignment_id):

    assignment = db.first_or_404(Assignment.query.filter_by(user_id=current_user.id, id=assignment_id))
    form = AssignmentForm()
    courses = db_util.current_courses()
    form.course.choices = [(course.id, course.name) for course in courses]

    if form.validate_on_submit():

        if form.due_time.data:
            due_datetime = util.utc_datetime_from_naive_local_date_time(form.due_date.data, form.due_time.data)
        else:
            due_datetime = util.utc_datetime_from_naive_local_date(form.due_date.data)

        if assignment.course_id != form.course.data:
            db_util.fix_assignment_study_sessions(assignment)

        assignment.course_id = form.course.data
        assignment.name = form.name.data
        assignment.due_datetime = due_datetime
        # assignment.est_time = form.est_time.data
        # assignment.importance = form.importance.data
        assignment.completed = form.completed.data
        db.session.commit()
        db_util.invalidate_caches("current_assignments")
        return redirect(data['url'])

    form.course.data = assignment.course_id
    form.name.data = assignment.name
    form.due_date.data = util.local_datetime_from_naive_utc_datetime(assignment.due_datetime).date()
    form.due_time.data = util.local_datetime_from_naive_utc_datetime(assignment.due_datetime).time()
    # form.est_time.data = assignment.est_time
    # form.importance.data = assignment.importance
    form.completed.data = assignment.completed

    return render_template(
        "edit.html",
        form=form,
        action=url_for('main.edit_assignment', assignment_id=assignment.id),
        delete_action=url_for('main.delete_assignment', assignment_id=assignment.id),
        methods=['GET', 'POST']
    )


@main.route("/assignments/delete/<int:assignment_id>", methods=['GET', 'POST'])
@login_required
def delete_assignment(assignment_id):

    assignment = db.first_or_404(Assignment.query.filter_by(user_id=current_user.id, id=assignment_id))
    form = ConfirmDelete()

    if form.validate_on_submit():
        db_util.deep_delete_assignment(assignment)
        return redirect(url_for('main.index'))

    return render_template(
        "delete.html",
        form=form,
        target=assignment,
        action=url_for('main.delete_assignment', assignment_id=assignment.id),
        methods=['GET', 'POST']
    )


@main.route("/assignments/complete/<int:assignment_id>")
@login_required
def complete_assignment(assignment_id):

    assignment = db.first_or_404(Assignment.query.filter_by(user_id=current_user.id, id=assignment_id))
    assignment.completed = True
    db.session.commit()
    db_util.invalidate_caches("current_assignments")
    return redirect(data['url'])


@main.route("/select_study", methods=['GET', 'POST'])
@login_required
def select_study():

    if not db_util.current_semester():
        return redirect(url_for('main.create_semester'))
    courses = db_util.current_courses()
    if not courses:
        return redirect(url_for("main.create_course"))

    assignments = db_util.current_assignments()
    if assignments:
        max_id = 1 + max([assignment.id for assignment in assignments])
    else:
        max_id = 0
    assignment_options = [(assignment.id, assignment.name) for assignment in assignments]
    course_options = [(course.id+max_id, course.name) for course in courses]

    form = SelectStudyForm()
    form.choice.choices = assignment_options + course_options

    if form.validate_on_submit():
        choice = form.choice.data

        if choice in [assignment.id for assignment in assignments]:
            assignment = db.first_or_404(Assignment.query.filter_by(user_id=current_user.id, id=choice))
            course = db.first_or_404(Course.query.filter_by(user_id=current_user.id, id=assignment.course_id))

        else:
            choice -= max_id
            assignment = None
            course = db.first_or_404(Course.query.filter_by(user_id=current_user.id, id=choice))

        db_util.start_study_session(course, assignment)
        return redirect(url_for('main.study'))

    return render_template("select_study.html", form=form)


@main.route("/study")
@login_required
def study():

    study_session = db_util.current_study_session()
    if not study_session:
        return redirect(url_for('main.select_study'))

    action_links = [(_("Stop Studying"), url_for('main.stop_study')),]
    if study_session.assignment_id:
        target = db.first_or_404(Assignment.query.filter_by(user_id=current_user.id, id=study_session.assignment_id))
        action_links.append((_("Assignment Completed"), url_for('main.stop_study_complete_assignment')))
    else:
        target = db.first_or_404(Course.query.filter_by(user_id=current_user.id, id=study_session.course_id))

    return render_template("study.html", target=target, action_links=action_links)


@main.route("/stop_study")
@login_required
def stop_study():

    db_util.stop_study_session()
    return redirect(data['url'])


@main.route("/stop_study_complete_assignment")
@login_required
def stop_study_complete_assignment():

    study_session = db_util.current_study_session()
    if study_session and study_session.assignment_id:
        assignment = db.first_or_404(Assignment.query.filter_by(user_id=current_user.id, id=study_session.assignment_id))
        assignment.completed = True
        db.session.commit()
        db_util.invalidate_caches("current_assignments")

    db_util.stop_study_session()
    return redirect(data['url'])


@main.route("/stats")
@login_required
def stats():

    return render_template("stats.html")


@main.route("/admin")
@login_required
def admin():

    from . import ADMIN_USER_IDS
    if current_user.id not in ADMIN_USER_IDS:
        abort(403)

    import os
    import sys

    with open(os.path.join('requirements.txt')) as requirements_file:
        requirements = [line.strip() for line in requirements_file.readlines()]
    python_version = sys.version

    users = User.query.all()
    semesters = Semester.query.all()
    courses = Course.query.all()
    assignments = Assignment.query.all()
    study_sessions = StudySession.query.all()
    todos = ToDo.query.all()

    return render_template(
        "admin.html",
        python_version=python_version,
        requirements=requirements,
        users=users,
        semesters=semesters,
        courses=courses,
        assignments=assignments,
        study_sessions=study_sessions,
        todos=todos
    )


