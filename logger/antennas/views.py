from flask import Blueprint, flash, render_template, redirect, request, url_for, abort
from flask_login import login_required, current_user
from logger.models import db, Antenna
from logger.forms import AntennaForm

antennas = Blueprint('antennas', __name__, template_folder='templates')

ROWS_PER_PAGE = 10

@antennas.route("/<username>")
@login_required
def antennalist(username):
    '''Homepage for a users antennas. We should show a table of all the antennas logged against
    this user.'''
    if username == current_user.name:
        page = request.args.get('page', 1, type=int)
        antennapage = Antenna.query.filter_by(user_id=current_user.get_id()).paginate(page=page, per_page=ROWS_PER_PAGE)
        allantennas = Antenna.query.filter_by(user_id=current_user.get_id()).all()
        return render_template('antennalist.html', antennapage=antennapage, allantennas=allantennas, username=username)
    else:
        abort(403)


@antennas.route("/view/<int:id>")
@login_required
def antennaview(id):
    '''View an antenna and the Station configurations / QSOs associated with it'''
    antenna = Antenna.query.filter_by(user_id=id).first()
    if int(antenna.user_id) == int(current_user.get_id()):
        return render_template('anteannaview.html', antenna=antenna)
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
    form.antenna.choices = [(a.id, a.name) for a in Antenna.query.filter_by(user_id=current_user.get_id()).order_by('name')]
    return render_template('antennacreateform.html', form=form, username=current_user.name)