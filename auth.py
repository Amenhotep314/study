from flask import Blueprint
from . import db


auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():

    return "Log In"


@auth.route("/signup")
def signup():

    return "Sign Up"


@auth.route("/logout")
def logout():

    return "Log Out"