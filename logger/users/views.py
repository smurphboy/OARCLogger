from flask import Blueprint

users = Blueprint('users', __name__, template_folder='templates')

@users.route("/")
def user_index():
    '''Shows all known users and lists their callsigns. Allows admin
    to manage users.'''
    return "User Index"

@users.route('/<user>')
def user_homepage(user):
    '''This page shows all the users callsigns and let them manage them,
    add new calls, edit calls and add information about the callsign'''
    return ("User: " + user)

@users.route('/<user>/<call>')
def call_homepage(user, call):
    '''this show shows information about this callsign and allows the
    to edit the information. Also links to import / export for this callsign'''
    return ("User: " + user + " Working as: " + call)