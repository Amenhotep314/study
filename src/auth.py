from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
import pytz

from . import db
from .models import *
from .forms import *


auth = Blueprint("auth", __name__)


@auth.route("/login", methods=['GET', 'POST'])
def login():

    form = LogIn()

    if form.validate_on_submit():
        email = form.email.data
        remember = form.remember.data

        user = User.query.filter_by(email=email).first()
        login_user(user, remember=remember)
        return redirect(url_for('main.index'))

    return render_template(
        "auth.html",
        form=form,
        title="Log In",
        action=url_for('auth.login'),
        methods=['GET', 'POST']
    )


@auth.route('/signup', methods=['GET', 'POST'])
def signup():

    form = SignUp()

    if form.validate_on_submit():
        email = form.email.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        password = form.password.data
        timezone = form.timezone.data

        hashed_password = generate_password_hash(password, method='scrypt')
        new_user = User(
            email=email,
            firstname=firstname,
            lastname=lastname,
            password=hashed_password,
            timezone=timezone
        )

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))

    form.timezone.choices = [(timezone, timezone) for timezone in pytz.common_timezones]
    form.timezone.data = "Canada/Eastern"

    return render_template(
        "auth.html",
        form=form,
        title="Sign Up",
        action=url_for('auth.signup'),
        methods=['GET', 'POST']
    )


@auth.route("/logout")
@login_required
def logout():

    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/about")
def front_page():

    return render_template("front_page.html")