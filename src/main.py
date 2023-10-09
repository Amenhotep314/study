from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from datetime import date

from . import db
from .models import *
from .forms import *
from .util import current_semester, invalidate_caches


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
        invalidate_caches()
        return redirect(url_for('main.view_semesters'))

    return render_template("create_semester.html", form=form, methods=['GET', 'POST'])


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
        invalidate_caches()
        return redirect(url_for('main.view_semesters'))

    form.name.data = semester.name
    form.start_date.data = semester.start_date
    form.end_date.data = semester.end_date

    return render_template("edit_semester.html", form=form, semester=semester, methods=['GET', 'POST'])


@main.route("/semesters/delete/<semester_id>", methods=['GET', 'POST'])
@login_required
def delete_semester(semester_id):

    semester = db.first_or_404(Semester.query.filter_by(user_id=current_user.id, id=semester_id))
    db.session.delete(semester)
    db.session.commit()

    return redirect(url_for('main.view_semesters'))


@main.route("/courses/create", methods=['GET', 'POST'])
@login_required
def create_course():

    form = CourseForm()
    if not current_semester():
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
        return redirect(url_for('main.view_semester', semester_id=form.semester.data))

    for semester in Semester.query.filter_by(user_id=current_user.id).all():
        print([semester.id, semester.name])

    form.semester.choices = [(semester.id, semester.name) for semester in Semester.query.filter_by(user_id=current_user.id).all()]
    form.semester.data = current_semester().id

    return render_template("create_course.html", form=form, methods=['GET', 'POST'])