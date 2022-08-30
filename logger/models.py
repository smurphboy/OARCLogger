from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

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
    mode = db.Column(db.String(25))
    submode = db.Column(db.String(25))
    freq = db.Column(db.String(25))
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

    def update(self, update_dictionary: dict):
        for col_name in self.__table__.columns.keys():
            if col_name in update_dictionary:
                setattr(self, col_name, update_dictionary[col_name])
        
        db.session.add(self)
        db.session.commit()
