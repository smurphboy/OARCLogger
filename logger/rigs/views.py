from flask import Blueprint, flash, render_template, redirect, request, url_for, abort
from flask_login import login_required, current_user
from logger.models import db, Rig
from logger.forms import RigForm

rigs = Blueprint('rigs', __name__, template_folder='templates')

ROWS_PER_PAGE = 10

@rigs.route("/<username>")
@login_required
def riglist(username):
    '''Homepage for a users rigs. We should show a table of all the rigs logged against
    this user.'''
    if username == current_user.name:
        page = request.args.get('page', 1, type=int)
        rigpage = Rig.query.filter_by(user_id=current_user.get_id()).paginate(page=page, per_page=ROWS_PER_PAGE)
        allrigs = Rig.query.filter_by(user_id=current_user.get_id()).all()
        return render_template('riglist.html', rigpage=rigpage, allrigs=allrigs, username=username)
    else:
        abort(403)


@rigs.route("/view/<int:id>")
@login_required
def rigview(id):
    '''View a rig and the Station configurations / Antennas associated with it'''
    rig = Rig.query.filter_by(id=id).first()
    if int(rig.user_id) == int(current_user.get_id()):
        return render_template('rigview.html', rig=rig)
    else:
        abort(403)


@rigs.route("/create", methods=['GET','POST'])
@login_required
def rigcreate():
    '''Create a Rig'''
    form = RigForm()
    if request.method == 'POST':
        name = request.form['name']
        newrig = Rig(name=name, user_id=current_user.get_id())
        db.session.add(newrig)
        db.session.commit()
        return redirect(url_for('rigs.riglist', username=current_user.name))
        form.rig.choices = [(r.id, r.name) for r in Rig.query.filter_by(user_id=current_user.get_id()).order_by('name')]
    return render_template('rigcreateform.html', form=form, username=current_user.name)