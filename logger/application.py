import flask_login as login
from flask import Flask, current_app, render_template, redirect
from flask_admin import Admin
from flask_login import LoginManager
from flask_migrate import Migrate
from pyhamtools import Callinfo, LookupLib, utils

from logger.admin import (LoggerAntennaModelView, LoggerBandModelView,
                          LoggerCallsignModelView,
                          LoggerConfigurationModelView, LoggerEventModelView,
                          LoggerModelView, LoggerRigModelView,
                          LoggerUserModelView)
from logger.antennas.views import antennas
from logger.callsigns.views import callsigns
from logger.config import Config
from logger.configurations.views import configurations
from logger.dashboard.views import dashboard
from logger.events.views import events
from logger.models import (QSO, Antenna, Band, Callsign, Configuration, Event,
                           Rig, User, db)
from logger.qsos.views import qsos
from logger.rigs.views import rigs
from logger.users.views import users
from logger.waoarc.views import waoarc

bandorder = {	
'2190m' : 1,
'630m' : 2,
'560m' : 3,
'160m' : 4,
'80m' : 5,
'60m' : 6,
'40m' : 7,
'30m' : 8,
'20m' : 9,
'17m' : 10,
'15m' : 11,
'12m' : 12,
'10m' : 13,
'8m' : 14,
'6m' : 15,
'5m' : 16,
'4m' : 17,
'2m' : 18,
'1.25m' : 19,
'70cm' : 20,
'33cm' : 21,
'23cm' : 22,
'13cm' : 23,
'9cm' : 24,
'6cm' : 25,
'3cm' : 26,
'1.25cm' : 27,
'6mm' : 28,
'4mm' : 29,
'2.5mm' : 30,
'2mm' : 31,
'1mm' : 32,
'submm' : 33
}


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.from_object(Config)
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    db.init_app(app)
    migrate = Migrate(app, db, render_as_batch=True)

    login_manager = LoginManager()
    login_manager.login_view = 'users.login'
    login_manager.init_app(app)

    admin = Admin(app, name='Logger', template_mode='bootstrap3')

    admin._menu = admin._menu[1:]
    admin.add_view(LoggerModelView(QSO, db.session))
    admin.add_view(LoggerCallsignModelView(Callsign, db.session))
    admin.add_view(LoggerEventModelView(Event, db.session))
    admin.add_view(LoggerUserModelView(User, db.session))
    admin.add_view(LoggerBandModelView(Band, db.session))
    admin.add_view(LoggerRigModelView(Rig, db.session))
    admin.add_view(LoggerAntennaModelView(Antenna, db.session))
    admin.add_view(LoggerConfigurationModelView(Configuration, db.session))


    with app.app_context():
        current_app.my_lookuplib = LookupLib(lookuptype='countryfile')
        current_app.cic = Callinfo(current_app.my_lookuplib)
        current_app.bandmode = utils

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    app.register_blueprint(users, url_prefix='/users')
    app.register_blueprint(callsigns, url_prefix='/callsigns')
    app.register_blueprint(qsos, url_prefix='/qsos')
    app.register_blueprint(events, url_prefix='/events')
    app.register_blueprint(configurations, url_prefix='/configs')
    app.register_blueprint(antennas, url_prefix='/antennas')
    app.register_blueprint(rigs, url_prefix='/rigs')
    app.register_blueprint(waoarc, url_prefix='/waoarc')
    app.register_blueprint(dashboard, url_prefix='/dashboard')

    @app.route("/")
    def index():
        return render_template('index.html')

    @app.route("/about")
    def about():
        return render_template('about.html')

    @app.route("/gettingstarted")
    def gettingstarted():
        return render_template('gettingstarted.html')

    @app.template_filter()
    def MhzFormat(value):
        value = float(value)
        return "{:,.6f} MHz".format(value)
        
    @app.context_processor
    def utility_processor():
        def qsocount(logbook):
            '''returns the total number of QSOs in the logbook and date and time of last QSO'''
            return QSO.query.filter_by(station_callsign=logbook).count()
        def latestqso(logbook):
            if QSO.query.filter_by(station_callsign=logbook).count() > 0:
                latest_qso = QSO.query.filter_by(station_callsign=logbook).order_by(QSO.qso_date.desc(), QSO.time_on.desc()).first()
                return (latest_qso.qso_date.strftime("%d %b %Y") + ' at ' + latest_qso.time_on.strftime("%X") + ' with ' + latest_qso.call)
            else: return ('N/A')
        def countrylookup(logbook):
            '''returns the country of the callsign'''
            try:
                ret = current_app.cic.get_country_name(logbook)
            except KeyError:
                ret = "N/A"
            return ret
        def get_adif_id(logbook):
            '''returns the DXCC of the callsign'''
            try:
                ret = current_app.cic.get_adif_id(logbook)
            except KeyError:
                ret = "N/A"
            return ret
        def dxccituz(logbook):
            '''returns the ITU Zone for a callsign'''
            try:
                ret = current_app.cic.get_ituz(logbook)
            except KeyError:
                ret = "N/A"
            return ret

        def dxcccqz(logbook):
            '''returns the CQ Zone for a callsign'''
            try:
                ret = current_app.cic.get_cqz(logbook)
            except KeyError:
                ret = "N/A"
            return ret

        def homecallsign(logbook):
            '''returns home callsign and strips prefix / suffix'''
            try:
                ret = current_app.cic.get_homecall(logbook)
            except KeyError:
                ret = 'N/A'
            return ret
        
        def bandfromfreq(freq):
            '''returns the band and mode from the frequency'''
            try:
                print(freq)
                ret = utils.freq_to_band(freq*1000.0)                  
            except KeyError:
                ret = 'N/A'
            print(ret)
            return ret
        
        def bandsortorder(band):
            if band and (band not in ['Discord', 'Internet', 'Post', 'Other']):
                return bandorder[band]
            else:
                return 0
        
        return dict(qsocount=qsocount, latestqso=latestqso, countrylookup=countrylookup,
                    get_adif_id=get_adif_id, dxccituz=dxccituz, dxcccqz=dxcccqz,
                    homecallsign=homecallsign, bandfromfreq=bandfromfreq, bandsortorder=bandsortorder)

    return app