import operator
from datetime import datetime

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import desc, func
from werkzeug.security import check_password_hash, generate_password_hash

from logger.forms import CallsignForm
from logger.models import QSO, Callsign, User, db

users = Blueprint('users', __name__, template_folder='templates')



@users.route("/")
def index():
    '''Our intro page'''
    return render_template('index.html')

@users.route('/<user>', methods=['GET','POST'])
@login_required
def profile(user):
    '''This page shows all the users callsigns and let them manage them,
    add new calls, edit calls and add information about the callsign'''
    form = CallsignForm()
    if request.method == 'POST':
        name = request.form.get('name','').upper() or None
        newcallsign = Callsign(name=name, user_id=current_user.get_id())
        db.session.add(newcallsign)
        db.session.commit()
        return redirect(url_for('users.profile', user=current_user.name))
    return render_template('profile.html', user=current_user.name, form=form)

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
    user.last_login = datetime.now()
    db.session.commit()
    return redirect(url_for('users.profile', user=current_user.name))

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
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), created_on=datetime.now())

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('users.login'))

@users.route('/logout')
@login_required
def logout():
    logout_user()
    #return render_template('logout.html')   
    return redirect(url_for('users.index'))

@users.route('/home')
@login_required
def home():
    callsigns = Callsign.query.filter_by(user_id=current_user.get_id()).all()
    calls = []
    countries = {}
    for callname in callsigns:
        calls.append(callname.name)
    for qso in QSO.query.filter(QSO.station_callsign.in_(calls)).all():
        dxcc = current_app.cic.get_all(qso.call)['country'] + " (" + str(current_app.cic.get_all(qso.call)['adif']) + "):"
        if dxcc in countries.keys():
            countries[dxcc] = countries[dxcc] + 1
        else:
            countries[dxcc] = 1
    sortedcountries = dict(sorted(countries.items(), key=operator.itemgetter(1), reverse=True))
    print(len(countries))
    #dxcccounts = QSO.query.filter(QSO.station_callsign.in_(calls)).with_entities(QSO.dxcc, func.count(QSO.dxcc)).group_by(QSO.dxcc).order_by(desc(func.count(QSO.dxcc))).limit(10).all()
    totalqsos = QSO.query.filter(QSO.station_callsign.in_(calls)).count()
    #totaldxcc = QSO.query.filter(QSO.station_callsign.in_(calls)).with_entities(QSO.dxcc).distinct().count()
    return render_template('home.html', totalqsos=totalqsos, dxcccounts=sortedcountries)