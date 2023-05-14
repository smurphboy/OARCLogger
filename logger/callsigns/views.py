from flask import (Blueprint, abort, flash, make_response, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required

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
    page = request.args.get('page', 1, type=int)
    callqsos = QSO.query.filter_by(station_callsign = callsign).order_by(QSO.qso_date.desc(), QSO.time_on.desc()).paginate(page=page, per_page=ROWS_PER_PAGE)
    allqsos = QSO.query.filter_by(station_callsign = callsign).all()
    return render_template('callsign.html', qsos=callqsos, station_callsign=callsign, callsignid=callsignid, allqsos=allqsos)


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


@callsigns.post("/delete/<int:id>")
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
    calls = Callsign.query.filter_by(user_id=current_user.get_id()).all()
    callsigns = []
    for vircall in calls:
        callsigns.append(str(vircall))
    virtualcall = QSO.query.filter(QSO.call.in_(callsigns)).all()
    callsign = Callsign.query.filter_by(name=call).first()
    return render_template('virtualcallsign.html', call=call, qsos=virtualcall, callsign=callsign)