import datetime
import operator
import os

from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import desc, func, and_
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
    calls = QSO.query.with_entities(QSO.call).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).distinct()
    callsigns = Callsign.query.with_entities(Callsign.name).distinct()
    unclaimed = list(set(calls).difference(callsigns))
    facts['unclaimedcallsigns'] = len(unclaimed)
    facts['dxcctable'] = db.session.query(QSO.station_callsign, db.func.count(db.distinct(QSO.dxcc))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(QSO.station_callsign).order_by(db.func.count(db.distinct(QSO.dxcc)).desc()).limit(10).all()
    facts['totaldxcc'] = QSO.query.with_entities(QSO.dxcc).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).distinct().count()
    facts['cqztable'] = db.session.query(QSO.station_callsign, db.func.count(db.distinct(QSO.cqz))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(QSO.station_callsign).order_by(db.func.count(db.distinct(QSO.cqz)).desc()).limit(10).all()
    facts['totalcqz'] = QSO.query.with_entities(QSO.cqz).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).distinct().count()
    facts['ituztable'] = db.session.query(QSO.station_callsign, db.func.count(db.distinct(QSO.ituz))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(QSO.station_callsign).order_by(db.func.count(db.distinct(QSO.ituz)).desc()).limit(10).all()
    facts['totalituz'] = QSO.query.with_entities(QSO.ituz).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).distinct().count()
    facts['bandtable'] = db.session.query(QSO.station_callsign, db.func.count(db.distinct(QSO.band))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(QSO.station_callsign).order_by(db.func.count(db.distinct(QSO.band)).desc()).limit(10).all()
    facts['totalbands'] = QSO.query.with_entities(QSO.band).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).distinct().count()
    facts['qsostoday'] = db.session.query(QSO.id).filter(QSO.qso_date==datetime.date.today()).count()
    qsobyday = db.session.query(QSO.qso_date, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(QSO.qso_date).order_by(QSO.qso_date.desc()).all()
    return render_template('leaderboard.html', facts=facts, unclaimed=unclaimed, qsobyday=qsobyday)


@waoarc.route("/gettingstarted")
def gettingstarted():
    '''Worked All OARC Season 2 getting started page'''
    return render_template('gettingstarted.html')

@waoarc.route("/users")
def users():
    '''Detail of Users and Callsigns tile on Leaderboard'''
    calls = db.session.query(User.name, Callsign.name, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name, Callsign.name).order_by(func.count(QSO.id).desc()).all()
    unccalls = QSO.query.with_entities(QSO.call).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).distinct()
    callsigns = Callsign.query.with_entities(Callsign.name).distinct()
    unclaimedcalls = list(set(unccalls).difference(callsigns))
    unclaimedtable = []
    for call in unclaimedcalls:
        line = []
        line.append(call[0])
        line.append(QSO.query.filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.call == call[0]).count())
        unclaimedtable.append(line)
    return render_template('users.html', calls=calls, unclaimedcalls=unclaimedcalls, unclaimedtable=unclaimedtable)


@waoarc.route("/dates")
def dates():
    '''All the date and time related info for the Leaderboard Dates detail page'''
    qsobyday = db.session.query(QSO.qso_date, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(QSO.qso_date).order_by(QSO.qso_date.desc()).all()
    labels = list(map(list, zip(*qsobyday)))[0]
    dates = []
    for label in labels:
        dates.append(label.strftime('%Y-%m-%d'))
    values = list(map(list, zip(*qsobyday)))[1]
    usersbyday = db.session.query(QSO.qso_date, User.name, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(QSO.qso_date, User.name).order_by(QSO.qso_date.desc()).order_by(func.count(QSO.id).desc()).all()
    return render_template('dates.html', qsobyday=qsobyday, labels=dates, values=values, usersbyday=usersbyday)