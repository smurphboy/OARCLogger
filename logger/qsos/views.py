import datetime
import os
from flask import Blueprint, flash, render_template, redirect, request, url_for, abort, current_app
from flask_login import login_required, current_user
from logger.models import User, db, Callsign, QSO
from logger.forms import QSOForm, QSOUploadForm
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
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
                print('abort')
                abort(400)
            uploaded_file.save(os.path.join(current_app.root_path, 'static/adi/', current_user.get_id(),'.adi')) #we store the file in static/adi/<user.id>
        return redirect(url_for('callsigns.call',callsign=user.callsigns.filter_by(primary='Y').one().name))
    return render_template('qsoupload.html')

@qsos.route('/view/<call>/<date>/<time>')
@login_required
def viewqso(call, date, time):
    call = call.replace('_', '/')
    qso = QSO.query.filter_by(call=call, qso_date=date, time_on=time).first()
    return render_template('viewqso.html', qso=qso)

@qsos.errorhandler(400)
def page_not_found(e):
    # note that we set the 400 status explicitly
    return render_template('400.html'), 400

