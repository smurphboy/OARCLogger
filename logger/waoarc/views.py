import datetime
import json
import operator
import os

import maidenhead as mh
import requests

from flask import (Blueprint, abort, current_app, flash, jsonify, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from geojson import Feature, Polygon, FeatureCollection, load as gjload
from pprint import pprint
from requests_cache import CachedSession
from sqlalchemy import desc, func, and_, or_, text
from werkzeug.security import check_password_hash, generate_password_hash

from logger.forms import CallsignForm
from logger.helpers import countrylookup
from logger.models import QSO, Callsign, User, db

waoarc = Blueprint('waoarc', __name__, template_folder='../templates/waoarc')

rarity = {
    1 : 24,
    2 : 12,
    3 : 8,
    4 : 6,
    5 : 5,
    6 : 4,
    7 : 3,
    8 : 3,
    9 : 2,
    10 : 2,
    11 : 2,
    12 : 2,
    13 : 1,
    14 : 1,
    15 : 1,
    16 : 1,
    17 : 1,
    18 : 1,
    19 : 1,
    20 : 1,
    21 : 1,
    22 : 1,
    23 : 1,
    24 : 1,
}

DOW = {
    0 : 'Sunday',
    1 : 'Monday',
    2 : 'Tuesday',
    3 : 'Wednesday',
    4 : 'Thursday',
    5 : 'Friday',
    6 : 'Saturday'
}

sotasession = CachedSession(expire_after=datetime.timedelta(days=1))

@waoarc.route("/")
def about():
    '''Worked All OARC Season 2 intro page'''
    return render_template('aboutwaoarc.html')


@waoarc.route("/leaderboards")
def leaderboards():
    '''Worked All OARC Season 2 leaderboards'''
    facts = {}
    facts['totalqsos'] = QSO.query.filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).count()
    facts['totalusers'] = User.query.count()
    facts['totalcallsigns'] = Callsign.query.count()
    calls = QSO.query.with_entities(QSO.call).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).distinct()
    callsigns = Callsign.query.with_entities(Callsign.name).distinct()
    unclaimed = list(set(calls).difference(callsigns))
    facts['unclaimedcallsigns'] = len(unclaimed)
    facts['dxcctable'] = db.session.query(User.name, db.func.count(db.distinct(QSO.dxcc))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.dxcc)).desc()).limit(10).all()
    facts['totaldxcc'] = QSO.query.with_entities(QSO.dxcc).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).distinct().count()
    facts['cqztable'] = db.session.query(User.name, db.func.count(db.distinct(QSO.cqz))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.cqz)).desc()).limit(10).all()
    facts['totalcqz'] = QSO.query.with_entities(QSO.cqz).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).distinct().count()
    facts['ituztable'] = db.session.query(User.name, db.func.count(db.distinct(QSO.ituz))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.ituz)).desc()).limit(10).all()
    facts['totalituz'] = QSO.query.with_entities(QSO.ituz).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).distinct().count()
    facts['bandtable'] = db.session.query(User.name, db.func.count(db.distinct(QSO.band))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.band)).desc()).limit(10).all()
    facts['totalbands'] = QSO.query.with_entities(QSO.band).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).distinct().count()
    facts['modetable'] = db.session.query(User.name, db.func.count(db.distinct(QSO.mode))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.mode)).desc()).limit(10).all()
    facts['totalmodes'] = QSO.query.with_entities(QSO.mode).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).distinct().count()
    facts['qsostoday'] = db.session.query(QSO.id).filter(QSO.qso_date==datetime.date.today()).count()
    facts['qsosyesterday'] = db.session.query(QSO.id).filter(QSO.qso_date==datetime.date.today()-datetime.timedelta(days=1)).count()
    facts['topcalls'] = db.session.query(User.name, Callsign.name, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name, Callsign.name).order_by(func.count(QSO.id).desc()).limit(1).all()
    facts['topusers'] = db.session.query(User.name, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(func.count(QSO.id).desc()).limit(1).all()
    facts['gridtable'] = db.session.query(User.name, db.func.count(db.distinct(func.left(QSO.gridsquare,4)))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(func.left(QSO.gridsquare,4))).desc()).limit(10).all()
    facts['totalgrids'] = QSO.query.with_entities(func.left(QSO.gridsquare,4)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).distinct().count()
    facts['mygridtable'] = db.session.query(User.name, db.func.count(db.distinct(func.left(QSO.my_gridsquare,4)))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(func.left(QSO.my_gridsquare,4))).desc()).limit(10).all()
    facts['totalmygrids'] = QSO.query.with_entities(func.left(QSO.my_gridsquare,4)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).distinct().count()
    qsobyday = db.session.query(QSO.qso_date, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(QSO.qso_date).order_by(QSO.qso_date.desc()).all()
    qsobyweek = db.session.query(func.date_part('week',QSO.qso_date), func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(func.date_part('week',QSO.qso_date)).order_by(func.date_part('week',QSO.qso_date).desc()).all()
    workedcallsigns = db.session.query(User.name, QSO.call, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.call == Callsign.name).join(User, Callsign.user_id == User.id).group_by(QSO.call, User.name).order_by(func.count(QSO.id).desc()).limit(10).all()
    sotasummits = db.session.query(func.split_part(QSO.sota_ref, '/', 1)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.sota_ref != None).group_by(func.split_part(QSO.sota_ref, '/', 1))
    sotaact = db.session.query(func.split_part(QSO.my_sota_ref, '/', 1)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.my_sota_ref != None).group_by(func.split_part(QSO.my_sota_ref, '/', 1))
    facts['totalassoc'] = sotasummits.union(sotaact).count()
    sotasummits = db.session.query(func.split_part(func.split_part(QSO.sota_ref, '/', 2), '-', 1)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.sota_ref != None).group_by(func.split_part(func.split_part(QSO.sota_ref, '/', 2), '-', 1))
    sotaact = db.session.query(func.split_part(func.split_part(QSO.my_sota_ref, '/', 2), '-', 1)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.my_sota_ref != None).group_by(func.split_part(func.split_part(QSO.my_sota_ref, '/', 2), '-', 1))
    facts['totalregion'] = sotasummits.union(sotaact).count()
    sotasummits = db.session.query(QSO.sota_ref).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.sota_ref != None).group_by(QSO.sota_ref)
    sotaact = db.session.query(QSO.my_sota_ref).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.my_sota_ref != None).group_by(QSO.my_sota_ref)
    facts['totalsummit'] = sotasummits.union(sotaact).count()
    potasummits = db.session.query(func.split_part(QSO.pota_ref, '/', 1)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.pota_ref != None).group_by(func.split_part(QSO.pota_ref, '/', 1))
    potaact = db.session.query(func.split_part(QSO.my_pota_ref, '/', 1)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.my_pota_ref != None).group_by(func.split_part(QSO.my_pota_ref, '/', 1))
    facts['totalpassoc'] = potasummits.union(potaact).count()
    potasummits = db.session.query(func.split_part(func.split_part(QSO.pota_ref, '/', 2), '-', 1)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.pota_ref != None).group_by(func.split_part(func.split_part(QSO.pota_ref, '/', 2), '-', 1))
    potaact = db.session.query(func.split_part(func.split_part(QSO.my_pota_ref, '/', 2), '-', 1)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.my_pota_ref != None).group_by(func.split_part(func.split_part(QSO.my_pota_ref, '/', 2), '-', 1))
    facts['totalpregion'] = potasummits.union(potaact).count()
    potasummits = db.session.query(QSO.pota_ref).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.pota_ref != None).group_by(QSO.pota_ref)
    potaact = db.session.query(QSO.my_pota_ref).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.my_pota_ref != None).group_by(QSO.my_pota_ref)
    facts['totalpsummit'] = potasummits.union(potaact).count()
    facts['timesworkedtable'] = db.session.query(User.name, db.func.count(db.distinct(QSO.station_callsign))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.call == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.station_callsign)).desc()).all()
    facts['callsworkedtable'] = db.session.query(User.name, db.func.count(db.distinct(QSO.call))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.call)).desc()).all()
    worked = { x : y for x,y in facts['callsworkedtable']}
    for call in facts['timesworkedtable']:
        new = {call[0] : [worked.get(call[0], 0) , call[1]]}
        worked.update(new)
    return render_template('leaderboard.html', facts=facts, unclaimed=unclaimed, qsobyday=qsobyday, qsobyweek=qsobyweek, workedcallsigns=workedcallsigns, worked=worked)


