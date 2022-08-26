from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField,\
                    RadioField, DateField, TimeField, SelectField
from wtforms.validators import InputRequired, Length

class QSOForm(FlaskForm):
    qso_date = DateField('QSO Date', validators=[InputRequired()])
    time_on = TimeField('QSO On Time',
                                validators=[InputRequired()])
    call = StringField('Call', validators=[InputRequired(),
                                            Length(max=50)])
    band = SelectField('Band',
                       choices=['160m', '80m', '60m', '40m', '30m', '20m', '17m',
                                '15m', '12m', '10m', '6m', '4m', '2m', '70cms'],
                       validators=[InputRequired()])
    mode = SelectField('Mode',
                       choices=['USB', 'LSB', 'FM', 'AM', 'DSB', 'FT8'],
                       validators=[InputRequired()])
    gridsquare = StringField('Gridsquare', validators=[InputRequired(),
                                            Length(max=10)])
    my_gridsquare = StringField('My Gridsquare', validators=[InputRequired(),
                                            Length(max=10)])