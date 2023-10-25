# Useful links
# Flask docs: https://flask.palletsprojects.com/en/2.3.x/
# SQLAlchemy docs: https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/
# Basic Flask tutorial: https://www.youtube.com/watch?v=Z1RJmh_OqeA and code: https://github.com/jakerieger/FlaskIntroduction
# User authentication guide: https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login


from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import json


db = SQLAlchemy()


def create_app():

    app = Flask(__name__)
    app.config.from_file("config.json", load=json.load)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
