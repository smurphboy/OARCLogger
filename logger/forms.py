import datetime

from flask_wtf import FlaskForm
from wtforms import (BooleanField, DateField, DateTimeField, FileField,
                     IntegerField, RadioField, SelectField,
                     SelectMultipleField, StringField, SubmitField,
                     TextAreaField, TimeField, DecimalField)
from wtforms.validators import InputRequired, Length, Optional
from wtforms.widgets import DateTimeInput


class QSOForm(FlaskForm):
    qso_date = DateField('QSO Date', validators=[InputRequired()], default=datetime.datetime.utcnow().date())
    time_on = TimeField('QSO On Time', validators=[InputRequired()], default=datetime.datetime.utcnow())
    qso_date_off = DateField('QSO Date Off')
    time_off = TimeField('QSO Off Time')
    dxcc = IntegerField('DXCC')
    cqz = IntegerField('CQ Zone')
    ituz = IntegerField('ITU Zone')
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
    lat = StringField('Latitude', validators=[Length(max=11)])
    my_lat = StringField('My Latitude', validators=[Length(max=11)])
    lon = StringField('Longitude', validators=[Length(max=11)])
    my_lon = StringField('My Longitude', validators=[Length(max=11)])
    sota_ref = StringField('SOTA Reference')
    rst_rcvd = StringField('RST Received', validators=[Length(max=10)]) 
    rst_sent = StringField('RST Sent', validators=[Length(max=10)]) 
    srx = IntegerField('Contest Serial Received')
    srx_string = StringField('Contest String Received', validators=[Length(max=50)]) 
    stx = IntegerField('Contest Serial Sent')
    stx_string = StringField('Contest String Sent', validators=[Length(max=50)]) 
    my_sota_ref = StringField('My SOTA Reference')
    pota_ref = StringField('POTA Reference')
    my_pota_ref = StringField('My POTA Reference')
    wwff_ref = StringField('WWFF Reference')
    my_wwff_ref = StringField('My WWFF Reference')
    sig = StringField('Special Interest Group')
    sig_info = StringField('SIG Information')
    my_sig = StringField('My Special Interest Group')
    my_sig_info = StringField('My SIG Information')
    iota = StringField('Islands on the Air', validators=[Length(max=6)])
    my_iota = StringField('My IOTA', validators=[Length(max=6)])
    prop_mode = SelectField('Propagation Mode',
                            choices=[('', '----'), ('AS', 'Aircraft Scatter'), ('AUE', 'Aurora-E'), ('AE', 'Aurora'), ('BS', 'Backscatter'), ('ECH', 'Echolink'), ('EME', 'Earth-Moon-Earth'),
                                     ('ES', 'Sporadic-E'), ('F2', 'F2 Reflection'), ('FAI', 'Field Aligned Irregularities'), ('GWAVE', 'Ground Wave'), ('INTERNET', 'Internet-assisted'),
                                     ('ION', 'Ionoscatter'), ('IRL', 'IRLP'), ('LOS', 'Line of Sight'), ('MS', 'Meteor Scatter'), ('RPT', 'Repeater'), ('RS', 'Rain Scatter'),
                                     ('SAT', 'Satellite'), ('TEP', 'Trans-equatorial'), ('TR', 'Tropospheric Ducting')])
    sat_name = StringField('Sat Name')
    sat_mode = StringField('Sat Mode')
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
    tx_pwr = DecimalField('TX Power', places = 1)
    gridsquare = StringField('Gridsquare', validators=[Length(max=10)])
    my_gridsquare = StringField('My Gridsquare', validators=[Length(max=10)])
    comment = TextAreaField('Comment', validators=[Length(max=255)])

class QSOUploadForm(FlaskForm):
    file = FileField('File')
    submit = SubmitField('Submit')

class EventForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(max=50)])
    type = SelectField('Type',
                        choices=['SOTA', 'POTA', 'SOTA-POTA', 'Non-Amateur', 'Contest', 'Satellite', 'WWFF', 'Portable Day',
                        'Net', 'Other'])
    sota_ref = StringField('SOTA Reference', validators=[Optional(), Length(max=25)])
    pota_ref = StringField('POTA References', validators=[Optional(), Length(max=255)])
    wwff_ref = StringField('WWFF Reference', validators=[Optional(), Length(max=255)])
    iota_ref = StringField('IOTA Reference', validators=[Optional(), Length(max=255)])
    sat_name = StringField('Satellite Name', validators=[Optional(), Length(max=255)])
    sat_mode = StringField('Satellite Mode', validators=[Optional(), Length(max=255)])
    my_gridsquare = StringField('My Gridsquare', validators=[Length(max=10)])
    start_date = DateField('Start Date', validators=[InputRequired()], default=datetime.date.today)
    start_time = TimeField('Start Time', validators=[InputRequired()], default=datetime.datetime.now)
    end_date  = DateField('End Date', validators=[Optional()], default=datetime.date.today)
    end_time = TimeField('End Time', validators=[Optional()], default=datetime.datetime.now)
    comment = TextAreaField('Comment', validators=[Optional(), Length(max=255)])


class ConfigForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(max=50)])
    comment = TextAreaField('Comment', validators=[Optional(), Length(max=255)])
    antenna = SelectField('Antenna', validators=[InputRequired()], coerce=int)
    rig = SelectField('Rig', validators=[InputRequired()], coerce=int)


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


class SOTAQSOForm(FlaskForm):
    qso_date = DateField('QSO Date', validators=[InputRequired()], default=datetime.datetime.utcnow().date())
    time_on = TimeField('QSO On Time', validators=[InputRequired()], default=datetime.datetime.utcnow())
    qso_date_off = DateField('QSO Date Off')
    time_off = TimeField('QSO Off Time')
    call = StringField('Call', validators=[InputRequired(),
                                            Length(max=50)])
    station_callsign = RadioField('Station Callsign')
    operator = StringField('Operator')
    freq = StringField('Freq')
    rst_rcvd = StringField('RST Received')
    rst_sent = StringField('RST Sent')
    sota_ref = StringField('SOTA Reference')
    my_sota_ref = StringField('My SOTA Reference')
    pota_ref = StringField('POTA Reference')
    my_pota_ref = StringField('My POTA Reference')
    tx_pwr = DecimalField('TX Power', places = 1)
    gridsquare = StringField('Gridsquare', validators=[Length(max=10)])
    my_gridsquare = StringField('My Gridsquare', validators=[Length(max=10)])
    dxcc = StringField('DXCC')
    cqz = StringField('CQ Zone')
    ituz = StringField('ITU Zone')
    country = StringField('Country')
    band = SelectField('Band',
                       choices=['', '2190m', '630m', '560m', '160m', '80m', '60m', '40m', '30m', '20m', '17m', '15m',
                                '12m', '10m', '8m', '6m', '5m', '4m', '2m', '1.25m', '70cm', '33cm', '23cm', '13cm',
                                '9cm', '6cm', '3cm', '1.25cm', '6mm', '4mm', '2.5mm', '2mm', '1mm', 'submm']) # convert this to look at the config selected and bands on the rig
    mode = SelectField('Mode',
                       choices=['AM', 'ATV', 'CW', 'DIGITALVOICE', 'FM', 'FT8', 'HELL', 'MFSK', 'OLIVIA', 'PKT', 'PSK', 'RTTY',
                                'RTTYM', 'SSB', 'SSTV', 'ARDOP', 'CHIP', 'CLO', 'CONTESTI', 'DOMINO', 'DYNAMIC', 'FAX', 'FSK441',
                                'ISCAT', 'JT4', 'JT6M', 'JT9', 'JT44', 'JT65', 'MSK144', 'MT63', 'OPERA', 'PAC', 'PAX', 'PSK2K',
                                'Q15', 'QRA64', 'ROS', 'T10', 'THOR', 'THRB', 'TOR', 'V4', 'VOI', 'WINMOR', 'WSPR']) # convert this to look at the config selected and the modes available
    submode = SelectField('Sub Mode')
    comment = StringField('Comment', validators=[Length(max=255)])


