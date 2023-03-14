import datetime
import os
import adif_io
from flask import Blueprint, flash, render_template, redirect, request, url_for, abort, current_app, jsonify
from flask_login import login_required, current_user
from logger.models import User, db, Callsign, QSO
from logger.forms import QSOForm, QSOUploadForm
import maidenhead as mh
from pathlib import Path
import requests
from werkzeug.utils import secure_filename


qsos = Blueprint('qsos', __name__, template_folder='templates')

@qsos.route("/<station_callsign>/new", methods=['GET','POST'])
@login_required
def postnewqso(station_callsign):
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
        call = request.form.get('call', None)
        mode = request.form.get('mode', None)
        submode = request.form.get('submode', None)
        band = request.form.get('band', None)
        band_rx = request.form.get('band_rx', None)
        gridsquare = request.form.get('gridsquare', None)
        my_gridsquare = request.form.get('my_gridsquare', None)
        operator = request.form.get('operator', None)
        freq = request.form.get('freq', None)
        freq_rx = request.form.get('freq_rx', None)
        owner_callsign = request.form.get('owner_callsign', None)
        contacted_op = request.form.get('contacted_op', None)
        eq_call = request.form.get('eq_call', None)
        lat = request.form.get('lat', None)
        my_lat = request.form.get('my_lat', None)
        lon = request.form.get('lon', None)
        my_lon = request.form.get('my_lon', None)
        sota_ref = request.form.get('sota_ref', None)
        my_sota_ref = request.form.get('my_sota_ref', None)
        pota_ref = request.form.get('pota_ref', None)
        my_pota_ref = request.form.get('my_pota_ref', None)
        sat_name = request.form.get('sat_name', None)
        sat_mode = request.form.get('sat_mode', None)
        newqso = QSO(qso_date=qso_date, time_on=time_on, qso_date_off=qso_date_off, time_off=time_off, call=call, mode=mode,
                    band=band, band_rx=band_rx, gridsquare=gridsquare, my_gridsquare=my_gridsquare, station_callsign=station_callsign,
                    operator = operator, owner_callsign = owner_callsign, contacted_op = contacted_op, eq_call = eq_call,
                    submode = submode, freq=freq, freq_rx=freq_rx, sat_name=sat_name, sat_mode=sat_mode, lat=lat, lon=lon, my_lat=my_lat,
                    my_lon=my_lon, sota_ref=sota_ref, my_sota_ref=my_sota_ref, pota_ref=pota_ref, my_pota_ref=my_pota_ref)
        db.session.add(newqso)
        db.session.commit()
        return redirect(url_for('callsigns.call',callsign=station_callsign))
    return render_template('qsoform.html', form=form, station_callsign=station_callsign)

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
            print(file_path)
            uploaded_file.save(file_path) #we store the file in static/adi/<user.id>
            #we have a valid adi file saved as the <user id>.adi. Next to load and parse it.
            qsos_raw, adif_header = adif_io.read_from_file(file_path)
            print('QSOs: ', len(qsos_raw))
            for qso in qsos_raw:
                print('qso')
                newqso = QSO()
                newqso.create(update_dictionary=qso)

        return redirect(url_for('users.profile',user=current_user.name))
    return render_template('qsoupload.html')

@qsos.route('/view/<call>/<date>/<time>')
@login_required
def viewqso(call, date, time):
    call = call.replace('_', '/')
    qso = QSO.query.filter_by(call=call, qso_date=date, time_on=time).first()
    for key in qso.__dict__.keys():
        if qso.__dict__[key]:
            print(key, qso.__dict__[key])
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

@qsos.route('/_dxcc')
def lookupdxcc():
            callsign = request.args.get('callsign', 0, type=str)
            dxcc = current_app.cic.get_country_name(callsign)
            ituz = current_app.cic.get_ituz(callsign)
            cqz = current_app.cic.get_cqz(callsign)
            print(dxcc, ituz, cqz)
            return jsonify(dxcc = dxcc, ituz = ituz, cqz = cqz)

@qsos.errorhandler(400)
def page_not_found(e):
    # note that we set the 400 status explicitly
    return render_template('400.html'), 400

