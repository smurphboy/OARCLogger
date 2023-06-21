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
    calls = QSO.query.with_entities(QSO.call).distinct()
    callsigns = Callsign.query.with_entities(Callsign.name).distinct()
    unclaimed = list(set(calls).difference(callsigns))
    facts['unclaimedcallsigns'] = len(unclaimed)
    facts['dxcctable'] = db.session.query(QSO.station_callsign, db.func.count(db.distinct(QSO.dxcc))).group_by(QSO.station_callsign).order_by(db.func.count(db.distinct(QSO.dxcc)).desc()).limit(10).all()
    facts['totaldxcc'] = QSO.query.with_entities(QSO.dxcc).distinct().count()
    facts['cqztable'] = db.session.query(QSO.station_callsign, db.func.count(db.distinct(QSO.cqz))).group_by(QSO.station_callsign).order_by(db.func.count(db.distinct(QSO.cqz)).desc()).limit(10).all()
    facts['totalcqz'] = QSO.query.with_entities(QSO.cqz).distinct().count()
    facts['ituztable'] = db.session.query(QSO.station_callsign, db.func.count(db.distinct(QSO.ituz))).group_by(QSO.station_callsign).order_by(db.func.count(db.distinct(QSO.ituz)).desc()).limit(10).all()
    facts['totalituz'] = QSO.query.with_entities(QSO.ituz).distinct().count()
    facts['bandtable'] = db.session.query(QSO.station_callsign, db.func.count(db.distinct(QSO.band))).group_by(QSO.station_callsign).order_by(db.func.count(db.distinct(QSO.band)).desc()).limit(10).all()
    facts['totalbands'] = QSO.query.with_entities(QSO.band).distinct().count()
    return render_template('leaderboard.html', facts=facts)


@waoarc.route("/gettingstarted")
def gettingstarted():
    '''Worked All OARC Season 2 getting started page'''
    return render_template('gettingstarted.html')

@waoarc.route("/users")
def users():
    '''Detail of Users and Callsigns tile on Leaderboard'''
    return render_template('users.html')