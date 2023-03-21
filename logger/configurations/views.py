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
    form.antenna.choices = [(a.id, a.name) for a in Antenna.query.filter_by(user_id=current_user.get_id()).order_by('name')]
    form.rig.choices = [(r.id, r.name) for r in Rig.query.filter_by(user_id=current_user.get_id()).order_by('name')]
    if request.method == 'POST':
        if request.form['formsubmitted'] == 'antenna':
            print('antenna')
            antname = request.form['name']
            antmanufacturer = request.form['manufacturer']
            antcomment = request.form['comment']
            newantenna = Antenna(name=antname, manufacturer=antmanufacturer, comment=antcomment, user_id=current_user.get_id())
            db.session.add(newantenna)
            db.session.commit()
            return redirect(url_for('configurations.configcreate', username=current_user.name))
        elif request.form['formsubmitted'] == 'rig':
            print('rig')
            rigname = request.form['name']
            rigmanufacturer = request.form['manufacturer']
            rigcomment = request.form['comment']
            newrig = Rig(name=rigname, manufacturer=rigmanufacturer, comment=rigcomment, user_id=current_user.get_id())
            db.session.add(newrig)
            db.session.commit()
            return redirect(url_for('configurations.configcreate', username=current_user.name))
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
    return render_template('configcreateform.html', form=form, form_ant=form_ant, form_rig=form_rig, username=current_user.name)


@configurations.route("/edit/<int:id>", methods=['GET','POST'])
@login_required
def configedit(id):
    config = Configuration.query.filter_by(id=id).first()
    if int(config.user_id) == int(current_user.get_id()):
        config1 = config.query.get_or_404(id)
        if config1:
            form = ConfigForm(formdata=request.form, obj=config1)
            form_ant = AntennaForm()
            form_rig = RigForm()
            form.antenna.choices = [(a.id, a.name) for a in Antenna.query.filter_by(user_id=current_user.get_id()).order_by('name')]
            form.rig.choices = [(r.id, r.name) for r in Rig.query.filter_by(user_id=current_user.get_id()).order_by('name')]
            form.name.default = config.name
            form.comment.default = config.comment
            form.antenna.default = config.antenna_id
            form.rig.default = config.rig_id
            form.process()
            if request.method == 'POST' and form.validate():
                if request.form['formsubmitted'] == 'antenna':
                    print('ant')
                    antname = request.form['name']
                    antmanufacturer = request.form['manufacturer']
                    antcomment = request.form['comment']
                    newantenna = Antenna(name=antname, manufacturer=antmanufacturer, comment=antcomment, user_id=current_user.get_id())
                    db.session.add(newantenna)
                    db.session.commit()
                    return redirect(url_for('configurations.configedit', username=current_user.name, id=id))
                elif request.form['formsubmitted'] == 'rig':
                    print('rig')
                    rigname = request.form['name']
                    rigmanufacturer = request.form['manufacturer']
                    rigcomment = request.form['comment']
                    newrig = Rig(name=rigname, manufacturer=rigmanufacturer, comment=rigcomment, user_id=current_user.get_id())
                    db.session.add(newrig)
                    db.session.commit()
                    return redirect(url_for('configurations.configedit', username=current_user.name, id=id))
                elif request.form['formsubmitted'] == 'config':
                    print('config')
                    config.name = request.form['name']
                    config.comment = request.form['comment']
                    config.antenna = Antenna.query.filter_by(id=request.form['antenna']).first()
                    config.rig = Rig.query.filter_by(id=request.form['rig']).first()
                    db.session.commit()
                    return redirect(url_for('configurations.configlist', username=current_user.name))
                else:
                    return 'Error loading config #{id}'.format(id=id)
            print('wasnt post')
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