from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from . import db
from .models import *


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


@main.route("/semesters/new_semester", methods=['GET', 'POST'])
@login_required
def create_semester():

    if request.method == 'GET':
        return render_template("new_semester.html")

    name = request.form.get('name')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    new_semester = Semester(name=name, start_date=start_date, end_date=end_date)
    db.session.add(new_semester)
    db.session.commit()

    return redirect(url_for('main.index'))

