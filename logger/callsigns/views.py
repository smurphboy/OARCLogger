from flask import Blueprint, flash, render_template, redirect, request, url_for
from flask_login import login_required, current_user
from logger.models import User, db, Callsign, QSO

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
    page = request.args.get('page', 1, type=int)
    callqsos = QSO.query.filter_by(station_callsign = callsign).order_by(QSO.qso_date.desc(), QSO.time_on.desc()).paginate(page=page, per_page=ROWS_PER_PAGE)
    allqsos = QSO.query.filter_by(station_callsign = callsign).all()
    return render_template('callsign.html', qsos=callqsos, station_callsign=callsign, allqsos=allqsos)