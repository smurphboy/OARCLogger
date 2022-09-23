import datetime
from flask import Blueprint, flash, render_template, redirect, request, url_for, abort
from flask_login import login_required, current_user
from logger.models import User, db, Callsign, QSO, Event, Configuration, Antenna, Rig
from logger.forms import EventForm, ConfigForm

configurations = Blueprint('configurations', __name__, template_folder='templates')

ROWS_PER_PAGE = 10

@configurations.route("/<username>")
@login_required
def configlist(username):
    '''Homepage for a users configurations. We should show a table of all the configurations logged against
    this user.'''
    if username == current_user.name:
        page = request.args.get('page', 1, type=int)
        configpage = Configuration.query.filter_by(user_id=current_user.get_id()).paginate(page=page, per_page=ROWS_PER_PAGE)
        allconfigs = Configuration.query.filter_by(user_id=current_user.get_id()).all()
        return render_template('configlist.html', configpage=configpage, allconfigs=allconfigs, username=username)
    else:
        abort(403)


@configurations.route("/view/<int:id>")
@login_required
def configview(id):
    '''View a Station Configuration and the Events / QSOs associated with it'''
    config = Configuration.query.filter_by(user_id=id).first()
    if int(config.user_id) == int(current_user.get_id()):
        return render_template('configview.html', config=config)
    else:
        abort(403)


@configurations.route("/create", methods=['GET','POST'])
@login_required
def configcreate():
    '''Create a Station Configuration'''
    form = ConfigForm()
    if request.method == 'POST':
        name = request.form['name']
        comment = request.form['comment']
        antenna = request.form['antenna']
        rig = request.form['rig']
        newconfig = Configuration(name=name, comment=comment, antenna=antenna,
                                  rig=rig, user_id=current_user.get_id())
        db.session.add(newconfig)
        db.session.commit()
        return redirect(url_for('configs.configlist', username=current_user.name))

    form.antenna.choices = [(a.id, a.name) for a in Antenna.query.filter_by(user_id=current_user.get_id()).order_by('name')]
    form.rig.choices = [(r.id, r.name) for r in Rig.query.filter_by(user_id=current_user.get_id()).order_by('name')]
    return render_template('configcreateform.html', form=form, username=current_user.name)

@configurations.errorhandler(403)
def page_not_found(e):
    # note that we set the 403 status explicitly
    return render_template('403.html'), 403