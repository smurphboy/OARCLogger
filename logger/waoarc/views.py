import datetime
import operator
import os

import maidenhead as mh
from flask import (Blueprint, abort, current_app, flash, jsonify, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from geojson import Feature, Polygon, FeatureCollection, load as gjload
from pprint import pprint
from sqlalchemy import desc, func, and_
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
    return render_template('leaderboard.html', facts=facts, unclaimed=unclaimed, qsobyday=qsobyday, qsobyweek=qsobyweek, workedcallsigns=workedcallsigns)


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
    return render_template('usertable.html', calls=calls, unclaimedcalls=unclaimedcalls, unclaimedtable=unclaimedtable, users=users)


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
    return render_template('userchart.html', memberlabels=memberlabels, membervalues=membervalues, callsignlabels=callsignlabels,
                           callsignvalues=callsignvalues, unclaimedlabels=unclaimedlabels, unclaimedvalues=unclaimedvalues)


@waoarc.route("/dates")
def dates():
    '''All the date and time related info for the Leaderboard Dates detail page'''
    facts={}
    facts['totalusers'] = User.query.count()
    qsobyday = db.session.query(QSO.qso_date, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(QSO.qso_date).order_by(QSO.qso_date).all()
    daylabels = list(map(list, zip(*qsobyday)))[0]
    daydates = []
    for label in daylabels:
        daydates.append(label.strftime('%Y-%m-%d'))
    dayvalues = list(map(list, zip(*qsobyday)))[1]
    usersbyday = db.session.query(QSO.qso_date, User.name, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(QSO.qso_date, User.name).order_by(QSO.qso_date.desc()).order_by(func.count(QSO.id).desc()).all()
    qsobyweek = db.session.query(func.date_part('week',QSO.qso_date), func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(func.date_part('week',QSO.qso_date)).order_by(func.date_part('week',QSO.qso_date)).all()
    weeklabels = list(map(list, zip(*qsobyweek)))[0]
    weekdates = []
    for label in weeklabels:
        weekdates.append(label - 25)
    weekvalues = list(map(list, zip(*qsobyweek)))[1]
    usersbyweek = db.session.query(func.date_part('week',QSO.qso_date), User.name, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(func.date_part('week',QSO.qso_date), User.name).order_by(func.date_part('week',QSO.qso_date).desc()).order_by(func.count(QSO.id).desc()).all()
    return render_template('dates.html', qsobyday=qsobyday, daylabels=daydates, dayvalues=dayvalues, weeklabels=weekdates,
                           weekvalues=weekvalues, usersbyday=usersbyday, qsobyweek=qsobyweek, usersbyweek=usersbyweek, facts=facts)

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
            print(dxcccount.get(feature['properties']['dxcc_entity_code'], 0), feature['properties']['dxcc_name'])
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
    userscores = {}
    callsignscores = {}
    for callsign, user in members:
        # print(callsign, user)
        callsignqsos = db.session.query(QSO.id, QSO.call, QSO.band, QSO.mode, QSO.gridsquare, QSO.my_gridsquare).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.station_callsign == callsign)
        callsignscores[callsign] = {}
        callsignscores[callsign]['qsos'] = callsignqsos.count()
        cscalls = set([r[0] for r in callsignqsos.filter(QSO.call.is_not(None)).values(QSO.call)])
        csmodes = set([r[0] for r in callsignqsos.filter(QSO.mode.is_not(None)).values(QSO.mode)])
        csbands = set([r[0] for r in callsignqsos.filter(QSO.band.is_not(None)).values(QSO.band)])
        csgrids = set([r[0] for r in callsignqsos.filter(QSO.gridsquare.is_not(None)).values(QSO.gridsquare)])
        csmygrids = set([r[0] for r in callsignqsos.filter(QSO.my_gridsquare.is_not(None)).values(QSO.my_gridsquare)])
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
        # pprint(callsignqsos.filter(QSO.call.in_(callsignqsos.QSO.call)).all())
    # pprint(callsignscores)
    return render_template('scoreboard.html', callsignscores=callsignscores, callscore=callscore, bandscore=bandscore,
                           modescore=modescore, gridscore=gridscore, mygridscore=mygridscore)