import datetime
import operator
import os
import math

import maidenhead as mh
from flask import (Blueprint, abort, current_app, flash, jsonify, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from geojson import Feature, Polygon, FeatureCollection, load as gjload
from pprint import pprint
from sqlalchemy import desc, func, and_, column, or_
from werkzeug.security import check_password_hash, generate_password_hash

from logger.forms import CallsignForm
from logger.helpers import countrylookup
from logger.models import QSO, Callsign, User, db

dashboard = Blueprint('dashboard', __name__, template_folder='../templates/dashboard')

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

@dashboard.route("/leaderboards")
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


@dashboard.route("/gettingstarted")
def gettingstarted():
    '''Worked All OARC Season 2 getting started page'''
    return render_template('gettingstarted.html')

@dashboard.route("/usertable")
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


@dashboard.route("/userchart")
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


@dashboard.route("/mydates/<user>")
def mydates(user):
    '''All the date and time related info for the Dashboard Dates detail page'''
    usercalls = Callsign.query.with_entities(Callsign.name).join(User, Callsign.user_id==User.id).filter(User.name==user).all()
    userfirstqso = QSO.query.with_entities(QSO.qso_date).filter(QSO.station_callsign.in_([lis[0] for lis in usercalls])).order_by(QSO.qso_date).first()
    userlastqso = QSO.query.with_entities(QSO.qso_date).filter(QSO.station_callsign.in_([lis[0] for lis in usercalls])).order_by(QSO.qso_date.desc()).first()
    date_list = func.generate_series(userfirstqso[0], userlastqso[0], '1 day').alias('day')
    day = column('day')
    userqsosbyday = db.session.query(day, func.count(QSO.id)).select_from(date_list).outerjoin(QSO, and_((func.date_trunc('day', QSO.qso_date) == day), QSO.station_callsign.in_([lis[0] for lis in usercalls]))).group_by(day).order_by(day).all()
    daylabels = list(map(list, zip(*userqsosbyday)))[0]
    daydates = []
    for label in daylabels:
        daydates.append(label.strftime('%Y-%m-%d'))
    dayvalues = list(map(list, zip(*userqsosbyday)))[1]
    userqsosbyweek = db.session.query(func.to_char(day, 'WW'), func.count(QSO.id)).select_from(date_list).outerjoin(QSO, and_((func.date_trunc('day', QSO.qso_date) == day), QSO.station_callsign.in_([lis[0] for lis in usercalls]))).group_by(func.to_char(day, 'WW')).order_by(func.to_char(day, 'WW')).all()
    qsobyweek = db.session.query(func.date_part('week',QSO.qso_date), func.count(QSO.id)).filter(QSO.station_callsign.in_([lis[0] for lis in usercalls])).group_by(func.date_part('week',QSO.qso_date)).order_by(func.date_part('week',QSO.qso_date)).all()
    weeklabels = list(map(list, zip(*userqsosbyweek)))[0]
    weekdates = []
    for label in weeklabels:
        weekdates.append(label)
    weekvalues = list(map(list, zip(*userqsosbyweek)))[1]
    hour_list = func.generate_series(0, 23).alias('hour')
    hour = column('hour')
    userqsosbyhour = db.session.query(hour, func.count(QSO.id)).select_from(hour_list).outerjoin(QSO, and_((func.extract('hour', QSO.time_on) == hour), QSO.station_callsign.in_([lis[0] for lis in usercalls]))).group_by(hour).order_by(hour).all()
    hc = []
    for hour in userqsosbyhour:
        hc.append((hour[0],hour[1]))
    dow_list = func.generate_series(0, 6).alias('dow')
    dow = column('dow')
    userqsobydow = db.session.query(dow, func.count(QSO.id)).select_from(dow_list).outerjoin(QSO, and_((func.extract('dow', QSO.qso_date) == dow), QSO.station_callsign.in_([lis[0] for lis in usercalls]))).group_by(dow).order_by(dow).all()
    dc = []
    for d in userqsobydow:
        dc.append((DOW[d[0]], d[1], d[0]))
    return render_template('mydates.html', qsobyday=userqsosbyday, user=user, daylabels=daydates, dayvalues=dayvalues, weeklabels=weekdates,
                           weekvalues=weekvalues, qsobyweek=userqsosbyweek, hc=hc, dc=dc)

@dashboard.route("/mybandschart/<user>")
def mybandschart(user):
    usercalls = Callsign.query.with_entities(Callsign.name).join(User, Callsign.user_id==User.id).filter(User.name==user).all()
    qsobybands = db.session.query(QSO.band, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.station_callsign.in_([lis[0] for lis in usercalls])).group_by(QSO.band).order_by(func.count(QSO.id).desc()).all()
    labels = list(map(list, zip(*qsobybands)))[0]
    bandlabels = ['None' if v is None else v for v in labels]
    bandvalues = list(map(list, zip(*qsobybands)))[1]
    qsobymodes = db.session.query(QSO.mode, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.station_callsign.in_([lis[0] for lis in usercalls])).group_by(QSO.mode).order_by(func.count(QSO.id).desc()).all()
    labels = list(map(list, zip(*qsobymodes)))[0]
    modelabels = ['None' if v is None else v for v in labels]
    modevalues = list(map(list, zip(*qsobymodes)))[1]
    qsobypropmodes = db.session.query(QSO.prop_mode, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.station_callsign.in_([lis[0] for lis in usercalls])).group_by(QSO.prop_mode).order_by(func.count(QSO.id).desc()).all()
    labels = list(map(list, zip(*qsobypropmodes)))[0]
    propmodelabels = ['None' if v is None else v for v in labels]
    propmodevalues = list(map(list, zip(*qsobypropmodes)))[1]
    bandsbycall = {}
    for call in usercalls:
        if db.session.query(QSO.band, func.count(QSO.id)).filter(QSO.station_callsign==call[0]).group_by(QSO.band).count() >0:
            bandsbycall[call[0]] = db.session.query(QSO.band, func.count(QSO.id)).filter(QSO.station_callsign==call[0]).group_by(QSO.band).all()
    modesbycall = {}
    for call in usercalls:
        if db.session.query(QSO.mode, func.count(QSO.id)).filter(QSO.station_callsign==call[0]).group_by(QSO.mode).count() >0:
            modesbycall[call[0]] = db.session.query(QSO.mode, func.count(QSO.id)).filter(QSO.station_callsign==call[0]).group_by(QSO.mode).all()
    pmodesbycall = {}
    for call in usercalls:
        if db.session.query(QSO.prop_mode, func.count(QSO.id)).filter(QSO.station_callsign==call[0]).group_by(QSO.prop_mode).count() >0:
            pmodesbycall[call[0]] = db.session.query(QSO.prop_mode, func.count(QSO.id)).filter(QSO.station_callsign==call[0]).group_by(QSO.prop_mode).all()
    return render_template('mybandschart.html', bandlabels=bandlabels, bandvalues=bandvalues, modelabels=modelabels, modevalues=modevalues, propmodelabels=propmodelabels,
                           propmodevalues=propmodevalues, user=user, bandsbycall=bandsbycall, modesbycall=modesbycall, pmodesbycall=pmodesbycall)


@dashboard.route("/mybandstable/<user>")
def mybandstable(user):
    usercalls = Callsign.query.with_entities(Callsign.name).join(User, Callsign.user_id==User.id).filter(User.name==user).all()
    bands = db.session.query(QSO.band, func.count(QSO.id)).filter(QSO.station_callsign.in_([lis[0] for lis in usercalls])).group_by(QSO.band).all()
    modes = db.session.query(QSO.mode, func.count(QSO.id)).filter(QSO.station_callsign.in_([lis[0] for lis in usercalls])).group_by(QSO.mode).all()
    pmodes = db.session.query(QSO.prop_mode, func.count(QSO.id)).filter(QSO.station_callsign.in_([lis[0] for lis in usercalls])).group_by(QSO.prop_mode).all()
    bandsbycall = {}
    for call in usercalls:
        if db.session.query(QSO.band, func.count(QSO.id)).filter(QSO.station_callsign==call[0]).group_by(QSO.band).count() >0:
            bandsbycall[call[0]] = db.session.query(QSO.band, func.count(QSO.id)).filter(QSO.station_callsign==call[0]).group_by(QSO.band).all()
    modesbycall = {}
    for call in usercalls:
        if db.session.query(QSO.mode, func.count(QSO.id)).filter(QSO.station_callsign==call[0]).group_by(QSO.mode).count() >0:
            modesbycall[call[0]] = db.session.query(QSO.mode, func.count(QSO.id)).filter(QSO.station_callsign==call[0]).group_by(QSO.mode).all()  
    pmodesbycall = {}
    for call in usercalls:
        if db.session.query(QSO.prop_mode, func.count(QSO.id)).filter(QSO.station_callsign==call[0]).group_by(QSO.prop_mode).count() >0:
            pmodesbycall[call[0]] = db.session.query(QSO.prop_mode, func.count(QSO.id)).filter(QSO.station_callsign==call[0]).group_by(QSO.prop_mode).all()  
    return render_template('mybandstable.html', bands=bands, modes=modes, pmodes=pmodes, user=user, bandsbycall=bandsbycall,
                           modesbycall=modesbycall, pmodesbycall=pmodesbycall)


@dashboard.route("/dxccchart")
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


@dashboard.route("/dxcctable")
def dxcctable():
    dxccmembers = db.session.query(User.name, func.string_agg(db.distinct(Callsign.name), ', '), db.func.count(db.distinct(QSO.dxcc))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.dxcc)).desc()).all()
    cqzmembers = db.session.query(User.name, func.string_agg(db.distinct(Callsign.name), ', '), db.func.count(db.distinct(QSO.cqz))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.cqz)).desc()).all()
    ituzmembers = db.session.query(User.name, func.string_agg(db.distinct(Callsign.name), ', '), db.func.count(db.distinct(QSO.ituz))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.ituz)).desc()).all()
    return render_template('dxcctable.html', dxccmembers=dxccmembers, cqzmembers=cqzmembers, ituzmembers=ituzmembers)