@waoarc.route("/gettingstarted")
def gettingstarted():
    '''Worked All OARC Season 2 getting started page'''
    return render_template('gettingstarted.html')

@waoarc.route("/usertable")
def usertable():
    '''Detail of Users and Callsigns tile on Leaderboard'''
    calls = db.session.query(User.name, Callsign.name, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name, Callsign.name).order_by(func.count(QSO.id).desc()).all()
    users = db.session.query(User.name, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(func.count(QSO.id).desc()).all()
    unccalls = QSO.query.with_entities(QSO.call).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).distinct()
    callsigns = Callsign.query.with_entities(Callsign.name).distinct()
    unclaimedcalls = list(set(unccalls).difference(callsigns))
    unclaimedtable = []
    for call in unclaimedcalls:
        line = []
        line.append(call[0])
        line.append(QSO.query.filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.call == call[0]).count())
        unclaimedtable.append(line)
    facts = {}
    facts['timesworkedtable'] = db.session.query(User.name, db.func.count(db.distinct(QSO.station_callsign))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.call == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.station_callsign)).desc()).all()
    facts['callsworkedtable'] = db.session.query(User.name, db.func.count(db.distinct(QSO.call))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.call)).desc()).all()
    worked = { x : y for x,y in facts['callsworkedtable']}
    for call in facts['timesworkedtable']:
        new = {call[0] : [worked.get(call[0], 0) , call[1]]}
        worked.update(new)
    return render_template('usertable.html', calls=calls, unclaimedcalls=unclaimedcalls, unclaimedtable=unclaimedtable, users=users, facts=facts, worked=worked)


