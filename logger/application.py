from flask import Flask, render_template
from flask_login import LoginManager
from logger.users.views import users
from logger.callsigns.views import callsigns
from logger.config import Config
from logger.models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'users.login'
    login_manager.init_app(app)

    from logger.models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    app.register_blueprint(users, url_prefix='/users')
    app.register_blueprint(callsigns, url_prefix='/callsigns')

    @app.route("/")
    def index():
        return render_template('index.html')

    return app