@dashboard.route("/dxccmap")
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

@dashboard.route("/mygridchart/<user>")
def mygridchart(user):
    usercalls = Callsign.query.with_entities(Callsign.name).join(User, Callsign.user_id==User.id).filter(User.name==user).all()
    squares = db.session.query(func.left(QSO.gridsquare,4), func.count(QSO.id)).filter(QSO.station_callsign.in_([lis[0] for lis in usercalls])).group_by(func.left(QSO.gridsquare,4)).all()
    labels = list(map(list, zip(*squares)))[0]
    gridlabels = ['None' if v is None else v for v in labels]
    gridvalues = list(map(list, zip(*squares)))[1]
    mysquares = db.session.query(func.left(QSO.my_gridsquare,4), func.count(QSO.id)).filter(QSO.station_callsign.in_([lis[0] for lis in usercalls])).group_by(func.left(QSO.my_gridsquare,4)).all()
    labels = list(map(list, zip(*mysquares)))[0]
    mygridlabels = ['None' if v is None else v for v in labels]
    mygridvalues = list(map(list, zip(*mysquares)))[1]
    squaresbycall = {}
    for call in usercalls:
        if db.session.query(func.left(QSO.gridsquare,4), func.count(QSO.id)).filter(QSO.station_callsign==call[0]).group_by(func.left(QSO.gridsquare,4)).count() >0:
            squaresbycall[call[0]] = db.session.query(func.left(QSO.gridsquare,4), func.count(QSO.id)).filter(QSO.station_callsign==call[0]).group_by(func.left(QSO.gridsquare,4)).all()
    mysquaresbycall = {}
    for call in usercalls:
        if db.session.query(func.left(QSO.my_gridsquare,4), func.count(QSO.id)).filter(QSO.station_callsign==call[0]).group_by(func.left(QSO.my_gridsquare,4)).count() >0:
            mysquaresbycall[call[0]] = db.session.query(func.left(QSO.my_gridsquare,4), func.count(QSO.id)).filter(QSO.station_callsign==call[0]).group_by(func.left(QSO.my_gridsquare,4)).all()  
    return render_template('mygridchart.html', gridlabels=gridlabels, gridvalues=gridvalues, mygridlabels=mygridlabels,
                           mygridvalues=mygridvalues, squares=squares, mysquares=mysquares, squaresbycall=squaresbycall,
                           mysquaresbycall=mysquaresbycall, user=user)


