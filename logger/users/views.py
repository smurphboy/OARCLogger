from flask import Blueprint, flash, render_template, redirect, request, url_for
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash
from logger.models import User, db

users = Blueprint('users', __name__, template_folder='templates')

@users.route("/")
def index():
    '''Shows all known users and lists their callsigns. Allows admin
    to manage users.'''
    return "User Index"

@users.route('/<user>')
def profile(user):
    '''This page shows all the users callsigns and let them manage them,
    add new calls, edit calls and add information about the callsign'''
    return ("User: " + user)

@users.route('/<user>/<call>')
def call_homepage(user, call):
    '''this show shows information about this callsign and allows the
    to edit the information. Also links to import / export for this callsign'''
    return ("User: " + user + " Working as: " + call)

@users.route('/login')
def login():
    return render_template('login.html')

@users.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('users.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('users.profile', user=user.name))

@users.route('/signup')
def signup():
    return render_template('signup.html')

@users.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already registered')
        return redirect(url_for('users.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('users.login'))

@users.route('/logout')
def logout():
    #return render_template('logout.html')   
    return 'Logout'