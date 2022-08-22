from flask import Flask, render_template
from users.blueprint import users

app = Flask(__name__)
app.config.from_object('config.Config')

app.register_blueprint(users, url_prefix='/users')

@app.route("/")
def index():
    return render_template('index.html')