@waoarc.route("/userchart")
def userchart():
    calls = db.session.query(func.concat(User.name, " - ", Callsign.name), func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(func.concat(User.name, " - ", Callsign.name)).order_by(func.count(QSO.id).desc()).all()
    labels = list(map(list, zip(*calls)))[0]
    callsignlabels = ['None' if v is None else v for v in labels]
    callsignvalues = list(map(list, zip(*calls)))[1] 
    users = db.session.query(User.name, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(func.count(QSO.id).desc()).all()
    labels = list(map(list, zip(*users)))[0]
    memberlabels = ['None' if v is None else v for v in labels]
    membervalues = list(map(list, zip(*users)))[1]
    unccalls = QSO.query.with_entities(QSO.call).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).distinct()
    callsigns = Callsign.query.with_entities(Callsign.name).distinct()
    unclaimedcalls = list(set(unccalls).difference(callsigns))
    unclaimedtable = []
    for call in unclaimedcalls:
        line = []
        line.append(call[0])
        line.append(QSO.query.filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.call == call[0]).count())
        unclaimedtable.append(line)
    labels = list(map(list, zip(*unclaimedtable)))[0]
    unclaimedlabels = ['None' if v is None else v for v in labels]
    unclaimedvalues = list(map(list, zip(*unclaimedtable)))[1]
    facts = {}
    facts['timesworkedtable'] = db.session.query(User.name, db.func.count(db.distinct(QSO.station_callsign))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.call == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.station_callsign)).desc()).all()
    facts['callsworkedtable'] = db.session.query(User.name, db.func.count(db.distinct(QSO.call))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.call)).desc()).all()
    worked = { x : y for x,y in facts['callsworkedtable']}
    for call in facts['timesworkedtable']:
        new = {call[0] : [worked.get(call[0], 0) , call[1]]}
        worked.update(new)
    for call in worked:
        if type(worked.get(call)) == int:
            new = {call : [worked.get(call) , 0]}
            worked.update(new)
    pprint(worked)
    sortedwork = sorted(worked.items(), key=lambda x:x[1][1], reverse=True)
    return render_template('userchart.html', memberlabels=memberlabels, membervalues=membervalues, callsignlabels=callsignlabels,
                           callsignvalues=callsignvalues, unclaimedlabels=unclaimedlabels, unclaimedvalues=unclaimedvalues, facts=facts,
                           worked=worked, sortedwork=dict(sortedwork))


