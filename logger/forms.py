import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField,\
                    RadioField, DateField, TimeField, SelectField, FileField, SubmitField, DateTimeField, SelectMultipleField
from wtforms.validators import InputRequired, Length, Optional
from wtforms.widgets import DateTimeInput

class QSOForm(FlaskForm):
    qso_date = DateField('QSO Date', validators=[InputRequired()], default=datetime.datetime.utcnow().date())
    time_on = TimeField('QSO On Time', validators=[InputRequired()], default=datetime.datetime.utcnow())
    qso_date_off = DateField('QSO Date Off')
    time_off = TimeField('QSO Off Time')
    dxcc = StringField('DXCC')
    cqz = StringField('CQ Zone')
    ituz = StringField('ITU Zone')
    call = StringField('Call', validators=[InputRequired(),
                                            Length(max=50)])
    station_callsign = StringField('Station Callsign')
    operator = StringField('Operator')
    country = StringField('Country')
    owner_callsign = StringField('Owner Callsign')
    contacted_op = StringField('Contacted Operator')
    eq_call = StringField('EQ Callsign')
    freq = StringField('Freq')
    freq_rx = StringField('Freq RX')
    lat = StringField('Latitude')
    my_lat = StringField('My Latitude')
    lon = StringField('Longitude')
    my_lon = StringField('My Longitude')
    sota_ref = StringField('SOTA Reference')
    my_sota_ref = StringField('My SOTA Reference')
    pota_ref = StringField('POTA Reference')
    my_pota_ref = StringField('My POTA Reference')
    sat_name = StringField('Sat Name')
    sat_mode = SelectField('Sat Mode',
                       choices=['', 'H', 'A', 'V', 'U', 'L', 'S', 'S2', 'C', 'X', 'K', 'R']) # convert this to look at the config selected and bands on the rig
    band = SelectField('Band',
                       choices=['', '2190m', '630m', '560m', '160m', '80m', '60m', '40m', '30m', '20m', '17m', '15m',
                                '12m', '10m', '8m', '6m', '5m', '4m', '2m', '1.25m', '70cm', '33cm', '23cm', '13cm',
                                '9cm', '6cm', '3cm', '1.25cm', '6mm', '4mm', '2.5mm', '2mm', '1mm', 'submm']) # convert this to look at the config selected and bands on the rig
    band_rx = SelectField('Band RX',
                       choices=['', '2190m', '630m', '560m', '160m', '80m', '60m', '40m', '30m', '20m', '17m', '15m',
                                '12m', '10m', '8m', '6m', '5m', '4m', '2m', '1.25m', '70cm', '33cm', '23cm', '13cm',
                                '9cm', '6cm', '3cm', '1.25cm', '6mm', '4mm', '2.5mm', '2mm', '1mm', 'submm']) # convert this to look at the config selected and bands on the rig
    mode = SelectField('Mode',
                       choices=['AM', 'ATV', 'CW', 'DIGITALVOICE', 'FM', 'FT8', 'HELL', 'MFSK', 'OLIVIA', 'PKT', 'PSK', 'RTTY',
                                'RTTYM', 'SSB', 'SSTV', 'ARDOP', 'CHIP', 'CLO', 'CONTESTI', 'DOMINO', 'DYNAMIC', 'FAX', 'FSK441',
                                'ISCAT', 'JT4', 'JT6M', 'JT9', 'JT44', 'JT65', 'MSK144', 'MT63', 'OPERA', 'PAC', 'PAX', 'PSK2K',
                                'Q15', 'QRA64', 'ROS', 'T10', 'THOR', 'THRB', 'TOR', 'V4', 'VOI', 'WINMOR', 'WSPR']) # convert this to look at the config selected and the modes available
    submode = SelectField('Sub Mode')
    gridsquare = StringField('Gridsquare', validators=[Length(max=10)])
    my_gridsquare = StringField('My Gridsquare', validators=[Length(max=10)])

class QSOUploadForm(FlaskForm):
    file = FileField('File')
    submit = SubmitField('Submit')

class EventForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(max=50)])
    type = SelectField('Type',
                        choices=['SOTA Activation', 'POTA Activation', 'WWFF Activation', 'Contest', 'Portable Day',
                        'Net', 'Other'])
    start_date = DateField('Start Date', validators=[InputRequired()], default=datetime.date.today)
    start_time = TimeField('Start Time', validators=[InputRequired()], default=datetime.datetime.now)
    end_date  = DateField('End Date', validators=[Optional()], default=datetime.date.today)
    end_time = TimeField('End Time', validators=[Optional()], default=datetime.datetime.now)
    comment = TextAreaField('Comment', validators=[Optional(), Length(max=255)])


class ConfigForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(max=50)])
    comment = TextAreaField('Comment', validators=[Optional(), Length(max=255)])
    antenna = SelectField('Antenna', coerce=int)
    rig = SelectField('Rig', coerce=int)


class RigForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(max=50)])
    manufacturer = StringField('Manufacturer', validators=[Optional(), Length(max=255)])
    comment = StringField('Comment', validators=[Optional(), Length(max=255)])


class AntennaForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(max=50)])
    manufacturer = StringField('Manufacturer', validators=[Optional(), Length(max=255)])
    comment = StringField('Comment', validators=[Optional(), Length(max=255)])

class CallsignForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(max=50)])


class SelectedEventForm(FlaskForm):
    selectedevents = SelectMultipleField('Search', choices=())