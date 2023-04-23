import datetime

from flask import (Blueprint, abort, flash, make_response, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required

from logger.forms import EventForm, SelectedEventForm
from logger.helpers import adiftext
from logger.models import QSO, Callsign, Event, QSOEvent, Selected, User, db

events = Blueprint('events', __name__, template_folder='templates')

ROWS_PER_PAGE = 10
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
    '''Export all QSOs associated with an event'''
    event = Event.query.filter_by(id=id).first()
    if int(event.owner.id) == int(current_user.get_id()):
        qsos = QSO.query.filter(QSO.events.any(event=id)).all()
        response = make_response(adiftext(qsos), 200)
        response.mimetype = "text/plain"
        exportevent = Event.query.filter_by(id=id).first()
        cdtext = 'attachment; filename=' + exportevent.name + '.adi'
        response.headers = {'Content-disposition': cdtext}
        return response
    else:
        abort(403)


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