@waoarc.route("/datestable")
def datestable():
    '''All the date and time related info for the Leaderboard Dates detail page'''
    facts={}
    facts['totalusers'] = User.query.count()
    qsobyday = db.session.query(QSO.qso_date, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(QSO.qso_date).order_by(QSO.qso_date).all()
    usersbyday = db.session.query(QSO.qso_date, User.name, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(QSO.qso_date, User.name).order_by(QSO.qso_date.desc()).order_by(func.count(QSO.id).desc()).all()
    qsobyweek = db.session.query(func.date_part('week',QSO.qso_date), func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(func.date_part('week',QSO.qso_date)).order_by(func.date_part('week',QSO.qso_date)).all()
    usersbyweek = db.session.query(func.date_part('week',QSO.qso_date), User.name, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(func.date_part('week',QSO.qso_date), User.name).order_by(func.date_part('week',QSO.qso_date).desc()).order_by(func.count(QSO.id).desc()).all()
    hourcount = db.session.execute(text('Select h.h as hour, coalesce(count(r.*), 0) as count from generate_series(0, 23) as h LEFT JOIN qso as r on extract(hour from r.time_on) = h.h group by h.h order by h.h'))
    hc = []
    for hour in hourcount:
        hc.append((hour[0],hour[1]))
    dowcount = db.session.execute(text('Select d.d as dow, coalesce(count(r.*), 0) as count from generate_series(0, 6) as d LEFT JOIN qso as r on extract(dow from r.qso_date) = d.d group by d.d order by d.d'))
    dc = []
    for d in dowcount:
        dc.append((DOW[d[0]], d[1], d[0]))
    callsignstreaks = db.session.execute(text("select distinct on (name) name, count(distinct ci.qso_date::date) as num_days from (select ci.qso_date, u.name, dense_rank() over (partition by u.name order by ci.qso_date::date) as seq from qso ci join callsign c on ci.station_callsign = c.name join public.user u on c.user_id = u.id where qso_date >= '2023-07-01' and qso_date <= '2023-08-31') ci group by name, ci.qso_date::date - seq * interval '1 day' order by name, num_days desc"))
    cs = []
    for streak in callsignstreaks:
        cs.append((streak[0], streak[1]))
    return render_template('datestable.html', qsobyday=qsobyday, usersbyday=usersbyday, qsobyweek=qsobyweek, usersbyweek=usersbyweek,
                           facts=facts, hourcount=hc, dowcount=dc, callsignstreak=cs)


@waoarc.route("/dateschart")
def dateschart():
    '''All the date and time related info for the Leaderboard Dates detail page'''
    qsobyday = db.session.query(QSO.qso_date, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(QSO.qso_date).order_by(QSO.qso_date).all()
    daylabels = list(map(list, zip(*qsobyday)))[0]
    daydates = []
    for label in daylabels:
        daydates.append(label.strftime('%Y-%m-%d'))
    dayvalues = list(map(list, zip(*qsobyday)))[1]
    qsobyweek = db.session.query(func.date_part('week',QSO.qso_date), func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(func.date_part('week',QSO.qso_date)).order_by(func.date_part('week',QSO.qso_date)).all()
    weeklabels = list(map(list, zip(*qsobyweek)))[0]
    weekdates = []
    for label in weeklabels:
        weekdates.append(label - 25)
    weekvalues = list(map(list, zip(*qsobyweek)))[1]
    hourcount = db.session.execute(text('Select h.h as hour, coalesce(count(r.*), 0) as count from generate_series(0, 23) as h LEFT JOIN qso as r on extract(hour from r.time_on) = h.h group by h.h order by h.h'))
    hc = []
    for hour in hourcount:
        hc.append((hour[0],hour[1]))
    dowcount = db.session.execute(text('Select d.d as dow, coalesce(count(r.*), 0) as count from generate_series(0, 6) as d LEFT JOIN qso as r on extract(dow from r.qso_date) = d.d group by d.d order by d.d'))
    dc = []
    for d in dowcount:
        dc.append((DOW[d[0]], d[1]))
    callsignstreaks = db.session.execute(text("select distinct on (name) name, count(distinct ci.qso_date::date) as num_days from (select ci.qso_date, u.name, dense_rank() over (partition by u.name order by ci.qso_date::date) as seq from qso ci join callsign c on ci.station_callsign = c.name join public.user u on c.user_id = u.id where qso_date >= '2023-07-01' and qso_date <= '2023-08-31') ci group by name, ci.qso_date::date - seq * interval '1 day' order by name, num_days desc"))
    cs = []
    for streak in callsignstreaks:
        if streak[1] > 1:
            cs.append((streak[0], streak[1]))
    cs.sort(key=lambda a: a[1], reverse=True)
    return render_template('dateschart.html', daylabels=daydates, dayvalues=dayvalues, weeklabels=weekdates,
                           weekvalues=weekvalues, hourcount=hc, dowcount=dc, callsignstreak=cs)

@waoarc.route("/bands")
def bands():
    qsobybands = db.session.query(QSO.band, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(QSO.band).order_by(func.count(QSO.id).desc()).all()
    labels = list(map(list, zip(*qsobybands)))[0]
    bandlabels = ['None' if v is None else v for v in labels]
    bandvalues = list(map(list, zip(*qsobybands)))[1]
    qsobymodes = db.session.query(QSO.mode, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(QSO.mode).order_by(func.count(QSO.id).desc()).all()
    labels = list(map(list, zip(*qsobymodes)))[0]
    modelabels = ['None' if v is None else v for v in labels]
    modevalues = list(map(list, zip(*qsobymodes)))[1]
    qsobypropmodes = db.session.query(QSO.prop_mode, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(QSO.prop_mode).order_by(func.count(QSO.id).desc()).all()
    labels = list(map(list, zip(*qsobypropmodes)))[0]
    propmodelabels = ['None' if v is None else v for v in labels]
    propmodevalues = list(map(list, zip(*qsobypropmodes)))[1]
    return render_template('bands.html', bandlabels=bandlabels, bandvalues=bandvalues, modelabels=modelabels, modevalues=modevalues, propmodelabels=propmodelabels,
                           propmodevalues=propmodevalues)


@waoarc.route("/dxccchart")
def dxccchart():
    qsobydxcc = db.session.query(QSO.dxcc, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(QSO.dxcc).order_by(func.count(QSO.id).desc()).all()
    labels = list(map(list, zip(*qsobydxcc)))[0]
    dxccnums = ['None' if v is None else v for v in labels]
    dxcclabels = []
    for label in dxccnums:
        if label == "None":
            dxcclabels.append("None")
        else:
            dxcclabels.append(countrylookup(label))
    dxccvalues = list(map(list, zip(*qsobydxcc)))[1]
    qsobycqz = db.session.query(QSO.cqz, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(QSO.cqz).order_by(func.count(QSO.id).desc()).all()
    labels = list(map(list, zip(*qsobycqz)))[0]
    cqzlabels = ['None' if v is None else v for v in labels]
    cqzvalues = list(map(list, zip(*qsobycqz)))[1]
    qsobyituz = db.session.query(QSO.ituz, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(QSO.ituz).order_by(func.count(QSO.id).desc()).all()
    labels = list(map(list, zip(*qsobyituz)))[0]
    ituzlabels = ['None' if v is None else v for v in labels]
    ituzvalues = list(map(list, zip(*qsobyituz)))[1]
    dxccmembers = db.session.query(func.concat(User.name, " (", func.string_agg(db.distinct(Callsign.name), ', '), ")"), db.func.count(db.distinct(QSO.dxcc))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.dxcc)).desc()).all()
    cqzmembers = db.session.query(func.concat(User.name, " (", func.string_agg(db.distinct(Callsign.name), ', '), ")"), db.func.count(db.distinct(QSO.cqz))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.cqz)).desc()).all()
    ituzmembers = db.session.query(func.concat(User.name, " (", func.string_agg(db.distinct(Callsign.name), ', '), ")"), db.func.count(db.distinct(QSO.ituz))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.ituz)).desc()).all()
    return render_template('dxccchart.html', dxcclabels=dxcclabels, dxccvalues=dxccvalues, cqzlabels=cqzlabels, cqzvalues=cqzvalues,
                           ituzlabels=ituzlabels, ituzvalues=ituzvalues, dxccmembers=dxccmembers, cqzmembers=cqzmembers,
                           ituzmembers=ituzmembers)    


@waoarc.route("/dxcctable")
def dxcctable():
    dxccmembers = db.session.query(User.name, func.string_agg(db.distinct(Callsign.name), ', '), db.func.count(db.distinct(QSO.dxcc))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.dxcc)).desc()).all()
    cqzmembers = db.session.query(User.name, func.string_agg(db.distinct(Callsign.name), ', '), db.func.count(db.distinct(QSO.cqz))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.cqz)).desc()).all()
    ituzmembers = db.session.query(User.name, func.string_agg(db.distinct(Callsign.name), ', '), db.func.count(db.distinct(QSO.ituz))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.ituz)).desc()).all()
    return render_template('dxcctable.html', dxccmembers=dxccmembers, cqzmembers=cqzmembers, ituzmembers=ituzmembers)


