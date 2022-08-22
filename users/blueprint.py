from flask import Blueprint

users = Blueprint('users', __name__, template_folder='templates')

@users.route("/")
def user_index():
    return "User Index"

@users.route('/<user>')
def user_homepage(user):
    return ("User: " + user)

@users.route('/<user>/<call>')
def call_homepage(user, call):
    return ("User: " + user + " Working as: " + call)