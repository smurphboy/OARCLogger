from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from .users.views import users
from .config import Config

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(users, url_prefix='/users')

    @app.route("/")
    def index():
        return render_template('index.html')

    return app

if __name__ == "__main__":
    create_app().run()