@waoarc.route("/dxccmap")
def dxccmap():
    totaldxcc = QSO.query.with_entities(QSO.dxcc).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).distinct().count()    
    dxccsquares = QSO.query.with_entities(QSO.dxcc, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(QSO.dxcc).all()
    dxcccount = {}
    for dxcc, count in dxccsquares:
        if dxcc != None:
            dxcccount[dxcc] = count
    with open("./dxcc.geojson") as f:
        gj = gjload(f)
    for feature in gj['features']:
        # print(feature['properties']['dxcc_entity_code'])
        if dxcccount.get(feature['properties']['dxcc_entity_code'], 0) != 0:
            feature['properties']['count'] = dxcccount.get(feature['properties']['dxcc_entity_code'], 0)
            # print(dxcccount.get(feature['properties']['dxcc_entity_code'], 0), feature['properties']['dxcc_name'])
    return render_template('dxccmap.html', totaldxcc=totaldxcc, dxccsquares=gj)

@waoarc.route("/gridchart")
def gridchart():
    qsobygrid = db.session.query(func.left(QSO.gridsquare,4), func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(func.left(QSO.gridsquare,4)).order_by(func.count(QSO.id).desc()).all()
    labels = list(map(list, zip(*qsobygrid)))[0]
    gridlabels = ['None' if v is None else v for v in labels]
    gridvalues = list(map(list, zip(*qsobygrid)))[1]
    qsobymygrid = db.session.query(func.left(QSO.my_gridsquare,4), func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(func.left(QSO.my_gridsquare,4)).order_by(func.count(QSO.id).desc()).all()
    labels = list(map(list, zip(*qsobymygrid)))[0]
    mygridlabels = ['None' if v is None else v for v in labels]
    mygridvalues = list(map(list, zip(*qsobymygrid)))[1]
    gridmembers = db.session.query(func.concat(User.name, ' : ', func.string_agg(db.distinct(Callsign.name), ', ')), db.func.count(db.distinct(func.left(QSO.gridsquare,4)))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(func.left(QSO.gridsquare,4))).desc()).all()
    labels = list(map(list, zip(*gridmembers)))[0]
    memberlabels = ['None' if v is None else v for v in labels]
    membervalues = list(map(list, zip(*gridmembers)))[1]
    mygridmembers = db.session.query(func.concat(User.name, ' : ',func.string_agg(db.distinct(Callsign.name), ', ')), db.func.count(db.distinct(func.left(QSO.my_gridsquare,4)))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(func.left(QSO.my_gridsquare,4))).desc()).all()
    labels = list(map(list, zip(*mygridmembers)))[0]
    mymemberlabels = ['None' if v is None else v for v in labels]
    mymembervalues = list(map(list, zip(*mygridmembers)))[1]
    return render_template('gridchart.html', gridlabels=gridlabels, gridvalues=gridvalues, mygridlabels=mygridlabels,
                           mygridvalues=mygridvalues, memberlabels=memberlabels, membervalues=membervalues,
                           mymemberlabels=mymemberlabels, mymembervalues=mymembervalues)


@waoarc.route("/gridtable")
def gridtable():
    gridmembers = db.session.query(User.name, func.string_agg(db.distinct(Callsign.name), ', '), db.func.count(db.distinct(func.left(QSO.gridsquare,4)))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(func.left(QSO.gridsquare,4))).desc()).all()
    mygridmembers = db.session.query(User.name, func.string_agg(db.distinct(Callsign.name), ', '), db.func.count(db.distinct(func.left(QSO.my_gridsquare,4)))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(func.left(QSO.my_gridsquare,4))).desc()).all()
    gridqsos = db.session.query(func.left(QSO.gridsquare, 4), func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(func.left(QSO.gridsquare,4)).order_by(func.left(QSO.gridsquare,4).desc()).all()
    mygridqsos = db.session.query(func.left(QSO.my_gridsquare, 4), func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(func.left(QSO.my_gridsquare,4)).order_by(func.left(QSO.my_gridsquare,4).desc()).all()
    return render_template('gridtable.html', gridmembers=gridmembers, mygridmembers=mygridmembers, gridqsos=gridqsos, mygridqsos=mygridqsos)


@waoarc.route("/workedmap")
def workedmap():
    squares = db.session.query(func.left(QSO.gridsquare,4), func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(func.left(QSO.gridsquare,4)).all()
    features = []
    mlayer = {}
    for square in squares:
        if square[0] is not None:
            lat = (mh.to_location(square[0], center=True)[0])
            lon = (mh.to_location(square[0], center=True)[1])
            my_poly = Polygon([[(lon - 1.0, lat - 0.5),(lon + 1.0, lat - 0.5),(lon + 1.0, lat + 0.5), (lon - 1.0, lat + 0.5), (lon - 1.0, lat - 0.5)]])
            features.append(Feature(geometry=my_poly, properties={"qsos": square[1], "name": str(square[0])}))
            mlayer[str(square[0])] = ([lat, lon])
    gridsquares = FeatureCollection(features)
    totalgrids = QSO.query.with_entities(func.left(QSO.gridsquare,4)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).distinct().count()
    return render_template('workedmap.html', gridsquares=gridsquares, totalgrids=totalgrids, mlayer=mlayer)


@waoarc.route("/activatedmap")
def activatedmap():
    squares = db.session.query(func.left(QSO.my_gridsquare,4), func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(func.left(QSO.my_gridsquare,4)).all()
    features = []
    mlayer = {}
    for square in squares:
        if square[0] is not None:
            lat = (mh.to_location(square[0], center=True)[0])
            lon = (mh.to_location(square[0], center=True)[1])
            my_poly = Polygon([[(lon - 1.0, lat - 0.5),(lon + 1.0, lat - 0.5),(lon + 1.0, lat + 0.5), (lon - 1.0, lat + 0.5), (lon - 1.0, lat - 0.5)]])
            features.append(Feature(geometry=my_poly, properties={"qsos": square[1], "name": str(square[0])}))
            mlayer[str(square[0])] = ([lat, lon])
    gridsquares = FeatureCollection(features)
    totalgrids = QSO.query.with_entities(func.left(QSO.my_gridsquare,4)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).distinct().count()
    return render_template('workedmap.html', gridsquares=gridsquares, totalgrids=totalgrids, mlayer=mlayer)

@waoarc.route("/edgetest")
def edgetest():
    squares = db.session.query(func.left(QSO.gridsquare,4), func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(func.left(QSO.gridsquare,4)).all()
    features = []
    mlayer = {}
    for square in squares:
        if square[0] is not None:
            lat = (mh.to_location(square[0], center=True)[0])
            lon = (mh.to_location(square[0], center=True)[1])
            my_poly = Polygon([[(lon - 1.0, lat - 0.5),(lon + 1.0, lat - 0.5),(lon + 1.0, lat + 0.5), (lon - 1.0, lat + 0.5), (lon - 1.0, lat - 0.5)]])
            features.append(Feature(geometry=my_poly, properties={"qsos": square[1], "name": str(square[0])}))
            mlayer[str(square[0])] = ([lat, lon])
    gridsquares = FeatureCollection(features)
    totalgrids = QSO.query.with_entities(func.left(QSO.gridsquare,4)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).distinct().count()
    return render_template('edgetest.html', gridsquares=gridsquares, totalgrids=totalgrids, mlayer=mlayer)


@waoarc.route("/scoreboard")
def scoreboard():
    '''scores all members by rariety of modes, bands, calls, grids, SOTA, etc. Rough rule is that being the only
    member to work something scores 24 points, two members working is 12 each, three is 8 each, four is 6,
    five is 5, six is 4, seven and up is one point up to 24 members when zero points are scored'''
    members = db.session.query(Callsign.name, User.name).join(User, Callsign.user_id == User.id).all()
    callsigns = QSO.query.with_entities(func.count(QSO.id), QSO.call).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(QSO.call).order_by(func.count(QSO.id).desc()).having(func.count(QSO.id) <= 24).all()
    bands = QSO.query.with_entities(func.count(QSO.id), QSO.band).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.band != None).group_by(QSO.band).order_by(func.count(QSO.id).desc()).having(func.count(QSO.id) <= 24).all()
    modes = QSO.query.with_entities(func.count(QSO.id), QSO.mode).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(QSO.mode).order_by(func.count(QSO.id).desc()).having(func.count(QSO.id) <= 24).all()
    grids = QSO.query.with_entities(func.count(QSO.id), func.left(QSO.gridsquare,4)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(func.left(QSO.gridsquare,4)).order_by(func.count(QSO.id).desc()).having(func.count(QSO.id) <= 24).all()
    mygrids = QSO.query.with_entities(func.count(QSO.id), func.left(QSO.my_gridsquare,4)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(func.left(QSO.my_gridsquare,4)).order_by(func.count(QSO.id).desc()).having(func.count(QSO.id) <= 24).all()
    callscore = {}
    for quant, callsign in callsigns:
        callscore[callsign] = rarity[quant]
    bandscore = {}
    for quant, band in bands:
        bandscore[band] = rarity[quant]    
    modescore = {}
    for quant, mode in modes:
        modescore[mode] = rarity[quant]
    gridscore = {}
    for quant, grid in grids:
        gridscore[grid] = rarity[quant]
    mygridscore = {}
    for quant, mygrid in mygrids:
        mygridscore[mygrid] = rarity[quant]
    callsignscores = {}
    for callsign, user in members:
        # print(callsign, user)
        callsignqsos = db.session.query(QSO.id, QSO.call, QSO.band, QSO.mode, QSO.gridsquare, QSO.my_gridsquare).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.station_callsign == callsign)
        callsignscores[callsign] = {}
        qsocount = callsignqsos.count()
        callsignscores[callsign]['qsos'] = qsocount
        cscalls = set([r[0] for r in callsignqsos.filter(QSO.call.is_not(None)).values(QSO.call)])
        csmodes = set([r[0] for r in callsignqsos.filter(QSO.mode.is_not(None)).values(QSO.mode)])
        csbands = set([r[0] for r in callsignqsos.filter(QSO.band.is_not(None)).values(QSO.band)])
        csgrids = set([r[0] for r in callsignqsos.filter(QSO.gridsquare.is_not(None)).values(func.left(QSO.gridsquare, 4))])
        csmygrids = set([r[0] for r in callsignqsos.filter(QSO.my_gridsquare.is_not(None)).values(func.left(QSO.my_gridsquare, 4))])
        cascore = 0
        for call in cscalls:
            cascore += callscore.get(call, 0)
        callsignscores[callsign]['callsscore'] = cascore
        mscore = 0
        for mode in csmodes:
            mscore += modescore.get(mode, 0)
        callsignscores[callsign]['modescore'] = mscore
        bscore = 0
        for band in csbands:
            bscore += bandscore.get(band, 0)
        callsignscores[callsign]['bandscore'] = bscore
        gscore = 0
        for grid in csgrids:
            gscore += gridscore.get(grid, 0)
        callsignscores[callsign]['gridscore'] = gscore
        mgscore = 0
        for mgrid in csmygrids:
            mgscore += mygridscore.get(mgrid, 0)
        callsignscores[callsign]['mygridscore'] = mgscore
        callsignscores[callsign]['totalscore'] = cascore + mscore + bscore + gscore + mgscore
        if qsocount > 0:
            callsignscores[callsign]['scoreperqso'] = round(((cascore + mscore + bscore + gscore + mgscore) / qsocount),2)
        # pprint(callsignqsos.filter(QSO.call.in_(callsignqsos.QSO.call)).all())
    userscores = {}
    for callsign, username in members:
        if username not in userscores:
            userscores[username] = {}
        if 'callsscore' not in userscores[username]:
            userscores[username]['callsscore'] = callsignscores[callsign].get('callsscore', 0)
        else:
            userscores[username]['callsscore'] += callsignscores[callsign].get('callsscore', 0)
        if 'modescore' not in userscores[username]:
            userscores[username]['modescore'] = callsignscores[callsign].get('modescore', 0)
        else:
            userscores[username]['modescore'] += callsignscores[callsign].get('modescore', 0)
        if 'bandscore' not in userscores[username]:
            userscores[username]['bandscore'] = callsignscores[callsign].get('bandscore', 0)
        else:
            userscores[username]['bandscore'] += callsignscores[callsign].get('bandscore', 0)
        if 'gridscore' not in userscores[username]:
            userscores[username]['gridscore'] = callsignscores[callsign].get('gridscore', 0)
        else:
            userscores[username]['gridscore'] += callsignscores[callsign].get('gridscore', 0)
        if 'mygridscore' not in userscores[username]:
            userscores[username]['mygridscore'] = callsignscores[callsign].get('mygridscore', 0)
        else:
            userscores[username]['mygridscore'] += callsignscores[callsign].get('mygridscore', 0)
        if 'totalscore' not in userscores[username]:
            userscores[username]['totalscore'] = callsignscores[callsign].get('totalscore', 0)
        else:
            userscores[username]['totalscore'] += callsignscores[callsign].get('totalscore', 0)
        if 'qsos' not in userscores[username]:
            userscores[username]['qsos'] = callsignscores[callsign].get('qsos', 0)
        else:
            userscores[username]['qsos'] += callsignscores[callsign].get('qsos', 0)
    return render_template('scoreboard.html', callsignscores=callsignscores, callscore=callscore, bandscore=bandscore,
                           modescore=modescore, gridscore=gridscore, mygridscore=mygridscore, userscores=userscores)


@waoarc.route("/sotatable")
def sotatable():
    '''Find all SOTA QSOs and plot them on a map'''
    summitqsos = QSO.query.with_entities(QSO.qso_date, QSO.time_on, QSO.station_callsign, QSO.my_sota_ref, QSO.call, QSO.gridsquare, QSO.lat, QSO.lon).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.my_sota_ref != None, QSO.sota_ref == None).all()
    s2sqsos = QSO.query.with_entities(QSO.qso_date, QSO.time_on, QSO.station_callsign, QSO.my_sota_ref, QSO.call, QSO.sota_ref).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.my_sota_ref != None, QSO.sota_ref != None).all()
    chaserqsos = QSO.query.with_entities(QSO.qso_date, QSO.time_on, QSO.station_callsign, QSO.my_gridsquare, QSO.my_lat, QSO.my_lon, QSO.call, QSO.sota_ref).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.my_sota_ref == None, QSO.sota_ref != None).all()
    return render_template('sotatable.html', summitqsos=summitqsos, s2sqsos=s2sqsos, chaserqsos=chaserqsos)


@waoarc.route("/sotachart")
def sotachart():
    sotaactivations = db.session.query(QSO.sota_ref).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.sota_ref != None)
    sotachases = db.session.query(QSO.my_sota_ref).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.my_sota_ref != None)
    sotasummits = sotaactivations.union_all(sotachases).all()
    summits = []
    for summit in sotasummits:
        if summit[0]:
            url = ("https://api2.sota.org.uk/api/summits/" + summit[0])
            sotasummit = sotasession.request("GET", url)
            if sotasummit.status_code == 200:
                slice = next((i for i, item in enumerate(summits) if item["summitCode"] == sotasummit.json()['summitCode']), None)
                if (not slice) and (slice != 0):
                    summits.append({ "summitCode" : sotasummit.json()['summitCode'], 'count' : 1, 'name' : sotasummit.json()['name'], 'lat' : sotasummit.json()['latitude'], 'lon' : sotasummit.json()['longitude'],
                                                                'points' : sotasummit.json()['points'], 'regionName' : sotasummit.json()['regionName'], 'regionCode' : sotasummit.json()['regionCode'],
                                                                'associationName' : sotasummit.json()['associationName'], 'associationCode' : sotasummit.json()['associationCode']})
                else:
                    summits[slice]['count'] += 1
    # pprint(summits)
    return render_template('sotachart.html', summits=json.dumps(summits))


