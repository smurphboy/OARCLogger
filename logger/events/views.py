import datetime
from flask import Blueprint, flash, render_template, redirect, request, url_for, abort, make_response
from flask_login import login_required, current_user
from logger.models import User, db, Callsign, QSO, Event, Selected, QSOEvent
from logger.forms import EventForm, SelectedEventForm

events = Blueprint('events', __name__, template_folder='templates')

ROWS_PER_PAGE = 10

EXPORT_FIELDS = ['my_name', 'my_cnty', 'my_city', 'my_postal_code', 'cqz', 'qth', 'my_cq_zone', 'swl', 'gridsquare', 'ituz', 'lat',
                 'my_gridsquare', 'my_itu_zone', 'my_lat', 'rst_rcvd', 'qsl_rcvd', 'lon', 'rst_sent', 'qsl_rcvd_via', 'my_lon', 'tx_pwr',
                 'qsl_sent', 'pfx', 'my_rig', 'qsl_sent_via', 'contest_id', 'my_antenna', 'my_wwff_ref', 'qso_random', 'wwff_ref',
                 'qso_complete', 'lotw_qsl_rcvd', 'my_street', 'sat_mode', 'lotw_qsl_sent', 'sig', 'iota', 'my_sig', 'sat_name', 'sig_info',
                 'srx', 'eqsl_qsl_rcvd', 'my_sig_info', 'srx_string', 'eqsl_qsl_sent', 'vucc_grids', 'stx', 'my_vucc_grids', 'stx_string', 
                 'usaca_counties', 'my_sota_ref', 'qrzcom_qso_upload_status', 'my_usaca_counties', 'band', 'sota_ref', 'state', 'id',
                 'my_iota', 'address', 'my_state', 'band_rx', 'my_iota_island_id', 'a_index', 'rig', 'mode', 'iota_island_id',
                 'k_index', 'submode', 'country', 'sfi', 'freq', 'my_country', 'ant_az', 'freq_rx', 'distance', 'ant_el', 'call',
                 'dxcc', 'comment', 'station_callsign', 'my_dxcc', 'cont', 'operator', 'name', 'email', 'owner_callsign', 'cnty']

EXPORT_DATES = ['qso_date', 'qso_date_off', 'qslrdate', 'qslsdate', 'lotw_qslsdate', 'lotw_qslrdate', 'eqsl_qslsdate', 'eqsl_qslrdate',
                'qrzcom_qso_upload_date']

EXPORT_TIMES = ['time_on', 'time_off']

@events.route("/<username>")
@login_required
def eventlist(username):
    '''Homepage for a users events. We should show a table of all the events logged against
    this user.'''
    if username == current_user.name:
        page = request.args.get('page', 1, type=int)
        todays_date = datetime.datetime.now()
        future = Event.query.filter(Event.user_id==current_user.get_id(), 
                                    Event.start_date >= todays_date).order_by(Event.start_date.desc()).limit(10).all()
        current = Event.query.filter(Event.user_id==current_user.get_id(), 
                                     Event.start_date <= todays_date, Event.end_date >= todays_date).order_by(Event.start_date.desc()).limit(5).all()
        past = Event.query.filter(Event.user_id==current_user.get_id(), 
                                  Event.end_date <= todays_date).order_by(Event.start_date.desc()).limit(10).all()
        print (future, current, past)
        eventpage = Event.query.filter_by(user_id=current_user.get_id()).order_by(Event.start_date.desc()).paginate(page=page, per_page=ROWS_PER_PAGE)
        allevents = Event.query.filter_by(user_id=current_user.get_id()).all()
        return render_template('eventlist.html', eventpage=eventpage, allevents=allevents, username=username, future=future, current=current, past=past)
    else:
        abort(403)

@events.route("/view/<int:id>")
@login_required
def eventview(id):
    '''View an event and the QSOs associated with it'''
    event = Event.query.filter_by(id=id).first()
    if int(event.owner.id) == int(current_user.get_id()):
        return render_template('eventview.html', event=event)
    else:
        abort(403)

