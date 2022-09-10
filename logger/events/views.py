import datetime
from flask import Blueprint, flash, render_template, redirect, request, url_for, abort
from flask_login import login_required, current_user
from logger.models import User, db, Callsign, QSO, Event
from logger.forms import EventForm

events = Blueprint('events', __name__, template_folder='templates')

ROWS_PER_PAGE = 10

@events.route("/<username>")
@login_required
def eventlist(username):
    '''Homepage for a users events. We should show a table of all the events logged against
    this user.'''
    if username == current_user.name:
        page = request.args.get('page', 1, type=int)
        eventpage = Event.query.filter_by(user_id=current_user.get_id()).order_by(Event.start_date.desc()).paginate(page=page, per_page=ROWS_PER_PAGE)
        allevents = Event.query.filter_by(user_id=current_user.get_id()).all()
        return render_template('eventlist.html', eventpage=eventpage, allevents=allevents, username=username)
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
    event = Event.query.filter_by(id=id).first()
    if int(event.owner.id) == int(current_user.get_id()):
        # we want to export an ADIF header with information about our export and then an ADI row for each record
        header = {'ADIF_VER' : '3.1.3', 'CREATED_TIMESTAMP' : datetime.datetime.now().strftime("%Y%m%d %H%M%S"),
                  'PROGRAMID' : 'OARC Logger', 'PROGRAMVERSION' : '0.1 Alpha'}
        for qso in event.qsos:
            for col in QSO.__table__.columns:
                print(col)
        return render_template('eventexport.html', event=event, qsos=event.qsos, eventid=id, header=header)
    else:
        abort(403)

@events.route("/create", methods=['GET','POST'])
@login_required
def eventcreate():
    '''Create an Event'''
    form = EventForm()
    if request.method == 'POST':
        start_date = datetime.datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        start_time = datetime.datetime.strptime(request.form['start_time'], '%H:%M').time()
        start_date = datetime.datetime.combine(start_date, start_time)
        print(start_date)
        end_date = datetime.datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        end_time = datetime.datetime.strptime(request.form['end_time'], '%H:%M').time()
        end_date = datetime.datetime.combine(end_date, end_time)
        name = request.form['name']
        type = request.form['type']
        comment = request.form['comment']
        newevent = Event(start_date=start_date, end_date=end_date, name=name, comment=comment,
                         type=type, user_id=current_user.get_id())
        db.session.add(newevent)
        db.session.commit()
        return redirect(url_for('events.eventlist', username=current_user.name))
    return render_template('eventcreateform.html', form=form, username=current_user.name)

@events.errorhandler(403)
def page_not_found(e):
    # note that we set the 403 status explicitly
    return render_template('403.html'), 403