@waoarc.route("/sotamap")
def sotamap():
    sotaactivations = db.session.query(QSO.sota_ref).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.sota_ref != None)
    sotachases = db.session.query(QSO.my_sota_ref).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.my_sota_ref != None)
    sotasummits = sotaactivations.union_all(sotachases).all()
    summits = []
    for summit in sotasummits:
        if summit[0]:
            url = ("https://api2.sota.org.uk/api/summits/" + summit[0])
            sotasummit = sotasession.request("GET", url)
            if sotasummit.status_code == 200:
                slice = next((i for i, item in enumerate(summits) if item["summitCode"] == sotasummit.json()['summitCode']), None)
                # print(summit[0], '---000', slice)
                if (not slice) and (slice != 0):
                    summits.append({ "summitCode" : sotasummit.json()['summitCode'], 'count' : 1, 'name' : sotasummit.json()['name'], 'lat' : sotasummit.json()['latitude'], 'lon' : sotasummit.json()['longitude'],
                                                                'points' : sotasummit.json()['points'], 'regionName' : sotasummit.json()['regionName'], 'regionCode' : sotasummit.json()['regionCode'],
                                                                'associationName' : sotasummit.json()['associationName'], 'associationCode' : sotasummit.json()['associationCode'] })
                else:
                    summits[slice]['count'] += 1
    regions = set()
    assoc = set()
    for summit in summits:
        regions.add(summit['regionCode'])
        assoc.add(summit['associationCode'])
        summit['popup'] = ("<p>" + summit['summitCode'] + " : " + summit['name'] + " in " + summit['regionName'] + " of " + summit['associationName'] + ".</br> Worth "
                           + str(summit['points']) + " points. Activated " + str(summit['count']) + " times.</p></br><a target='_blank' href='https://sotl.as/summits/" + summit['summitCode'] + "'>Click to view on SOTLAS</a>") 
    return render_template('sotamap.html', summitcount=len(summits), regioncount=len(regions), associationcount=len(assoc), markers=summits)


