from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from datetime import date

from . import db
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
        return redirect(url_for('main.view_semesters'))


    return render_template("create_semester.html", form=form, methods=['GET', 'POST'])