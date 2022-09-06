import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

DATE_FIELDS = ['qso_date', 'qso_date_off', 'lotw_qslsdate', 'eqsl_qslsdate', 'qrzcom_qso_upload_date', 'lotw_qslrdate', 'eqsl_qslrdate', 'qslrdate', 'qslsdate']
TIME_FIELDS = ['time_on', 'time_off']

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(1000), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    created_on = db.Column(db.DateTime())
    last_login = db.Column(db.DateTime())
    callsigns = db.relationship('Callsign', backref='user', lazy=True)

class Callsign(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(1000), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    primary = db.Column(db.Boolean, default=False)

class QSO(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    band = db.Column(db.String(25))
    band_rx = db.Column(db.String(25))
    mode = db.Column(db.String(25))
    submode = db.Column(db.String(25))
    freq = db.Column(db.String(25))
    freq_rx = db.Column(db.String(25))
    call = db.Column(db.String(50))
    station_callsign = db.Column(db.String(50))
    operator = db.Column(db.String(50))
    owner_callsign = db.Column(db.String(50))
    qso_date = db.Column(db.Date())
    qso_date_off = db.Column(db.Date())
    time_on = db.Column(db.Time())
    time_off = db.Column(db.Time())
    gridsquare = db.Column(db.String(10))
    my_gridsquare = db.Column(db.String(10))
    rst_rcvd = db.Column(db.String(10))
    rst_sent = db.Column(db.String(10))
    tx_pwr = db.Column(db.String(10))
    my_rig = db.Column(db.String(100))
    my_antenna = db.Column(db.String(100))
    qso_random = db.Column(db.String(1))
    qso_complete = db.Column(db.String(3))
    sat_mode = db.Column(db.String(25))
    sat_name = db.Column(db.String(25))
    srx = db.Column(db.Integer)
    srx_string = db.Column(db.String(50))
    stx = db.Column(db.Integer)
    stx_string = db.Column(db.String(50))
    my_sota_ref = db.Column(db.String(25))
    sota_ref = db.Column(db.String(25))
    my_iota = db.Column(db.String(6))
    iota = db.Column(db.String(6))
    my_iota_island_id = db.Column(db.Integer)
    iota_island_id = db.Column(db.Integer)
    country = db.Column(db.String(50))
    my_country = db.Column(db.String(50))
    distance = db.Column(db.String(10))
    dxcc = db.Column(db.Integer)
    my_dxcc = db.Column(db.Integer)
    name = db.Column(db.String(50))
    my_name = db.Column(db.String(50))
    my_city = db.Column(db.String(50))
    cqz = db.Column(db.Integer)
    my_cq_zone = db.Column(db.Integer)
    ituz = db.Column(db.Integer)
    my_itu_zone = db.Column(db.Integer)
    qsl_rcvd = db.Column(db.String(3))
    qsl_rcvd_via = db.Column(db.String(3))
    qsl_sent = db.Column(db.String(3))
    qsl_sent_via = db.Column(db.String(3))
    qslrdate = db.Column(db.Date())
    qslsdate = db.Column(db.Date())
    lotw_qsl_rcvd = db.Column(db.String(3))
    lotw_qsl_sent = db.Column(db.String(3))
    lotw_qslsdate = db.Column(db.Date())
    lotw_qslrdate = db.Column(db.Date())
    eqsl_qsl_rcvd = db.Column(db.String(3))
    eqsl_qsl_sent = db.Column(db.String(3))
    eqsl_qslsdate = db.Column(db.Date())
    eqsl_qslrdate = db.Column(db.Date())
    qrzcom_qso_upload_status = db.Column(db.String(3))
    qrzcom_qso_upload_date = db.Column(db.Date())
    address = db.Column(db.String(50))
    a_index = db.Column(db.Integer)
    k_index = db.Column(db.Integer)
    sfi = db.Column(db.Integer)
    ant_az = db.Column(db.Integer)
    ant_el = db.Column(db.Integer)
    comment = db.Column(db.String(255))
    cont = db.Column(db.String(2))
    email = db.Column(db.String(255))
    cnty = db.Column(db.String(50))
    my_cnty = db.Column(db.String(50))
    my_postal_code = db.Column(db.String(10))
    qth = db.Column(db.String(50))
    swl = db.Column(db.String(2))
    lat = db.Column(db.String(11))
    my_lat = db.Column(db.String(11))
    lon = db.Column(db.String(11))
    my_lon = db.Column(db.String(11))
    pfx = db.Column(db.String(15))
    contest_id = db.Column(db.String(50))
    my_wwff_ref = db.Column(db.String(15))
    wwff_ref = db.Column(db.String(15))
    my_street = db.Column(db.String(50))
    sig = db.Column(db.String(50))
    my_sig = db.Column(db.String(50))
    sig_info = db.Column(db.String(50))
    my_sig_info = db.Column(db.String(50))

    def update(self, update_dictionary: dict):
        for col_name in self.__table__.columns.keys():
            if col_name.upper() in update_dictionary:
                setattr(self, col_name, update_dictionary[col_name.lower()])
        db.session.add(self)
        db.session.commit()
        print('committed')
    
    def create(self, update_dictionary: dict):
        for col_name in update_dictionary:
            if hasattr(self, col_name.lower()):
                if col_name.lower() in DATE_FIELDS:
                    print(col_name, update_dictionary[col_name])
                    setattr(self, col_name.lower(), datetime.datetime.strptime(update_dictionary[col_name], '%Y%m%d').date())
                elif col_name.lower() in TIME_FIELDS:
                    print(col_name, update_dictionary[col_name])
                    setattr(self, col_name.lower(), datetime.datetime.strptime(update_dictionary[col_name], '%H%M%S').time())
                else:
                    setattr(self, col_name.lower(), update_dictionary[col_name])
            else:
                print(col_name.lower(), ': not found')
        db.session.add(self)
        db.session.commit()
        print('created')
