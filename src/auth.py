from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash

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

    return render_template("login.html", form=form)


@auth.route('/signup', methods=['GET', 'POST'])
def signup():

    form = SignUp()

    if form.validate_on_submit():
        email = form.email.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        password = form.password.data

        hashed_password = generate_password_hash(password, method='scrypt')
        new_user = User(
            email=email,
            firstname=firstname,
            lastname=lastname,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))

    return render_template("signup.html", form=form)


@auth.route("/logout")
@login_required
def logout():

    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/about")
def front_page():

    return render_template("front_page.html")