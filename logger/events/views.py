from flask import Blueprint, flash, render_template, redirect, request, url_for, abort
from flask_login import login_required, current_user
from logger.models import User, db, Callsign, QSO, Event

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

@events.route("/view/<id>")
@login_required
def eventview(id):
    '''View an event and the QSOs associated with it'''
    event = Event.query.filter_by(id=id).first()
    if event.owner.id == id:
        return render_template('eventview.html', event=event)
    else:
        about(403)

@events.route("/create")
@login_required
def eventcreate():
    '''Create an Event'''
    return render_template('eventcreate.html')


@events.errorhandler(403)
def page_not_found(e):
    # note that we set the 403 status explicitly
    return render_template('403.html'), 403