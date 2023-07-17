from flask import Blueprint, flash, render_template, redirect, request, url_for, abort
from flask_login import login_required, current_user
from logger.models import db, Antenna
from logger.forms import AntennaForm

antennas = Blueprint('antennas', __name__, template_folder='templates')

ROWS_PER_PAGE = 10

@antennas.route("/list/<username>", methods=['GET','POST'])
@login_required
def antennalist(username):
    '''Homepage for a users antennas. We should show a table of all the antennas logged against
    this user.'''
    form = AntennaForm()
    if request.method == 'POST':
        name = request.form['name']
        manufacturer = request.form['manufacturer']
        comment = request.form['comment']
        newantenna = Antenna(name=name, manufacturer=manufacturer, comment=comment, user_id=current_user.get_id())
        db.session.add(newantenna)
        db.session.commit()
        return redirect(url_for('antennas.antennalist', username=current_user.name))   
    if username == current_user.name:
        page = request.args.get('page', 1, type=int)
        antennapage = Antenna.query.filter_by(user_id=current_user.get_id()).paginate(page=page, per_page=ROWS_PER_PAGE)
        allantennas = Antenna.query.filter_by(user_id=current_user.get_id()).all()
        return render_template('antennalist.html', antennapage=antennapage, allantennas=allantennas, username=username, form=form)
    else:
        abort(403)
    


@antennas.route("/view/<int:id>")
@login_required
def antennaview(id):
    '''View an antenna and the Station configurations / QSOs associated with it'''
    antenna = Antenna.query.filter_by(id=id).first()
    if int(antenna.user_id) == int(current_user.get_id()):
        return render_template('antennaview.html', antenna=antenna)
    else:
        abort(403)


@antennas.route("/create", methods=['GET','POST'])
@login_required
def antennacreate():
    '''Create an Antenna'''
    form = AntennaForm()
    if request.method == 'POST':
        name = request.form['name']
        newantenna = Antenna(name=name, user_id=current_user.get_id())
        db.session.add(newantenna)
        db.session.commit()
        return redirect(url_for('antennas.antennalist', username=current_user.name))
    return render_template('antennacreateform.html', form=form, username=current_user.name)


@antennas.route("/delete/<int:id>")
@login_required
def antennadelete(id):
    '''deleted selected antenna'''
    antenna = Antenna.query.filter_by(id=id).first()
    if int(antenna.user_id) == int(current_user.get_id()):
        antenna1 = Antenna.query.get_or_404(id)
        db.session.delete(antenna1)
        db.session.commit()
        return redirect(url_for('antennas.antennalist', username=current_user.name))
    else:
        abort(403)


@antennas.route("/edit/<int:id>", methods=['GET','POST'])
@login_required
def antennaedit(id):
    '''edit an existing antenna'''
    form = AntennaForm()
    antenna = Antenna.query.get_or_404(id)
    form.name.data = antenna.name
    form.manufacturer.data = antenna.manufacturer
    form.comment.data = antenna.comment
    if request.method == 'POST':
        antenna.name = request.form['name']
        antenna.manufacturer = request.form['manufacturer']
        antenna.comment = request.form['comment']
        db.session.add(antenna)
        db.session.commit()
        return redirect(url_for('antennas.antennalist', username=current_user.name))
    return render_template('antennaeditform.html', form=form, username=current_user.name)