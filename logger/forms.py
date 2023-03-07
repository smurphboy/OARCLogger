import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField,\
                    RadioField, DateField, TimeField, SelectField, FileField, SubmitField, DateTimeField
from wtforms.validators import InputRequired, Length, Optional
from wtforms.widgets import DateTimeInput

class QSOForm(FlaskForm):
    qso_date = DateField('QSO Date', validators=[InputRequired()], default=datetime.date.today)
    time_on = TimeField('QSO On Time', validators=[InputRequired()], default=datetime.datetime.now)
    qso_date_off = DateField('QSO Date Off')
    time_off = TimeField('QSO Off Time')
    dxcc = StringField('DXCC', validators=[Length(max=50)])
    cqz = StringField('CQ Zone', validators=[Length(max=50)])
    ituz = StringField('ITU Zone', validators=[Length(max=50)])
    call = StringField('Call', validators=[InputRequired(),
                                            Length(max=50)])
    band = SelectField('Band',
                       choices=['160m', '80m', '60m', '40m', '30m', '20m', '17m',
                                '15m', '12m', '10m', '6m', '4m', '2m', '70cms'],
                       validators=[InputRequired()]) # convert this to look at the config selected and bands on the rig
    mode = SelectField('Mode',
                       choices=['USB', 'LSB', 'FM', 'AM', 'DSB', 'FT8'],
                       validators=[InputRequired()]) # convert this to look at the config selected and the modes available
    gridsquare = StringField('Gridsquare', validators=[InputRequired(),
                                            Length(max=10)])
    my_gridsquare = StringField('My Gridsquare', validators=[InputRequired(),
                                            Length(max=10)])

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