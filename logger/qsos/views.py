import datetime
import os
import adif_io
from flask import Blueprint, flash, render_template, redirect, request, url_for, abort, current_app
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
        call = request.form['call']
        mode = request.form['mode']
        band = request.form['band']
        gridsquare = request.form['gridsquare']
        my_gridsquare = request.form['my_gridsquare']
        station_callsign = station_callsign
        newqso = QSO(qso_date=qso_date, time_on=time_on, call=call, mode=mode,
                    band=band, gridsquare=gridsquare, my_gridsquare=my_gridsquare, station_callsign=station_callsign)
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
    markers = {}
    summit = {}
    if qso.gridsquare:
        markers['gslat'] = mh.to_location(qso.gridsquare, center=True)[0]
        markers['gslong'] = mh.to_location(qso.gridsquare, center=True)[1]
    if qso.my_gridsquare:
        markers['mgslat'] = mh.to_location(qso.my_gridsquare, center=True)[0]
        markers['mgslong'] = mh.to_location(qso.my_gridsquare, center=True)[1]
    if qso.my_sota_ref or qso.sota_ref: #we are on a SOTA summit or chasing, so let's map it
        url = ("https://api2.sota.org.uk/api/summits/" + qso.my_sota_ref)
        sotasummit = requests.request("GET", url)
        if sotasummit.status_code == 200:
            summit = sotasummit.json()
            summit['status'] = True
        else:
            summit['status'] = False

    return render_template('viewqso.html', qso=qso, markers=markers, summit=summit)

@qsos.errorhandler(400)
def page_not_found(e):
    # note that we set the 400 status explicitly
    return render_template('400.html'), 400

