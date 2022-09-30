import datetime
from flask import Blueprint, flash, render_template, redirect, request, url_for, abort
from flask_login import login_required, current_user
from logger.models import User, db, Callsign, QSO, Event, Configuration, Antenna, Rig
from logger.forms import AntennaForm, EventForm, ConfigForm, RigForm

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
    configuration = Configuration.query.filter_by(id=id).first()
    if int(configuration.user_id) == int(current_user.get_id()):
        return render_template('configview.html', configuration=configuration)
    else:
        abort(403)


@configurations.route("/create", methods=['GET','POST'])
@login_required
def configcreate():
    '''Create a Station Configuration'''
    form = ConfigForm()
    form_ant = AntennaForm()
    form_rig = RigForm()
    if request.method == 'POST':
        if request.form['formsubmitted'] == 'antenna':
            print('antenna')
            name = request.form['name']
            newantenna = Antenna(name=name, user_id=current_user.get_id())
            db.session.add(newantenna)
            db.session.commit()
            form.antenna.choices = [(a.id, a.name) for a in Antenna.query.filter_by(user_id=current_user.get_id()).order_by('name')]
            form.rig.choices = [(r.id, r.name) for r in Rig.query.filter_by(user_id=current_user.get_id()).order_by('name')]
            form.name.data='' #stops our form name leaking into the config form
            return render_template('configcreateform.html', form=form, form_ant=form_ant, form_rig=form_rig, username=current_user.name)
        elif request.form['formsubmitted'] == 'rig':
            print('rig')
            name = request.form['name']
            newrig = Rig(name=name, user_id=current_user.get_id())
            db.session.add(newrig)
            db.session.commit()
            form.antenna.choices = [(a.id, a.name) for a in Antenna.query.filter_by(user_id=current_user.get_id()).order_by('name')]
            form.rig.choices = [(r.id, r.name) for r in Rig.query.filter_by(user_id=current_user.get_id()).order_by('name')]
            form.name.data='' #stops our form name leaking into the config form
            return render_template('configcreateform.html', form=form, form_ant=form_ant, form_rig=form_rig, username=current_user.name)
        elif request.form['formsubmitted'] == 'config':
            print('config')
            name = request.form['name']
            comment = request.form['comment']
            antenna = Antenna.query.filter_by(id=request.form['antenna']).first()
            rig = Rig.query.filter_by(id=request.form['rig']).first()
            newconfig = Configuration(name=name, comment=comment, antenna=antenna,
                                    rig=rig, user_id=current_user.get_id())
            db.session.add(newconfig)
            db.session.commit()
            return redirect(url_for('configurations.configlist', username=current_user.name))
    form.antenna.choices = [(a.id, a.name) for a in Antenna.query.filter_by(user_id=current_user.get_id()).order_by('name')]
    form.rig.choices = [(r.id, r.name) for r in Rig.query.filter_by(user_id=current_user.get_id()).order_by('name')]
    return render_template('configcreateform.html', form=form, form_ant=form_ant, form_rig=form_rig, username=current_user.name)


@configurations.route("/delete/<int:id>")
@login_required
def configdelete(id):
    config = Configuration.query.filter_by(id=id).first()
    if int(config.user_id) == int(current_user.get_id()):
        config1 = Configuration.query.get_or_404(id)
        db.session.delete(config1)
        db.session.commit()
        return redirect(url_for('configurations.configlist', username=current_user.name))
    else:
        abort(403)

@configurations.errorhandler(403)
def page_not_found(e):
    # note that we set the 403 status explicitly
    return render_template('403.html'), 403