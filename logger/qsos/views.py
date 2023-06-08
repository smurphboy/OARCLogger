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

from logger.forms import QSOForm, QSOUploadForm, SOTAQSOForm, SATQSOForm
from logger.models import QSO, Callsign, Event, User, db

qsos = Blueprint('qsos', __name__, template_folder='templates')

@qsos.route("/<station_callsign>/new", methods=['GET','POST'])
@login_required
def postnewqso(station_callsign):
    station_callsign = station_callsign.replace('_', '/')
    form = QSOForm()
    if request.method == 'POST':
        qso_date = datetime.datetime.strptime(request.form['qso_date'], '%Y-%m-%d').date()
        time_on = datetime.datetime.strptime(request.form['time_on'], '%H:%M').time()
        if request.form.get('qso_date_off', '') != '':
            qso_date_off = datetime.datetime.strptime(request.form['qso_date_off'], '%Y-%m-%d').date()
        else:
            qso_date_off = None
        if request.form.get('time_off', '') != '':
            time_off = datetime.datetime.strptime(request.form['time_off'], '%H:%M').time()
        else:
            time_off = None
        call = request.form.get('call', '').upper() or None
        mode = request.form.get('mode', '') or None
        submode = request.form.get('submode', '') or None
        band = request.form.get('band', '') or None
        band_rx = request.form.get('band_rx', '') or None
        gridsquare = request.form.get('gridsquare', '') or None
        if gridsquare:
            gridsquare = gridsquare[:2].upper() + gridsquare[2:4] + gridsquare[4:].lower()
        my_gridsquare = request.form.get('my_gridsquare', '') or None
        if my_gridsquare:
            my_gridsquare = my_gridsquare[:2].upper() + my_gridsquare[2:4] + my_gridsquare[4:].lower()
        operator = request.form.get('operator', '').upper() or None
        freq = request.form.get('freq', '') or None
        freq_rx = request.form.get('freq_rx', '') or None
        owner_callsign = request.form.get('owner_callsign', '').upper() or None
        contacted_op = request.form.get('contacted_op', '').upper() or None
        eq_call = request.form.get('eq_call', '').upper() or None
        lat = request.form.get('lat', '') or None
        my_lat = request.form.get('my_lat', '') or None
        lon = request.form.get('lon', '') or None
        my_lon = request.form.get('my_lon', '') or None
        sota_ref = request.form.get('sota_ref', '').upper() or None
        my_sota_ref = request.form.get('my_sota_ref', '').upper() or None
        pota_ref = request.form.get('pota_ref', '').upper() or None
        my_pota_ref = request.form.get('my_pota_ref', '').upper() or None
        sat_name = request.form.get('sat_name', '') or None
        sat_mode = request.form.get('sat_mode', '') or None
        dxcc = request.form.get('dxcc', '') or None
        my_dxcc = request.form.get('my_dxcc', '') or None
        cqz = request.form.get('cqz', '') or None
        my_cq_zone = request.form.get('my_cq_zone', '') or None
        ituz = request.form.get('ituz', '') or None
        my_itu_zone = request.form.get('my_itu_zone', '') or None
        country = request.form.get('country', '') or None
        my_country = request.form.get('my_country', '') or None
        stat_callsign = request.form.get('station_callsign', '') or station_callsign

        newqso = QSO(qso_date=qso_date, time_on=time_on, qso_date_off=qso_date_off, time_off=time_off, call=call, mode=mode,
                    band=band, band_rx=band_rx, gridsquare=gridsquare, my_gridsquare=my_gridsquare, station_callsign=stat_callsign.replace('_', '/'),
                    operator = operator, owner_callsign = owner_callsign, contacted_op = contacted_op, eq_call = eq_call,
                    submode = submode, freq=freq, freq_rx=freq_rx, sat_name=sat_name, sat_mode=sat_mode, lat=lat, lon=lon, my_lat=my_lat,
                    my_lon=my_lon, sota_ref=sota_ref, my_sota_ref=my_sota_ref, pota_ref=pota_ref, my_pota_ref=my_pota_ref, dxcc=dxcc, my_dxcc=my_dxcc,
                    cqz=cqz, my_cq_zone=my_cq_zone, ituz=ituz, my_itu_zone=my_itu_zone, country=country, my_country=my_country)
        user = User.query.filter_by(id=current_user.get_id()).first()
        selectedevents=[]
        for event in user.selected_events:
            selectedevents.append(event.id)
        newqso.events[:] = Event.query.filter(Event.id.in_(selectedevents))
        db.session.add(newqso)
        db.session.commit()
        return redirect(url_for('callsigns.call',callsign=station_callsign.replace('/', '_')))
    return render_template('qsoform.html', form=form, station_callsign=station_callsign.replace('_', '/'))

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
        sota_ref = request.form.get('sota_ref', '').upper() or None
        my_sota_ref = request.form.get('my_sota_ref', '').upper() or None
        pota_ref = request.form.get('pota_ref', '').upper() or None
        my_pota_ref = request.form.get('my_pota_ref', '').upper() or None
        mode = request.form.get('mode', '') or None
        submode = request.form.get('submode', '') or None
        newqso = QSO(qso_date=qso_date, time_on=time_on, call=call, station_callsign=station_callsign,
                     band=band, freq=freq, sota_ref=sota_ref, my_sota_ref=my_sota_ref, mode=mode,
                     submode=submode, pota_ref=pota_ref, my_pota_ref=my_pota_ref)
        if sota_ref:
            url = ("https://api2.sota.org.uk/api/summits/" + sota_ref)
            sotasummit = requests.request("GET", url)
            if sotasummit.status_code == 200:
                summit = sotasummit.json()
                newqso.lat = summit['latitude']
                newqso.lon = summit['longitude']
                newqso.gridsquare = summit['locator']
                newqso.country = summit['associationName']
                db.session.commit()
        if my_sota_ref:
            url = ("https://api2.sota.org.uk/api/summits/" + my_sota_ref)
            sotasummit = requests.request("GET", url)
            if sotasummit.status_code == 200:
                summit = sotasummit.json()
                newqso.my_lat = summit['latitude']
                newqso.my_lon = summit['longitude']
                newqso.my_gridsquare = summit['locator']
                newqso.my_country = summit['associationName']
                db.session.commit()
        user = User.query.filter_by(id=current_user.get_id()).first()
        selectedevents=[]
        for ev in user.selected_events:
            selectedevents.append(ev.id)
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
        gridsquare = request.form.get('gridsquare', '') or None
        if gridsquare:
            gridsquare = gridsquare[:2].upper() + gridsquare[2:4] + gridsquare[4:].lower()
        my_gridsquare = request.form.get('my_gridsquare', '') or None
        if my_gridsquare:
            my_gridsquare = my_gridsquare[:2].upper() + my_gridsquare[2:4] + my_gridsquare[4:].lower()
        mode = request.form.get('mode', '') or None
        submode = request.form.get('submode', '') or None
        newqso = QSO(qso_date=qso_date, time_on=time_on, call=call, station_callsign=station_callsign,
                     band=band, freq=freq, sat_name=sat_name, sat_mode=sat_mode, mode=mode,
                     submode=submode, gridsquare=gridsquare, my_gridsquare=my_gridsquare)
        user = User.query.filter_by(id=current_user.get_id()).first()
        selectedevents=[]
        for ev in user.selected_events:
            selectedevents.append(ev.id)
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