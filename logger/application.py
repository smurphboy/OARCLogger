from flask import Flask, render_template, current_app
from flask_login import LoginManager
from logger.users.views import users
from logger.callsigns.views import callsigns
from logger.qsos.views import qsos
from logger.events.views import events
from logger.configurations.views import configurations
from logger.antennas.views import antennas
from logger.rigs.views import rigs
from logger.config import Config
from logger.models import db, QSO
from flask_migrate import Migrate
from pyhamtools import LookupLib, Callinfo


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.from_object(Config)
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    db.init_app(app)
    migrate = Migrate(app, db, render_as_batch=True)

    login_manager = LoginManager()
    login_manager.login_view = 'users.login'
    login_manager.init_app(app)

    from logger.models import User

    with app.app_context():
        current_app.my_lookuplib = LookupLib(lookuptype='countryfile')
        current_app.cic = Callinfo(current_app.my_lookuplib)

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
        return dict(qsocount=qsocount, latestqso=latestqso, countrylookup=countrylookup, get_adif_id=get_adif_id, dxccituz=dxccituz, dxcccqz=dxcccqz, homecallsign=homecallsign)

    return app