class POTAQSOForm(FlaskForm):
    qso_date = DateField('QSO Date', validators=[InputRequired()], default=datetime.datetime.utcnow().date())
    time_on = TimeField('QSO On Time', validators=[InputRequired()], default=datetime.datetime.utcnow())
    qso_date_off = DateField('QSO Date Off')
    time_off = TimeField('QSO Off Time')
    call = StringField('Call', validators=[InputRequired(),
                                            Length(max=50)])
    station_callsign = RadioField('Station Callsign')
    operator = StringField('Operator')
    freq = StringField('Freq')
    rst_rcvd = StringField('RST Received')
    rst_sent = StringField('RST Sent')
    pota_ref = StringField('POTA Reference')
    my_pota_ref = StringField('My POTA Reference')
    tx_pwr = DecimalField('TX Power', places = 1)
    gridsquare = StringField('Gridsquare', validators=[Length(max=10)])
    my_gridsquare = StringField('My Gridsquare', validators=[Length(max=10)])
    band = SelectField('Band',
                       choices=['', '2190m', '630m', '560m', '160m', '80m', '60m', '40m', '30m', '20m', '17m', '15m',
                                '12m', '10m', '8m', '6m', '5m', '4m', '2m', '1.25m', '70cm', '33cm', '23cm', '13cm',
                                '9cm', '6cm', '3cm', '1.25cm', '6mm', '4mm', '2.5mm', '2mm', '1mm', 'submm']) # convert this to look at the config selected and bands on the rig
    mode = SelectField('Mode',
                       choices=['AM', 'ATV', 'CW', 'DIGITALVOICE', 'FM', 'FT8', 'HELL', 'MFSK', 'OLIVIA', 'PKT', 'PSK', 'RTTY',
                                'RTTYM', 'SSB', 'SSTV', 'ARDOP', 'CHIP', 'CLO', 'CONTESTI', 'DOMINO', 'DYNAMIC', 'FAX', 'FSK441',
                                'ISCAT', 'JT4', 'JT6M', 'JT9', 'JT44', 'JT65', 'MSK144', 'MT63', 'OPERA', 'PAC', 'PAX', 'PSK2K',
                                'Q15', 'QRA64', 'ROS', 'T10', 'THOR', 'THRB', 'TOR', 'V4', 'VOI', 'WINMOR', 'WSPR']) # convert this to look at the config selected and the modes available
    submode = SelectField('Sub Mode')
    comment = StringField('Comment', validators=[Length(max=255)])


class SOTAPOTAQSOForm(FlaskForm):
    qso_date = DateField('QSO Date', validators=[InputRequired()], default=datetime.datetime.utcnow().date())
    time_on = TimeField('QSO On Time', validators=[InputRequired()], default=datetime.datetime.utcnow())
    qso_date_off = DateField('QSO Date Off')
    time_off = TimeField('QSO Off Time')
    call = StringField('Call', validators=[InputRequired(),
                                            Length(max=50)])
    station_callsign = RadioField('Station Callsign')
    operator = StringField('Operator')
    freq = StringField('Freq')
    rst_rcvd = StringField('RST Received')
    rst_sent = StringField('RST Sent')
    sota_ref = StringField('SOTA Reference')
    my_sota_ref = StringField('My SOTA Reference')
    pota_ref = StringField('POTA Reference')
    my_pota_ref = StringField('My POTA Reference')
    tx_pwr = DecimalField('TX Power', places = 1)
    gridsquare = StringField('Gridsquare', validators=[Length(max=10)])
    my_gridsquare = StringField('My Gridsquare', validators=[Length(max=10)])
    band = SelectField('Band',
                       choices=['', '2190m', '630m', '560m', '160m', '80m', '60m', '40m', '30m', '20m', '17m', '15m',
                                '12m', '10m', '8m', '6m', '5m', '4m', '2m', '1.25m', '70cm', '33cm', '23cm', '13cm',
                                '9cm', '6cm', '3cm', '1.25cm', '6mm', '4mm', '2.5mm', '2mm', '1mm', 'submm']) # convert this to look at the config selected and bands on the rig
    mode = SelectField('Mode',
                       choices=['AM', 'ATV', 'CW', 'DIGITALVOICE', 'FM', 'FT8', 'HELL', 'MFSK', 'OLIVIA', 'PKT', 'PSK', 'RTTY',
                                'RTTYM', 'SSB', 'SSTV', 'ARDOP', 'CHIP', 'CLO', 'CONTESTI', 'DOMINO', 'DYNAMIC', 'FAX', 'FSK441',
                                'ISCAT', 'JT4', 'JT6M', 'JT9', 'JT44', 'JT65', 'MSK144', 'MT63', 'OPERA', 'PAC', 'PAX', 'PSK2K',
                                'Q15', 'QRA64', 'ROS', 'T10', 'THOR', 'THRB', 'TOR', 'V4', 'VOI', 'WINMOR', 'WSPR']) # convert this to look at the config selected and the modes available
    submode = SelectField('Sub Mode')
    comment = StringField('Comment', validators=[Length(max=255)])


