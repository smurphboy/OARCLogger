import datetime
import operator
import os

import maidenhead as mh
from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import desc, func, and_
from werkzeug.security import check_password_hash, generate_password_hash

from logger.forms import CallsignForm
from logger.helpers import countrylookup
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
    workedcallsigns = db.session.query(User.name, QSO.call, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.call == Callsign.name).join(User, Callsign.user_id == User.id).group_by(QSO.call, User.name).order_by(func.count(QSO.id).desc()).limit(10).all()
    return render_template('leaderboard.html', facts=facts, unclaimed=unclaimed, qsobyday=qsobyday, workedcallsigns=workedcallsigns)


@waoarc.route("/gettingstarted")
def gettingstarted():
    '''Worked All OARC Season 2 getting started page'''
    return render_template('gettingstarted.html')

@waoarc.route("/users")
def users():
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
    return render_template('users.html', calls=calls, unclaimedcalls=unclaimedcalls, unclaimedtable=unclaimedtable, users=users)


@waoarc.route("/dates")
def dates():
    '''All the date and time related info for the Leaderboard Dates detail page'''
    qsobyday = db.session.query(QSO.qso_date, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(QSO.qso_date).order_by(QSO.qso_date).all()
    labels = list(map(list, zip(*qsobyday)))[0]
    dates = []
    for label in labels:
        dates.append(label.strftime('%Y-%m-%d'))
    values = list(map(list, zip(*qsobyday)))[1]
    usersbyday = db.session.query(QSO.qso_date, User.name, func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(QSO.qso_date, User.name).order_by(QSO.qso_date.desc()).order_by(func.count(QSO.id).desc()).all()
    return render_template('dates.html', qsobyday=qsobyday, labels=dates, values=values, usersbyday=usersbyday)

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


@waoarc.route("/dxcc")
def dxcc():
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
    dxccmembers = db.session.query(User.name, func.string_agg(db.distinct(Callsign.name), ', '), db.func.count(db.distinct(QSO.dxcc))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.dxcc)).desc()).all()
    cqzmembers = db.session.query(User.name, func.string_agg(db.distinct(Callsign.name), ', '), db.func.count(db.distinct(QSO.cqz))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.cqz)).desc()).all()
    ituzmembers = db.session.query(User.name, func.string_agg(db.distinct(Callsign.name), ', '), db.func.count(db.distinct(QSO.ituz))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(QSO.ituz)).desc()).all()
    return render_template('dxcc.html', dxcclabels=dxcclabels, dxccvalues=dxccvalues, cqzlabels=cqzlabels, cqzvalues=cqzvalues, ituzlabels=ituzlabels,
                           ituzvalues=ituzvalues, dxccmembers=dxccmembers, cqzmembers=cqzmembers, ituzmembers=ituzmembers)    


@waoarc.route("/grids")
def grids():
    qsobygrid = db.session.query(func.left(QSO.gridsquare,4), func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(func.left(QSO.gridsquare,4)).order_by(func.count(QSO.id).desc()).all()
    labels = list(map(list, zip(*qsobygrid)))[0]
    gridlabels = ['None' if v is None else v for v in labels]
    gridvalues = list(map(list, zip(*qsobygrid)))[1]
    qsobymygrid = db.session.query(func.left(QSO.my_gridsquare,4), func.count(QSO.id)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(func.left(QSO.my_gridsquare,4)).order_by(func.count(QSO.id).desc()).all()
    labels = list(map(list, zip(*qsobymygrid)))[0]
    mygridlabels = ['None' if v is None else v for v in labels]
    mygridvalues = list(map(list, zip(*qsobymygrid)))[1]
    gridmembers = db.session.query(User.name, func.string_agg(db.distinct(Callsign.name), ', '), db.func.count(db.distinct(func.left(QSO.gridsquare,4)))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(func.left(QSO.gridsquare,4))).desc()).all()
    mygridmembers = db.session.query(User.name, func.string_agg(db.distinct(Callsign.name), ', '), db.func.count(db.distinct(func.left(QSO.my_gridsquare,4)))).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).join(Callsign, QSO.station_callsign == Callsign.name).join(User, Callsign.user_id == User.id).group_by(User.name).order_by(db.func.count(db.distinct(func.left(QSO.my_gridsquare,4))).desc()).all()
    return render_template('grids.html', gridlabels=gridlabels, gridvalues=gridvalues, mygridlabels=mygridlabels,
                           mygridvalues=mygridvalues, gridmembers=gridmembers, mygridmembers=mygridmembers)


@waoarc.route("/map")
def simplemap():
    squares = QSO.query.with_entities(func.left(QSO.gridsquare,4)).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31')).group_by(db.distinct(func.left(QSO.gridsquare,4))).all()
    bounds = []
    lats = []
    lons = []
    for square in squares:
        if square[0] is not None:
            lat = (mh.to_location(square[0], center=True)[0])
            lon = (mh.to_location(square[0], center=True)[1])
            lats.append(lat)
            lons.append(lon)
            bounds.append([[lat - 0.5, lon -1.0 ],[lat + 0.5, lon + 1.0]])
    extent = [[min(lats),min(lons)],[max(lats),max(lons)]]
    return render_template('map.html', bounds=bounds, extent=extent)