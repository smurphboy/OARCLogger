import operator
import os
from datetime import datetime

from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import desc, func
from werkzeug.security import check_password_hash, generate_password_hash

from logger.forms import CallsignForm
from logger.models import QSO, Callsign, User, db

waoarc = Blueprint('waoarc', __name__, template_folder='../templates/waoarc')

@waoarc.route("/")
def about():
    '''Worked All OARC Season 2 intro page'''
    return render_template('aboutwaoarc.html')


@waoarc.route("/leaderboards")
def leaderboards():
    '''Worked All OARC Season 2 leaderboards'''
    facts = {}
    facts['totalusers'] = User.query.count()
    facts['totalcallsigns'] = Callsign.query.count()
    #calls = QSO.query.filter(QSO.call.in_(Callsign.name)).all()
    #facts['unclaimedcallsigns'] = 
    #print ("Calls: ", calls)
    return render_template('leaderboard.html', facts=facts)


@waoarc.route("/gettingstarted")
def gettingstarted():
    '''Worked All OARC Season 2 getting started page'''
    return render_template('gettingstarted.html')

@waoarc.route("/users")
def users():
    '''Detail of Users and Callsigns tile on Leaderboard'''
    return render_template('users.html')