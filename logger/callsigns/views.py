from flask import Blueprint, flash, render_template, redirect, request, url_for
from flask_login import login_required, current_user
from logger.models import User, db, Callsign

callsigns = Blueprint('callsigns', __name__, template_folder='templates')

@callsigns.route("/")
def index():
    '''Callsign index. show who has what callsign'''
    callsignlist = Callsign.query.all()
    return render_template('callsignindex.html', callsigns=callsignlist)