@dashboard.route("/mygridtable/<user>")
def mygridtable(user):
    usercalls = Callsign.query.with_entities(Callsign.name).join(User, Callsign.user_id==User.id).filter(User.name==user).all()
    squares = db.session.query(func.left(QSO.gridsquare,4), func.count(QSO.id)).filter(QSO.station_callsign.in_([lis[0] for lis in usercalls])).group_by(func.left(QSO.gridsquare,4)).all()
    labels = list(map(list, zip(*squares)))[0]
    gridlabels = ['None' if v is None else v for v in labels]
    gridvalues = list(map(list, zip(*squares)))[1]
    mysquares = db.session.query(func.left(QSO.my_gridsquare,4), func.count(QSO.id)).filter(QSO.station_callsign.in_([lis[0] for lis in usercalls])).group_by(func.left(QSO.my_gridsquare,4)).all()
    labels = list(map(list, zip(*mysquares)))[0]
    mygridlabels = ['None' if v is None else v for v in labels]
    mygridvalues = list(map(list, zip(*mysquares)))[1]
    squaresbycall = {}
    for call in usercalls:
        if db.session.query(func.left(QSO.gridsquare,4), func.count(QSO.id)).filter(QSO.station_callsign==call[0]).group_by(func.left(QSO.gridsquare,4)).count() >0:
            squaresbycall[call[0]] = db.session.query(func.left(QSO.gridsquare,4), func.count(QSO.id)).filter(QSO.station_callsign==call[0]).group_by(func.left(QSO.gridsquare,4)).all()
    mysquaresbycall = {}
    for call in usercalls:
        if db.session.query(func.left(QSO.my_gridsquare,4), func.count(QSO.id)).filter(QSO.station_callsign==call[0]).group_by(func.left(QSO.my_gridsquare,4)).count() >0:
            mysquaresbycall[call[0]] = db.session.query(func.left(QSO.my_gridsquare,4), func.count(QSO.id)).filter(QSO.station_callsign==call[0]).group_by(func.left(QSO.my_gridsquare,4)).all()  
    return render_template('mygridtable.html', gridlabels=gridlabels, gridvalues=gridvalues, mygridlabels=mygridlabels,
                           mygridvalues=mygridvalues, squares=squares, mysquares=mysquares, squaresbycall=squaresbycall,
                           mysquaresbycall=mysquaresbycall, user=user)


