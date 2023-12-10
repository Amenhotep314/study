from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from . import db
from . import db_util
from . import util
from .models import *
from .forms import *


main = Blueprint("main", __name__)


@main.route("/")
@login_required
def index():

    return render_template("index.html")


@main.route("/semesters")
@login_required
def view_semesters():

    semesters = Semester.query.filter_by(user_id=current_user.id).all()
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
            user_id = current_user.id,
            name = form.name.data,
            start_datetime = start_datetime,
            end_datetime = end_datetime
        )
        db.session.add(new_semester)
        db.session.commit()
        db_util.invalidate_caches("current_semester", "current_courses")
        return redirect(url_for('main.view_semesters'))

    return render_template(
        "create.html",
        form=form,
        title="Semester",
        action=url_for('main.create_semester'),
        methods=['GET', 'POST']
    )


@main.route("/semesters/<semester_id>")
@login_required
def view_semester(semester_id):

    semester = db.first_or_404(Semester.query.filter_by(user_id=current_user.id, id=semester_id))
    semester_dict = util.local_dict_from_naive_utc_query(semester)

    return render_template("view_semester.html", semester=semester_dict)


@main.route("/semesters/edit/<semester_id>", methods=['GET', 'POST'])
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
        return redirect(url_for('main.view_semesters'))

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


@main.route("/semesters/delete/<semester_id>", methods=['GET', 'POST'])
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

    form = CourseForm()
    form.semester.choices = [(semester.id, semester.name) for semester in Semester.query.filter_by(user_id=current_user.id).all()]
    if not db_util.current_semester():
        return redirect(url_for('main.create_semester'))

    if form.validate_on_submit():
        new_course = Course(
            user_id = current_user.id,
            semester_id = form.semester.data,
            name = form.name.data,
            short_name = form.short_name.data,
            credits = form.credits.data
        )
        db.session.add(new_course)
        db.session.commit()
        db_util.invalidate_caches("current_courses")
        return redirect(url_for('main.view_courses'))

    form.semester.data = db_util.current_semester().id

    return render_template(
        "create.html",
        form=form,
        title="Course",
        action=url_for('main.create_course'),
        methods=['GET', 'POST']
    )


@main.route("/courses/<course_id>")
@login_required
def view_course(course_id):

    course = db.first_or_404(Course.query.filter_by(user_id=current_user.id, id=course_id))
    return render_template("view_course.html", course=course)


@main.route("/courses/edit/<course_id>", methods=['GET', 'POST'])
@login_required
def edit_course(course_id):

    course = db.first_or_404(Course.query.filter_by(user_id=current_user.id, id=course_id))
    form = CourseForm()
    form.semester.choices = [(semester.id, semester.name) for semester in Semester.query.filter_by(user_id=current_user.id).all()]

    if form.validate_on_submit():
        course.semester_id = form.semester.data
        course.name = form.name.data
        course.short_name = form.short_name.data
        course.credits = form.credits.data
        db.session.commit()
        db_util.invalidate_caches("current_courses")
        return redirect(url_for('main.view_courses'))

    form.semester.data = course.semester_id
    form.name.data = course.name
    form.short_name.data = course.short_name
    form.credits.data = course.credits

    return render_template(
        "edit.html",
        form=form,
        action=url_for('main.edit_course', course_id=course.id),
        delete_action=url_for('main.delete_course', course_id=course.id),
        methods=['GET', 'POST']
    )


@main.route("/courses/delete/<course_id>", methods=['GET', 'POST'])
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
        return redirect(url_for('main.index'))

    return render_template(
        "create.html",
        form=form,
        title="Assignment",
        action=url_for('main.create_assignment'),
        methods=['GET', 'POST']
    )


@main.route("/assignments/<assignment_id>")
@login_required
def view_assignment(assignment_id):

    assignment = db.first_or_404(Assignment.query.filter_by(user_id=current_user.id, id=assignment_id))
    assignment_dict = util.local_dict_from_naive_utc_query(assignment)

    return render_template("view_assignment.html", assignment=assignment_dict)


@main.route("/assignments/edit/<assignment_id>", methods=['GET', 'POST'])
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

        assignment.course_id = form.course.data
        assignment.name = form.name.data
        assignment.due_datetime = due_datetime
        # assignment.est_time = form.est_time.data
        # assignment.importance = form.importance.data
        assignment.completed = form.completed.data
        db.session.commit()
        db_util.invalidate_caches("current_assignments")
        return redirect(url_for('main.index'))

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


@main.route("/assignments/delete/<assignment_id>", methods=['GET', 'POST'])
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

    action_links = [("Stop Studying", url_for('main.stop_study')),]
    if study_session.assignment_id:
        target = db.first_or_404(Assignment.query.filter_by(user_id=current_user.id, id=study_session.assignment_id))
        action_links.append(("Assignment Completed", url_for('main.stop_study_complete_assignment')))
    else:
        target = db.first_or_404(Course.query.filter_by(user_id=current_user.id, id=study_session.course_id))

    return render_template("study.html", target=target, action_links=action_links)


@main.route("/stop_study")
@login_required
def stop_study():

    db_util.stop_study_session()
    return redirect(url_for('main.index'))


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
    return redirect(url_for('main.index'))