import datetime
from flask import (Blueprint, abort, flash, make_response, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required

from sqlalchemy import desc, func, and_

from logger.forms import CallsignForm
from logger.helpers import adiftext
from logger.models import QSO, Callsign, User, db

callsigns = Blueprint('callsigns', __name__, template_folder='templates')

ROWS_PER_PAGE = 10

@callsigns.route("/")
@login_required
def index():
    '''Callsign index. show who has what callsign'''
    callsignlist = Callsign.query.all()
    return render_template('callsignindex.html', callsigns=callsignlist)

@callsigns.route("/<callsign>/qsos")
@login_required
def call(callsign):
    '''Homepage for a callsign. We should show a table of all the QSOs logged against
    this callsign.'''
    #swap _ for /
    callsign = callsign.replace('_', '/')
    callsignid = Callsign.query.filter_by(name=callsign).first().id
    allqsos = QSO.query.filter_by(station_callsign = callsign).order_by(QSO.qso_date.desc(), QSO.time_on.desc()).all()
    return render_template('callsign.html', qsos=allqsos, station_callsign=callsign, callsignid=callsignid)


@callsigns.route("/create", methods=['GET','POST'])
@login_required
def callsigncreate():
    '''Create a Callsign'''
    form = CallsignForm()
    if request.method == 'POST':
        name = request.form.get('name','').upper() or None
        newcallsign = Callsign(name=name, user_id=current_user.get_id())
        db.session.add(newcallsign)
        db.session.commit()
        return redirect(url_for('users.profile', user=current_user.name))
    return render_template('callsigncreateform.html', form=form, username=current_user.name)


@callsigns.route("/delete/<int:id>")
@login_required
def callsigndelete(id):
    callsign = Callsign.query.filter_by(id=id).first()
    if int(callsign.user_id) == int(current_user.get_id()):
        callsign1 = callsign.query.get_or_404(id)
        db.session.delete(callsign1)
        db.session.commit()
        return redirect(url_for('users.profile', user=current_user.name))
    else:
        abort(403)


@callsigns.route("/export/<int:id>")
@login_required
def callsignexport(id):
    '''Export all QSOs associated with a callsign'''
    callsign = Callsign.query.filter_by(id=id).first()
    if int(callsign.user_id) == int(current_user.get_id()):
        qsos = QSO.query.filter_by(station_callsign=callsign.name).all()
        response = make_response(adiftext(qsos), 200)
        response.mimetype = "text/plain"
        cdtext = 'attachment; filename=' + callsign.name + '.adi'
        response.headers = {'Content-disposition': cdtext}
        return response
    else:
        abort(403)

@callsigns.route("/<call>/virtual")
@login_required
def virtual(call):
    '''list all qsos where the callsign appears as the <call> not the station_callsign'''
    call = call.replace('_', '/')
    calls = Callsign.query.filter_by(user_id=current_user.get_id()).all()
    callsigns = []
    for vircall in calls:
        callsigns.append(str(vircall))
    virtualcall = QSO.query.filter_by(call = call).order_by(QSO.qso_date.desc(), QSO.time_on.desc()).all()
    callsign = Callsign.query.filter_by(name=call).first()
    matches = {}
    for vcall in virtualcall:
        matches[vcall.id] = QSO.query.with_entities(QSO.id, QSO.station_callsign, QSO.call, QSO.band, QSO.mode, QSO.qso_date, QSO.time_on).filter(and_(func.date(QSO.qso_date) >= '2023-07-01'),(func.date(QSO.qso_date) <= '2023-08-31'), QSO.call == vcall.station_callsign, QSO.station_callsign == vcall.call, QSO.band == vcall.band, QSO.mode == vcall.mode, QSO.qso_date == vcall.qso_date).all()
    print(matches)
    print(call)
    return render_template('virtualcallsign.html', call=call, qsos=virtualcall, callsign=callsign, matches=matches)


@callsigns.route("/<call>/search")
@login_required
def search(call):
    call = call.replace('_', '/')
    calls = Callsign.query.filter_by(user_id=current_user.get_id()).all()
    callsigns = []
    for mycall in calls:
        callsigns.append(str(mycall))
    qsos = QSO.query.filter(QSO.station_callsign.in_(callsigns), QSO.call == call).all()
    return render_template('callsignsearch.html', call=call, qsos=qsos, callsigns=callsigns)


@callsigns.route("/<callsign>/duplicates")
def dupes(callsign):
    '''find duplicates within a callsign based on call, band, mode, date and time'''
    callsign = callsign.replace('_', '/')
    qsos = QSO.query.filter_by(station_callsign = callsign).all()
    possdupes = []
    for leftqso in qsos:
        for rightqso in qsos:
            score = 0
            flag = False
            for dupe in possdupes:
                if (dupe[1] == leftqso) and (dupe[0] == rightqso):
                    flag = True
                    continue
            if flag == True:
                continue
            if leftqso.id == rightqso.id:
                continue
            if leftqso.call != rightqso.call:
                continue
            if leftqso.band == rightqso.band:
                score += 1
            if leftqso.mode == rightqso.mode:
                score += 1
            if leftqso.submode == rightqso.submode:
                score += 1
            if leftqso.mode == rightqso.submode:
                score += 1
            if leftqso.submode == rightqso.mode:
                score += 1
            leftt = datetime.datetime.combine(leftqso.qso_date, leftqso.time_on)
            rightt = datetime.datetime.combine(rightqso.qso_date, rightqso.time_on)
            deltat = leftt - rightt
            if (deltat >= datetime.timedelta(0) and (deltat <= datetime.timedelta(0.5))): # QSOs are within half of a day of each other
                possdupes.append((leftqso, rightqso, score, deltat))
    if len(possdupes) > 1:
        possdupes =sorted(possdupes, key=lambda x: x[2], reverse=True)
    return render_template('dups.html', possdupes=possdupes, callsign=callsign)
