from flask import Flask, render_template
from flask_login import LoginManager
from logger.users.views import users
from logger.callsigns.views import callsigns
from logger.qsos.views import qsos
from logger.events.views import events
from logger.configurations.views import configurations
from logger.config import Config
from logger.models import db
from flask_migrate import Migrate


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db, render_as_batch=True)

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
    app.register_blueprint(qsos, url_prefix='/qsos')
    app.register_blueprint(events, url_prefix='/events')
    app.register_blueprint(configurations, url_prefix='/configs')

    @app.route("/")
    def index():
        return render_template('index.html')

    @app.route("/about")
    def about():
        return render_template('about.html')

    @app.template_filter()
    def MhzFormat(value):
        value = float(value)
        return "{:,.6f} MHz".format(value)

    return app