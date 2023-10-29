from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from datetime import date

from . import db
from . import db_util
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
    return render_template("view_semesters.html", semesters=semesters)


@main.route("/semesters/create", methods=['GET', 'POST'])
@login_required
def create_semester():

    form = SemesterForm()

    if form.validate_on_submit():
        new_semester = Semester(
            user_id = current_user.id,
            name = form.name.data,
            start_date = form.start_date.data,
            end_date = form.end_date.data
        )
        db.session.add(new_semester)
        db.session.commit()
        db_util.invalidate_caches("current_semester")
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
    return render_template("view_semester.html", semester=semester)


@main.route("/semesters/edit/<semester_id>", methods=['GET', 'POST'])
@login_required
def edit_semester(semester_id):

    semester = db.first_or_404(Semester.query.filter_by(user_id=current_user.id, id=semester_id))
    form = SemesterForm()

    if form.validate_on_submit():
        semester.name = form.name.data
        semester.start_date = form.start_date.data
        semester.end_date = form.end_date.data

        db.session.commit()
        db_util.invalidate_caches("current_semester")
        return redirect(url_for('main.view_semesters'))

    form.name.data = semester.name
    form.start_date.data = semester.start_date
    form.end_date.data = semester.end_date

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
        courses = Course.query.filter_by(user_id=current_user.id, semester_id=current_semester.id).all()
        title = current_semester.name
    else:
        courses = []
        title = ""

    return render_template(
        "view_courses.html",
        courses=courses,
        title=title
    )


@main.route("/courses/create", methods=['GET', 'POST'])
@login_required
def create_course():

    form = CourseForm()
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
        return redirect(url_for('main.view_courses'))

    form.semester.choices = [(semester.id, semester.name) for semester in Semester.query.filter_by(user_id=current_user.id).all()]
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

    if form.validate_on_submit():
        course.semester_id = form.semester.data
        course.name = form.name.data
        course.short_name = form.short_name.data
        course.credits = form.credits.data
        db.session.commit()
        return redirect(url_for('main.view_courses'))

    form.semester.choices = [(semester.id, semester.name) for semester in Semester.query.filter_by(user_id=current_user.id).all()]
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