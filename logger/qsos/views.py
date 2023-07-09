import datetime
import os
from pathlib import Path

import adif_io
import maidenhead as mh
import requests
from flask import (Blueprint, abort, current_app, flash, jsonify, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from logger.forms import QSOForm, QSOUploadForm, SOTAQSOForm, SATQSOForm, NonAmQSOForm
from logger.models import QSO, Callsign, Event, User, db

qsos = Blueprint('qsos', __name__, template_folder='templates')


def save_changes(qso, form, new):
    qso.qso_date = datetime.datetime.strptime(request.form['qso_date'], '%Y-%m-%d').date()
    qso.time_on = datetime.datetime.strptime(request.form['time_on'], '%H:%M').time()
    if request.form.get('qso_date_off', '') != '':
        qso.qso_date_off = datetime.datetime.strptime(request.form['qso_date_off'], '%Y-%m-%d').date()
    else:
        qso.qso_date_off = None
    if request.form.get('time_off', '') != '':
        qso.time_off = datetime.datetime.strptime(request.form['time_off'], '%H:%M').time()
    else:
        qso.time_off = None
    qso.call = request.form.get('call', '').upper() or None
    qso.mode = request.form.get('mode', '') or None
    qso.submode = request.form.get('submode', '') or None
    qso.band = request.form.get('band', '') or None
    qso.band_rx = request.form.get('band_rx', '') or None
    qso.gridsquare = request.form.get('gridsquare', '').lstrip() or None
    if qso.gridsquare:
        qso.gridsquare = qso.gridsquare[:2].upper() + qso.gridsquare[2:4] + qso.gridsquare[4:].lower()
    qso.my_gridsquare = request.form.get('my_gridsquare', '').lstrip() or None
    if qso.my_gridsquare:
        qso.my_gridsquare = qso.my_gridsquare[:2].upper() + qso.my_gridsquare[2:4] + qso.my_gridsquare[4:].lower()
    qso.operator = request.form.get('operator', '').upper() or None
    qso.freq = request.form.get('freq', '') or None
    qso.freq_rx = request.form.get('freq_rx', '') or None
    qso.owner_callsign = request.form.get('owner_callsign', '').upper() or None
    qso.contacted_op = request.form.get('contacted_op', '').upper() or None
    qso.eq_call = request.form.get('eq_call', '').upper() or None
    qso.lat = request.form.get('lat', '')[:11] or None
    qso.my_lat = request.form.get('my_lat', '')[:11] or None
    qso.lon = request.form.get('lon', '')[:11] or None
    qso.my_lon = request.form.get('my_lon', '')[:11] or None
    qso.sota_ref = request.form.get('sota_ref', '').upper() or None
    qso.my_sota_ref = request.form.get('my_sota_ref', '').upper() or None
    qso.pota_ref = request.form.get('pota_ref', '').upper() or None
    qso.my_pota_ref = request.form.get('my_pota_ref', '').upper() or None
    qso.rst_rcvd = request.form.get('rst_rcvd', '') or None
    qso.rst_sent = request.form.get('rst_sent', '') or None
    qso.srx = request.form.get('srx', '') or None
    qso.srx_string = request.form.get('srx_string', '') or None
    qso.stx = request.form.get('stx', '') or None
    qso.stx_string = request.form.get('stx_string', '') or None
    qso.sat_name = request.form.get('sat_name', '') or None
    qso.sat_mode = request.form.get('sat_mode', '') or None
    qso.dxcc = request.form.get('dxcc', '') or None
    qso.my_dxcc = request.form.get('my_dxcc', '') or None
    qso.cqz = request.form.get('cqz', '') or None
    qso.my_cq_zone = request.form.get('my_cq_zone', '') or None
    qso.ituz = request.form.get('ituz', '') or None
    qso.my_itu_zone = request.form.get('my_itu_zone', '') or None
    qso.country = request.form.get('country', '') or None
    qso.my_country = request.form.get('my_country', '') or None
    qso.wwff_ref = request.form.get('wwff_ref', '') or None
    qso.my_wwff_ref = request.form.get('my_wwff_ref', '') or None
    qso.sig = request.form.get('sig', '') or None
    qso.sig_info = request.form.get('sig_info', '') or None
    qso.my_sig = request.form.get('my_sig', '') or None
    qso.my_sig_info = request.form.get('my_sig_info', '') or None
    qso.iota = request.form.get('iota', '') or None
    qso.my_iota = request.form.get('my_iota', '') or None
    qso.comment = request.form.get('comment', '') or None
    qso.prop_mode = request.form.get('prop_mode', '') or None
    qso.station_callsign = request.form.get('station_callsign', '') or qso.station_callsign
    if qso.sota_ref:
        url = ("https://api2.sota.org.uk/api/summits/" + qso.sota_ref)
        sotasummit = requests.request("GET", url)
        if sotasummit.status_code == 200:
            summit = sotasummit.json()
            if not qso.lat:
                qso.lat = str(summit['latitude'])[:11]
            if not qso.lon:
                qso.lon = str(summit['longitude'])[:11]
            if not qso.gridsquare:
                qso.gridsquare = str(summit['locator'])
            if not qso.country:
                qso.country = str(summit['associationName'])
            db.session.commit()
    if qso.my_sota_ref:
        url = ("https://api2.sota.org.uk/api/summits/" + qso.my_sota_ref)
        sotasummit = requests.request("GET", url)
        if sotasummit.status_code == 200:
            summit = sotasummit.json()
            if not qso.my_lat:
                qso.my_lat = str(summit['latitude'])[:11]
            if not qso.my_lon:
                qso.my_lon = str(summit['longitude'])[:11]
            if not qso.my_gridsquare:
                qso.my_gridsquare = str(summit['locator'])
            if not qso.my_country:
                qso.my_country = str(summit['associationName'])
            db.session.commit()
    if qso.station_callsign:
        info = dxcclookup(qso.station_callsign)
        if not qso.my_dxcc:
            qso.my_dxcc = info['dxcc']
        if not qso.my_country:
            qso.my_country = info['country']
        if not qso.my_itu_zone:
            qso.my_itu_zone = info['ituz']
        if not qso.my_cq_zone:
            qso.my_cq_zone = info['cqz']
    if qso.call:
        info = dxcclookup(qso.call)
        if not qso.dxcc:
            qso.dxcc = info['dxcc']
        if not qso.country:
            qso.country = info['country']
        if not qso.ituz:
            qso.ituz = info['ituz']
        if not qso.cqz:
            qso.cqz = info['cqz']
    user = User.query.filter_by(id=current_user.get_id()).first()
    selectedevents=[]
    for event in user.selected_events:
        selectedevents.append(event.id)
    qso.events[:] = Event.query.filter(Event.id.in_(selectedevents))
    if new:
        db.session.add(qso)
    db.session.commit()


def dxcclookup(callsign):
    '''returns the DXCC, Country, CQZ and ITUZ for a callsign'''
    info = {}
    info['country'] = current_app.cic.get_country_name(callsign)
    info['dxcc'] = current_app.cic.get_adif_id(callsign)
    info['ituz'] = current_app.cic.get_ituz(callsign)
    info['cqz'] = current_app.cic.get_cqz(callsign)
    return info


@qsos.route("/<station_callsign>/new", methods=['GET','POST'])
@login_required
def postnewqso(station_callsign):
    station_callsign = station_callsign.replace('_', '/')
    form = QSOForm()
    form.station_callsign.data = station_callsign
    if request.method == 'POST':
        qso = QSO()
        save_changes(qso, form, new=True)
        flash('QSO created successfully!')
        return redirect(url_for('callsigns.call',callsign=station_callsign.replace('/', '_')))
    return render_template('qsoform.html', form=form, station_callsign=station_callsign.replace('_', '/'))


@qsos.route("/edit/<id>", methods=['GET','POST'])
@login_required
def editqso(id):
    qso = QSO.query.get_or_404(id)
    if Callsign.query.filter(Callsign.name==qso.station_callsign, Callsign.user_id==current_user.get_id()).count(): # is the callsign ours?
        form = QSOForm(formdata=request.form, obj=qso)
        if request.method == 'POST':
            save_changes(qso, form, new=False)
            flash('QSO updated successfully!')
            return redirect(url_for('callsigns.call',callsign=qso.station_callsign.replace('/', '_')))
        form.submode.data = qso.submode
        form.submode.choices = ['', qso.submode]
        return render_template('qsoform.html', form=form, station_callsign=qso.station_callsign.replace('_', '/'), submode=qso.submode)
    else:
        return 'Error loading qso #{id}'.format(id=id)


@qsos.route("/<user>/upload", methods=['GET', 'POST'])
@login_required
def uploadqsos(user):
    uploadform = QSOUploadForm()
    if request.method == 'POST':
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = Path(filename).suffix
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
                print('abort')
                abort(400)
            user_file = (current_user.get_id() + '.adi')
            file_path = Path(current_app.root_path)
            file_path = file_path / "static/adi" / user_file
            #print(file_path)
            uploaded_file.save(file_path) #we store the file in static/adi/<user.id>
            #we have a valid adi file saved as the <user id>.adi. Next to load and parse it.
            qsos_raw, adif_header = adif_io.read_from_file(file_path)
            #print('QSOs: ', len(qsos_raw))
            user = User.query.filter_by(id=current_user.get_id()).first()
            selev = user.selected_events
            for qso in qsos_raw:
                #print('qso')
                newqso = QSO()
                newqso.create(update_dictionary=qso)
                for ev in selev:
                    newqso.events.append(ev)
                db.session.commit()

        return redirect(url_for('users.profile',user=current_user.name))
    return render_template('qsoupload.html')

@qsos.route('/view/<id>')
@login_required
def viewqso(id):
    qso = QSO.query.filter_by(id=id).first()
    print(qso.station_callsign)
    if Callsign.query.filter(Callsign.name==qso.station_callsign, Callsign.user_id==current_user.get_id()).count(): # is the callsign ours?
        for key in qso.__dict__.keys():
            if qso.__dict__[key]:
                pass
                # print(key, qso.__dict__[key])
        locations = []
        if qso.gridsquare:
            locations.append([mh.to_location(qso.gridsquare, center=True)[0], mh.to_location(qso.gridsquare, center=True)[1], 'star', 'red', 'Gridsquare: ' + qso.gridsquare])
        if qso.my_gridsquare:
            locations.append([mh.to_location(qso.my_gridsquare, center=True)[0],mh.to_location(qso.my_gridsquare, center=True)[1], 'home', 'green', 'My Gridsquare: ' + qso.my_gridsquare])
        if qso.my_sota_ref:
            url = ("https://api2.sota.org.uk/api/summits/" + qso.my_sota_ref)
            sotasummit = requests.request("GET", url)
            if sotasummit.status_code == 200:
                summit = sotasummit.json()
                locations.append([summit['latitude'], summit['longitude'], 'mountain', 'green', 'My SOTA Reference: ' + summit['summitCode'] + ' - ' + summit['name']])
        if qso.sota_ref:
            url = ("https://api2.sota.org.uk/api/summits/" + qso.sota_ref)
            sotasummit = requests.request("GET", url)
            if sotasummit.status_code == 200:
                summit = sotasummit.json()
                locations.append([summit['latitude'], summit['longitude'], 'mountain', 'red', 'SOTA Reference: ' + summit['summitCode'] + ' - ' + summit['name']])
        return render_template('viewqso.html', qso=qso, locations=locations)
    else:
        abort(403)

@qsos.route('/_dxcc')
def lookupdxcc():
    callsign = request.args.get('callsign', 0, type=str)
    country = current_app.cic.get_country_name(callsign)
    get_adif_id = current_app.cic.get_adif_id(callsign)
    ituz = current_app.cic.get_ituz(callsign)
    cqz = current_app.cic.get_cqz(callsign)
    return jsonify(country = country, get_adif_id=get_adif_id, ituz = ituz, cqz = cqz)

@qsos.route('/_freq')
def lookupband():
    freq = request.args.get('freq', type=float)
    bandmode = current_app.bandmode.freq_to_band(freq*1000.0)
    if bandmode['band'] > 1:
        bandmode['band'] = str(bandmode['band']) + 'm'
    elif (bandmode['band'] < 1) and (bandmode['band'] > 0.01):
        bandmode['band'] = str(int(bandmode['band']*100.0)) + 'cm'
    elif (bandmode['band'] < 0.01) and (bandmode['band'] > 0.0062):
        bandmode['band'] = str(bandmode['band']) + 'mm'
    print(str(bandmode['band']))
    return jsonify(bandmode=str(bandmode['band']))


@qsos.route('/_maidenhead')
def lookuplatlong():
    gridsquare = request.args.get('maidenhead')
    latlong = mh.to_location(gridsquare, center=True)
    latlong = (str(latlong[0])[:11], str(latlong[1])[:11])
    print(str(latlong))
    return jsonify(latlong=latlong)


@qsos.route('delete/<int:id>/<callsign>')
@login_required
def qsodelete(id, callsign):
    '''deleted selected qso'''
    qso = QSO.query.filter_by(id=id).first()
    qso.events[:] = []
    db.session.commit()
    db.session.delete(qso)
    db.session.commit()
    return redirect(request.referrer)


@qsos.errorhandler(400)
def page_not_found(e):
    # note that we set the 400 status explicitly
    return render_template('400.html'), 400


@qsos.route('sota/<int:event>/new', methods=['GET', 'POST'])
@login_required
def sota(event):
    if request.method == 'POST':
        qso_date = datetime.datetime.strptime(request.form['qso_date'], '%Y-%m-%d').date()
        time_on = datetime.datetime.strptime(request.form['time_on'], '%H:%M').time()
        call = request.form.get('call', '').upper() or None
        station_callsign = request.form.get('station_callsign', '').upper() or None
        band = request.form.get('band', '') or None
        freq = request.form.get('freq', '') or None
        rst_rcvd = request.form.get('rst_rcvd', '') or None
        rst_sent = request.form.get('rst_sent', '') or None
        sota_ref = request.form.get('sota_ref', '').upper() or None
        my_sota_ref = request.form.get('my_sota_ref', '').upper() or None
        pota_ref = request.form.get('pota_ref', '').upper() or None
        my_pota_ref = request.form.get('my_pota_ref', '').upper() or None
        mode = request.form.get('mode', '') or None
        submode = request.form.get('submode', '') or None
        newqso = QSO(qso_date=qso_date, time_on=time_on, call=call, station_callsign=station_callsign,
                     band=band, freq=freq, sota_ref=sota_ref, my_sota_ref=my_sota_ref, mode=mode,
                     submode=submode, pota_ref=pota_ref, my_pota_ref=my_pota_ref, rst_sent=rst_sent,
                     rst_rcvd=rst_rcvd)
        if sota_ref:
            url = ("https://api2.sota.org.uk/api/summits/" + sota_ref)
            sotasummit = requests.request("GET", url)
            if sotasummit.status_code == 200:
                summit = sotasummit.json()
                newqso.lat = str(summit['latitude'])[:11]
                newqso.lon = str(summit['longitude'])[:11]
                newqso.gridsquare = summit['locator']
                newqso.country = summit['associationName']
                db.session.commit()
        if my_sota_ref:
            url = ("https://api2.sota.org.uk/api/summits/" + my_sota_ref)
            sotasummit = requests.request("GET", url)
            if sotasummit.status_code == 200:
                summit = sotasummit.json()
                newqso.my_lat = str(summit['latitude'])[:11]
                newqso.my_lon = str(summit['longitude'])[:11]
                newqso.my_gridsquare = summit['locator']
                newqso.my_country = summit['associationName']
                db.session.commit()
        if station_callsign:
            info = dxcclookup(station_callsign)
            newqso.my_dxcc = info['dxcc']
            newqso.my_country = info['country']
            newqso.my_itu_zone = info['ituz']
            newqso.my_cq_zone = info['cqz']
        if call:
            info = dxcclookup(call)
            newqso.dxcc = info['dxcc']
            newqso.country = info['country']
            newqso.ituz = info['ituz']
            newqso.cqz = info['cqz']
        user = User.query.filter_by(id=current_user.get_id()).first()
        selectedevents=[]
        for ev in user.selected_events:
            selectedevents.append(ev.id)
        if event not in selectedevents:
            selectedevents.append(event)
        newqso.events[:] = Event.query.filter(Event.id.in_(selectedevents))
        db.session.add(newqso)
        db.session.commit()
        flash('New QSO added to the event', 'info')
        return redirect(url_for('qsos.sota', event=event))
    sotaevent = Event.query.filter_by(id=event).first()
    print(sotaevent.name)
    form = SOTAQSOForm()
    if (sotaevent.type == "SOTA") or (sotaevent.type == "SOTA-POTA"):
        form.my_sota_ref.data = sotaevent.sota_ref
    if (sotaevent.type == "POTA") or (sotaevent.type == "SOTA-POTA"):
        form.my_pota_ref.data = sotaevent.pota_ref
    user = User.query.filter_by(id=current_user.get_id()).first()
    selev = user.selected_events
    selectedevents = []
    for ev in selev:
        if ev.id != sotaevent.id:
            selectedevents.append(ev)
    callsigns = Callsign.query.filter_by(user_id=current_user.get_id()).all()
    form.station_callsign.data = callsigns[0].name
    form.station_callsign.choices = [callsign.name for callsign in Callsign.query.filter_by(user_id=current_user.get_id()).all()]
    return render_template('sotaqsoform.html', form=form, selectedevents=selectedevents, callsigns=callsigns, event=sotaevent)

@qsos.route('sat/<int:event>/new', methods=['GET', 'POST'])
@login_required
def sat(event):
    if request.method == 'POST':
        qso_date = datetime.datetime.strptime(request.form['qso_date'], '%Y-%m-%d').date()
        time_on = datetime.datetime.strptime(request.form['time_on'], '%H:%M').time()
        call = request.form.get('call', '').upper() or None
        station_callsign = request.form.get('station_callsign', '').upper() or None
        band = request.form.get('band', '') or None
        freq = request.form.get('freq', '') or None
        sat_name = request.form.get('sat_name', '').upper() or None
        sat_mode = request.form.get('sat_mode', '').upper() or None
        gridsquare = request.form.get('gridsquare', '').lstrip() or None
        if gridsquare:
            gridsquare = gridsquare[:2].upper() + gridsquare[2:4] + gridsquare[4:].lower()
        my_gridsquare = request.form.get('my_gridsquare', '').lstrip() or None
        if my_gridsquare:
            my_gridsquare = my_gridsquare[:2].upper() + my_gridsquare[2:4] + my_gridsquare[4:].lower()
        mode = request.form.get('mode', '') or None
        submode = request.form.get('submode', '') or None
        prop_mode = "SAT"
        newqso = QSO(qso_date=qso_date, time_on=time_on, call=call, station_callsign=station_callsign,
                     band=band, freq=freq, sat_name=sat_name, sat_mode=sat_mode, mode=mode,
                     submode=submode, gridsquare=gridsquare, my_gridsquare=my_gridsquare, prop_mode=prop_mode)
        if station_callsign:
            info = dxcclookup(station_callsign)
            newqso.my_dxcc = info['dxcc']
            newqso.my_country = info['country']
            newqso.my_itu_zone = info['ituz']
            newqso.my_cq_zone = info['cqz']
        if call:
            info = dxcclookup(call)
            newqso.dxcc = info['dxcc']
            newqso.country = info['country']
            newqso.ituz = info['ituz']
            newqso.cqz = info['cqz']
        user = User.query.filter_by(id=current_user.get_id()).first()
        selectedevents=[]
        for ev in user.selected_events:
            selectedevents.append(ev.id)
        if event not in selectedevents:
            selectedevents.append(event)
        newqso.events[:] = Event.query.filter(Event.id.in_(selectedevents))
        db.session.add(newqso)
        db.session.commit()
        flash('New QSO added to the event', 'info')
        return redirect(url_for('qsos.sat', event=event))
    satevent = Event.query.filter_by(id=event).first()
    print(satevent.name)
    form = SATQSOForm()
    form.sat_name.data = satevent.sat_name
    form.sat_mode.data = satevent.sat_mode
    user = User.query.filter_by(id=current_user.get_id()).first()
    selev = user.selected_events
    selectedevents = []
    for ev in selev:
        if ev.id != satevent.id:
            selectedevents.append(ev)
    callsigns = Callsign.query.filter_by(user_id=current_user.get_id()).all()
    form.station_callsign.data = callsigns[0].name
    form.station_callsign.choices = [callsign.name for callsign in Callsign.query.filter_by(user_id=current_user.get_id()).all()]
    form.my_gridsquare.data = satevent.my_gridsquare
    print(form.station_callsign.choices)
    return render_template('satqsoform.html', form=form, selectedevents=selectedevents, callsigns=callsigns, event=satevent)


@qsos.route('nonam/<int:event>/new', methods=['GET', 'POST'])
@login_required
def nonam(event):
    if request.method == 'POST':
        qso_date = datetime.datetime.strptime(request.form['qso_date'], '%Y-%m-%d').date()
        time_on = datetime.datetime.strptime(request.form['time_on'], '%H:%M').time()
        call = request.form.get('call', '').upper() or None
        station_callsign = request.form.get('station_callsign', '').upper() or None
        band = request.form.get('band', '') or None
        freq = request.form.get('freq', '') or None
        rst_rcvd = request.form.get('rst_rcvd', '') or None
        rst_sent = request.form.get('rst_sent', '') or None
        sota_ref = request.form.get('sota_ref', '').upper() or None
        my_sota_ref = request.form.get('my_sota_ref', '').upper() or None
        pota_ref = request.form.get('pota_ref', '').upper() or None
        my_pota_ref = request.form.get('my_pota_ref', '').upper() or None
        mode = request.form.get('mode', '') or None
        submode = request.form.get('submode', '') or None
        newqso = QSO(qso_date=qso_date, time_on=time_on, call=call, station_callsign=station_callsign,
                     band=band, freq=freq, sota_ref=sota_ref, my_sota_ref=my_sota_ref, mode=mode,
                     submode=submode, pota_ref=pota_ref, my_pota_ref=my_pota_ref, rst_sent=rst_sent,
                     rst_rcvd=rst_rcvd)
        if sota_ref:
            url = ("https://api2.sota.org.uk/api/summits/" + sota_ref)
            sotasummit = requests.request("GET", url)
            if sotasummit.status_code == 200:
                summit = sotasummit.json()
                newqso.lat = str(summit['latitude'])[:11]
                newqso.lon = str(summit['longitude'])[:11]
                newqso.gridsquare = summit['locator']
                newqso.country = summit['associationName']
                db.session.commit()
        if my_sota_ref:
            url = ("https://api2.sota.org.uk/api/summits/" + my_sota_ref)
            sotasummit = requests.request("GET", url)
            if sotasummit.status_code == 200:
                summit = sotasummit.json()
                newqso.my_lat = str(summit['latitude'])[:11]
                newqso.my_lon = str(summit['longitude'])[:11]
                newqso.my_gridsquare = summit['locator']
                newqso.my_country = summit['associationName']
                db.session.commit()
        if station_callsign:
            info = dxcclookup(station_callsign)
            newqso.my_dxcc = info['dxcc']
            newqso.my_country = info['country']
            newqso.my_itu_zone = info['ituz']
            newqso.my_cq_zone = info['cqz']
        if call:
            info = dxcclookup(call)
            newqso.dxcc = info['dxcc']
            newqso.country = info['country']
            newqso.ituz = info['ituz']
            newqso.cqz = info['cqz']
        user = User.query.filter_by(id=current_user.get_id()).first()
        selectedevents=[]
        for ev in user.selected_events:
            selectedevents.append(ev.id)
        if event not in selectedevents:
            selectedevents.append(event)
        newqso.events[:] = Event.query.filter(Event.id.in_(selectedevents))
        db.session.add(newqso)
        db.session.commit()
        flash('New QSO added to the event', 'info')
        return redirect(url_for('qsos.sota', event=event))
    sotaevent = Event.query.filter_by(id=event).first()
    print(sotaevent.name)
    form = NonAmQSOForm()
    if sotaevent.sota_ref:
        form.my_sota_ref.data = sotaevent.sota_ref
    if sotaevent.pota_ref:
        form.my_pota_ref.data = sotaevent.pota_ref
    user = User.query.filter_by(id=current_user.get_id()).first()
    selev = user.selected_events
    selectedevents = []
    for ev in selev:
        if ev.id != sotaevent.id:
            selectedevents.append(ev)
    callsigns = Callsign.query.filter_by(user_id=current_user.get_id()).all()
    form.station_callsign.data = callsigns[0].name
    form.station_callsign.choices = [callsign.name for callsign in Callsign.query.filter_by(user_id=current_user.get_id()).all()]
    return render_template('nonamqsoform.html', form=form, selectedevents=selectedevents, callsigns=callsigns, event=sotaevent)