from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from flask_babel import _, lazy_gettext as _l
import pytz

from . import db
from .models import *
from .forms import *
from . import db_util


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
        title=_("Log In"),
        action=url_for('auth.login'),
        methods=['GET', 'POST']
    )


@auth.route('/signup', methods=['GET', 'POST'])
def signup():

    form = SignUp()
    form.timezone.choices = [(timezone, timezone) for timezone in pytz.common_timezones]
    languages = util.language_options()
    form.language.choices = languages

    if form.validate_on_submit():
        email = form.email.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        password = form.password.data
        timezone = form.timezone.data
        language = form.language.data

        hashed_password = generate_password_hash(password, method='scrypt')
        new_user = User(
            created=util.utc_now(),
            email=email,
            firstname=firstname,
            lastname=lastname,
            password=hashed_password,
            timezone=timezone,
            language=language,
            theme = "greensboro_winter"
        )

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))

    form.timezone.data = "Canada/Eastern"
    form.language.data = request.accept_languages.best_match([item[0] for item in languages])

    return render_template(
        "auth.html",
        form=form,
        title=_("Sign Up"),
        action=url_for('auth.signup'),
        methods=['GET', 'POST']
    )


@auth.route("/logout")
@login_required
def logout():

    db_util.invalidate_caches()
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/")
def front_page():

    return render_template("front_page.html")