@events.route("/export/<int:id>")
@login_required
def export(id):
    '''Export and events QSOs associated with it'''
    def adiftext(id):
        event = Event.query.filter_by(id=id).first()
        if int(event.owner.id) == int(current_user.get_id()):
            # we want to export an ADIF header with information about our export and then an ADI row for each record
            header = {'ADIF_VER' : '3.1.2', 'CREATED_TIMESTAMP' : datetime.datetime.now().strftime("%Y%m%d %H%M%S"),
                    'PROGRAMID' : 'OARC Logger', 'PROGRAMVERSION' : '0.1 Alpha'}
            ADIF = "OARC Logger ADIF Export\n"
            for key, value in header.items():
                ADIF += "".join("<%s:%s>%s\n" % (key, len(value), value))
            ADIF += "".join("<EOH>\n\n")
            eventqsos = QSOEvent.query.filter_by(event=id).all()
            qsos = []
            qsoids = []
            allqsos = QSO.query.all()
            for qsoid in eventqsos:
                qsoids.append(qsoid.qso)
            for qso in allqsos:
                if qso.id in qsoids:
                    qsos.append(qso)
            for qso in qsos:
                for col in QSO.__table__.columns:
                    if str(col).split('.')[1] in EXPORT_DATES: 
                        if getattr(qso,str(col).split('.')[1]):
                            dateused = getattr(qso,str(col).split('.')[1])
                            ADIF += "".join("<{0}:8>{1:%Y%m%d}\n".format(str(col).split('.')[1], dateused))
                            continue
                    if str(col).split('.')[1] in EXPORT_TIMES:
                        if getattr(qso,str(col).split('.')[1]):
                            timeused = getattr(qso,str(col).split('.')[1])
                            ADIF += "".join("<{0}:6>{1:%H%M%S}\n".format(str(col).split('.')[1], timeused))
                            continue
                    if str(col).split('.')[1] == "id":
                        continue
                    else:
                        if getattr(qso,str(col).split('.')[1]):
                            ADIF += "".join("<%s:%s>%s \n" % (str(col).split('.')[1], len(str(getattr(qso,str(col).split('.')[1]))), str(getattr(qso,str(col).split('.')[1]))))
                ADIF += "".join("<EOR>\n\n")
        else:
            abort(403)

        return ADIF
    response = make_response(adiftext(id), 200)
    response.mimetype = "text/plain"
    exportevent = Event.query.filter_by(id=id).first()
    cdtext = 'attachment; filename=' + exportevent.name + '.adi'
    response.headers = {'Content-disposition': cdtext}
    return response


def save_changes(event, form, new):
        start_date = datetime.datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        start_time = datetime.datetime.strptime(request.form['start_time'], '%H:%M').time()
        event.start_date = datetime.datetime.combine(start_date, start_time)
        print(event.start_date)
        end_date = datetime.datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        end_time = datetime.datetime.strptime(request.form['end_time'], '%H:%M').time()
        event.end_date = datetime.datetime.combine(end_date, end_time)
        event.name = request.form['name']
        event.type = request.form['type']
        event.comment = request.form['comment']
        event.user_id=current_user.get_id()
        if new:
            db.session.add(event)
        db.session.commit()


@events.route("/create", methods=['GET','POST'])
@login_required
def eventcreate():
    '''Create an Event'''
    form = EventForm()
    if request.method == 'POST':
        event = Event()
        save_changes(event, form, new=True)
        flash('Event created successfully!')
        return redirect(url_for('events.eventlist', username=current_user.name))
    return render_template('eventcreateform.html', form=form, username=current_user.name)


@events.route("/delete/<int:id>")
@login_required
def eventdelete(id):
    event = Event.query.filter_by(id=id).first()
    if int(event.user_id) == int(current_user.get_id()):
        event1 = event.query.get_or_404(id)
        db.session.delete(event1)
        db.session.commit()
        return redirect(url_for('events.eventlist', username=current_user.name))
    else:
        abort(403)


@events.route("/edit/<int:id>", methods=['GET', 'POST'])
@login_required
def eventedit(id):
    event = Event.query.filter_by(id=id).first()
    if int(event.user_id) == int(current_user.get_id()):
        event1 = event.query.get_or_404(id)
        if event1:
            form = EventForm(formdata=request.form, obj=event1)
            if request.method == 'POST' and form.validate():
                save_changes(event1, form, new=False)
                flash('Event updated successfully!')
                return redirect(url_for('events.eventlist', username=current_user.name))
            return render_template('eventcreateform.html', form=form, username=current_user.name)
        else:
            return 'Error loading event #{id}'.format(id=id)


@events.errorhandler(403)
def page_not_found(e):
    # note that we set the 403 status explicitly
    return render_template('403.html'), 403


@events.route("/select/<username>", methods=['GET', 'POST'])
@login_required
def selectevents(username):
    form = SelectedEventForm()
    if request.method == 'POST' and form.validate():
        for ev in Selected.query.filter_by(user = current_user.id).all():
            db.session.delete(ev)
        for event in request.form.getlist('Search'): #we need to make sure we get an id from Search
            print (current_user.id, event)
            sel = Selected()
            sel.user = current_user.id
            sel.event = event
            db.session.add(sel)
        db.session.commit()
        print (request.form.getlist('Search'))
        return redirect(url_for('users.profile', user=current_user.name))
    userid = User.query.filter_by(name = username).first()
    allevents = Event.query.filter_by(user_id=current_user.get_id()).all()
    alleventsjson = []
    for e in allevents:
        alleventsjson.append({'val': e.name, 'id' : e.id})
    page = request.args.get('page', 1, type=int)
    eventpage = Event.query.filter_by(user_id=current_user.get_id()).order_by(Event.start_date.desc()).paginate(page=page, per_page=ROWS_PER_PAGE)
    selectedevents = Selected.query.filter_by(user = userid.id).all()
    seleventsjson = []
    for e in selectedevents:
        seleventsjson.append(Event.query.filter_by(id=e.event).first().id)
    return render_template('selectedeventsform.html', username=current_user.name, eventpage=eventpage, selectedevents=selectedevents,
                           allevents=allevents, alleventsjson=alleventsjson, form=form, seleventsjson=seleventsjson)