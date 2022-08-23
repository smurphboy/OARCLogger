from flask import Flask, render_template
from blueprints.users.views import users

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    app.register_blueprint(users, url_prefix='/users')

    @app.route("/")
    def index():
        return render_template('index.html')

    return app

if __name__ == "__main__":
    create_app().run()