@waoarc.route("/potatable")
def potatable():
    '''Find all SOTA QSOs and plot them on a map'''
    summitqsos = QSO.query.with_entities(QSO.qso_date, QSO.time_on, QSO.station_callsign, QSO.my_pota_ref, QSO.call, QSO.gridsquare, QSO.lat, QSO.lon).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.my_pota_ref != None, QSO.pota_ref == None).all()
    s2sqsos = QSO.query.with_entities(QSO.qso_date, QSO.time_on, QSO.station_callsign, QSO.my_pota_ref, QSO.call, QSO.pota_ref).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.my_pota_ref != None, QSO.pota_ref != None).all()
    chaserqsos = QSO.query.with_entities(QSO.qso_date, QSO.time_on, QSO.station_callsign, QSO.my_gridsquare, QSO.my_lat, QSO.my_lon, QSO.call, QSO.pota_ref).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.my_pota_ref == None, QSO.pota_ref != None).all()
    return render_template('potatable.html', summitqsos=summitqsos, s2sqsos=s2sqsos, chaserqsos=chaserqsos)


@waoarc.route("/potachart")
def potachart():
    potaactivations = db.session.query(QSO.pota_ref).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.pota_ref != None)
    potachases = db.session.query(QSO.my_pota_ref).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.my_pota_ref != None)
    potasummits = potaactivations.union_all(potachases).all()
    pprint(potasummits)
    summits = []
    for summit in potasummits:
        if summit[0]:
            url = ("https://api.pota.app/park/" + summit[0])
            potasummit = sotasession.request("GET", url)
            print(potasummit.json())
            if potasummit.status_code == 200:
                slice = next((i for i, item in enumerate(summits) if item["reference"] == potasummit.json()['reference']), None)
                if (not slice) and (slice != 0):
                    summits.append({ "reference" : potasummit.json()['reference'], 'count' : 1, 'name' : potasummit.json()['name'], 'lat' : potasummit.json()['latitude'], 'lon' : potasummit.json()['longitude'],
                                                                'locationName' : potasummit.json()['locationName'], 'locationDesc' : potasummit.json()['locationDesc'],
                                                                'entityName' : potasummit.json()['entityName']})
                else:
                    summits[slice]['count'] += 1
    # pprint(summits)
    return render_template('potachart.html', summits=json.dumps(summits))