class SATQSOForm(FlaskForm):
    qso_date = DateField('QSO Date', validators=[InputRequired()], default=datetime.datetime.utcnow().date())
    time_on = TimeField('QSO On Time', validators=[InputRequired()], default=datetime.datetime.utcnow())
    qso_date_off = DateField('QSO Date Off')
    time_off = TimeField('QSO Off Time')
    call = StringField('Call', validators=[InputRequired(),
                                            Length(max=50)])
    station_callsign = RadioField('Station Callsign')
    operator = StringField('Operator')
    freq = StringField('Freq')
    sat_name = StringField('Satellite Name')
    sat_mode = StringField('Satellite Mode')
    tx_pwr = DecimalField('TX Power', places = 1)
    gridsquare = StringField('Gridsquare', validators=[Length(max=10)])
    my_gridsquare = StringField('My Gridsquare', validators=[Length(max=10)])
    band = SelectField('Band',
                       choices=['', '2190m', '630m', '560m', '160m', '80m', '60m', '40m', '30m', '20m', '17m', '15m',
                                '12m', '10m', '8m', '6m', '5m', '4m', '2m', '1.25m', '70cm', '33cm', '23cm', '13cm',
                                '9cm', '6cm', '3cm', '1.25cm', '6mm', '4mm', '2.5mm', '2mm', '1mm', 'submm']) # convert this to look at the config selected and bands on the rig
    mode = SelectField('Mode',
                       choices=['AM', 'ATV', 'CW', 'DIGITALVOICE', 'FM', 'FT8', 'HELL', 'MFSK', 'OLIVIA', 'PKT', 'PSK', 'RTTY',
                                'RTTYM', 'SSB', 'SSTV', 'ARDOP', 'CHIP', 'CLO', 'CONTESTI', 'DOMINO', 'DYNAMIC', 'FAX', 'FSK441',
                                'ISCAT', 'JT4', 'JT6M', 'JT9', 'JT44', 'JT65', 'MSK144', 'MT63', 'OPERA', 'PAC', 'PAX', 'PSK2K',
                                'Q15', 'QRA64', 'ROS', 'T10', 'THOR', 'THRB', 'TOR', 'V4', 'VOI', 'WINMOR', 'WSPR']) # convert this to look at the config selected and the modes available
    submode = SelectField('Sub Mode')
    comment = StringField('Comment', validators=[Length(max=255)])


class NonAmQSOForm(FlaskForm):
    qso_date = DateField('QSO Date', validators=[InputRequired()], default=datetime.datetime.utcnow().date())
    time_on = TimeField('QSO On Time', validators=[InputRequired()], default=datetime.datetime.utcnow())
    qso_date_off = DateField('QSO Date Off')
    time_off = TimeField('QSO Off Time')
    call = StringField('Call', validators=[InputRequired(),
                                            Length(max=50)])
    station_callsign = RadioField('Station Callsign')
    operator = StringField('Operator')
    freq = StringField('Freq')
    rst_rcvd = StringField('RST Received')
    rst_sent = StringField('RST Sent')
    sota_ref = StringField('SOTA Reference')
    my_sota_ref = StringField('My SOTA Reference')
    pota_ref = StringField('POTA Reference')
    my_pota_ref = StringField('My POTA Reference')
    tx_pwr = DecimalField('TX Power', places = 1)
    gridsquare = StringField('Gridsquare', validators=[Length(max=10)])
    my_gridsquare = StringField('My Gridsquare', validators=[Length(max=10)])
    band = SelectField('Band',
                       choices=['', '2190m', '630m', '560m', '160m', '80m', '60m', '40m', '30m', '20m', '17m', '15m',
                                '12m', '10m', '8m', '6m', '5m', '4m', '2m', '1.25m', '70cm', '33cm', '23cm', '13cm',
                                '9cm', '6cm', '3cm', '1.25cm', '6mm', '4mm', '2.5mm', '2mm', '1mm', 'submm', 'Discord', 'Internet', 'Post', 'Other']) # convert this to look at the config selected and bands on the rig
    mode = SelectField('Mode',
                       choices=['AM', 'ATV', 'CW', 'DIGITALVOICE', 'FM', 'FT8', 'HELL', 'MFSK', 'OLIVIA', 'PKT', 'PSK', 'RTTY',
                                'RTTYM', 'SSB', 'SSTV', 'ARDOP', 'CHIP', 'CLO', 'CONTESTI', 'DOMINO', 'DYNAMIC', 'FAX', 'FSK441',
                                'ISCAT', 'JT4', 'JT6M', 'JT9', 'JT44', 'JT65', 'MSK144', 'MT63', 'OPERA', 'PAC', 'PAX', 'PSK2K',
                                'Q15', 'QRA64', 'ROS', 'T10', 'THOR', 'THRB', 'TOR', 'V4', 'VOI', 'WINMOR', 'WSPR', 'Other']) # convert this to look at the config selected and the modes available
    submode = SelectField('Sub Mode')
    comment = StringField('Comment', validators=[Length(max=255)])