@dashboard.route("/myworkedmap/<user>")
def myworkedmap(user):
    usercalls = Callsign.query.with_entities(Callsign.name).join(User, Callsign.user_id==User.id).filter(User.name==user).all()
    squares = db.session.query(func.left(QSO.gridsquare,4), func.count(QSO.id)).filter(QSO.station_callsign.in_([lis[0] for lis in usercalls])).group_by(func.left(QSO.gridsquare,4)).all()
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
    totalgrids = len(features)
    return render_template('myworkedmap.html', gridsquares=gridsquares, totalgrids=totalgrids, mlayer=mlayer, user=user)


@dashboard.route("/myactivatedmap/<user>")
def myactivatedmap(user):
    usercalls = Callsign.query.with_entities(Callsign.name).join(User, Callsign.user_id==User.id).filter(User.name==user).all()
    squares = db.session.query(func.left(QSO.my_gridsquare,4), func.count(QSO.id)).filter(QSO.station_callsign.in_([lis[0] for lis in usercalls])).group_by(func.left(QSO.my_gridsquare,4)).all()
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
    totalgrids = len(features)
    return render_template('myworkedmap.html', gridsquares=gridsquares, totalgrids=totalgrids, mlayer=mlayer, user=user)

@dashboard.route("/edgetest")
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


@dashboard.route("/scoreboard")
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
            print ("Nope")
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
    pprint(userscores)
    return render_template('scoreboard.html', callsignscores=callsignscores, callscore=callscore, bandscore=bandscore,
                           modescore=modescore, gridscore=gridscore, mygridscore=mygridscore, userscores=userscores)


@dashboard.route("network")
def network():
    nodes = []
    edges = []
    qsos = QSO.query.with_entities(func.count(QSO.id), QSO.call, QSO.station_callsign).group_by(QSO.call, QSO.station_callsign).all()
    for qso in qsos:
        edges.append({'from': qso[1].replace('/', '_'), 'to': qso[2].replace('/', '_'), 'value': min(math.log10(qso[0]),2)+1, 'title': str(qso[1]) + '-' + str(qso[2]) + ' : ' + str(qso[0]) + ', ' + str(min(math.log10(qso[0]),2)+1)})
    stations = db.session.query(Callsign.name, func.count(QSO.id)).join(QSO, or_(Callsign.name==QSO.call, Callsign.name==QSO.station_callsign)).group_by(Callsign.name).all()
    for station in stations:
        nodes.append({'id': str(station[0]).replace('/', '_'), 'value': station[1], 'label': str(station[0])})
    return render_template('network.html', nodes=nodes, edges=edges)