@waoarc.route("/potamap")
def potamap():
    potaactivations = db.session.query(QSO.pota_ref).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.pota_ref != None)
    potachases = db.session.query(QSO.my_pota_ref).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.my_pota_ref != None)
    potasummits = potaactivations.union_all(potachases).all()
    summits = []
    for summit in potasummits:
        if summit[0]:
            url = ("https://api.pota.app/park/" + summit[0])
            potasummit = sotasession.request("GET", url)
            if potasummit.status_code == 200:
                slice = next((i for i, item in enumerate(summits) if item["reference"] == potasummit.json()['reference']), None)
                # print(summit[0], '---000', slice)
                if (not slice) and (slice != 0):
                    summits.append({ "reference" : potasummit.json()['reference'], 'count' : 1, 'name' : potasummit.json()['name'], 'lat' : potasummit.json()['latitude'], 'lon' : potasummit.json()['longitude'],
                                                                'locationName' : potasummit.json()['locationName'], 'locationDesc' : potasummit.json()['locationDesc'],
                                                                'entityName' : potasummit.json()['entityName']})
                else:
                    summits[slice]['count'] += 1
    regions = set()
    assoc = set()
    for summit in summits:
        regions.add(summit['locationDesc'])
        assoc.add(summit['entityName'])
        summit['popup'] = ("<p>" + summit['reference'] + " : " + summit['name'] + " in " + summit['locationName'] + " of " + summit['entityName'] + ".</br>Activated " + str(summit['count'])
                           + " times.</p></br><a target='_blank' href='https://pota.app/#/park/" + summit['reference'] + "'>Click to view on POTA Site</a>")
    pprint(summits)
    return render_template('potamap.html', summitcount=len(summits), regioncount=len(regions), associationcount=len(assoc), markers=summits)