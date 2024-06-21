""""Constructs the Flask object for a session and configures the app."""

# Useful links
# Flask docs: https://flask.palletsprojects.com/en/2.3.x/
# SQLAlchemy docs: https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/
# Basic Flask tutorial: https://www.youtube.com/watch?v=Z1RJmh_OqeA and code: https://github.com/jakerieger/FlaskIntroduction
# User authentication guide: https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login


from flask import Flask, request, render_template, url_for
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel, _, lazy_gettext as _l
import json
from json import JSONEncoder
import os
from . import util


db = SQLAlchemy()
# Tuple of user ids with access to the admin page
ADMIN_USER_IDS = 1,


def page_not_found(e):
    error_description = _("The page you are looking for does not exist.")
    template = "error_main.html" if current_user.is_authenticated else "error_auth.html"
    return render_template(
        template,
        error_description=error_description,
        button_link=url_for('main.index')
    ), 404


def internal_server_error(e):
    error_description = _("An error occured in a Python script, so we weren't able to complete your request.")
    template = "error_main.html" if current_user.is_authenticated else "error_auth.html"
    return render_template(
        template,
        error_description=error_description,
        button_link=url_for('main.index')
    ), 500


def create_app():
    """Creates and configures a Flask object. Called at the start of any new session.

    Returns:
        A Flask object
    """

    app = Flask(__name__)

    # Configure the app. Look for environment variables first.
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://') or 'sqlite:///db.sqlite'

    # After that, look for a config file
    try:
        app.config.from_file("config.json", load=json.load)
    except:
        pass

    app.config['LANGUAGES'] = [item[0] for item in util.language_options()]
    db.init_app(app)

    # User authentication
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    # Try to get language from the database, otherwise ask the browser
    def get_locale():
        if current_user.is_authenticated:
            return current_user.language
        return request.accept_languages.best_match(app.config['LANGUAGES'])
    babel = Babel(app, locale_selector=get_locale)

    # Custom encoder necessary to deal with translatable strings in async JSON responses
    class CustomJSONEncoder(JSONEncoder):
        def default(self, obj):
            from speaklater import is_lazy_string
            if is_lazy_string(obj):
                return str(obj)
            return super(CustomJSONEncoder, self).default(obj)
    app.json_encoder = CustomJSONEncoder

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    from .ajax import ajax as ajax_blueprint
    app.register_blueprint(ajax_blueprint)

    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)

    return app
