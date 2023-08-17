from flask import redirect, url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

admins = ['Simon']

class MyAdminModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('users.login'))


class LoggerModelView(MyAdminModelView):

    column_hide_backrefs = False
    column_display_pk = True
    column_searchable_list = ('call', 'station_callsign', 'band', 'mode', 'gridsquare', 'my_gridsquare', 'sota_ref', 'my_sota_ref')

class LoggerEventModelView(MyAdminModelView):

    column_hide_backrefs = False
    column_display_pk = True
    form_columns = ('name', 'type', 'start_date', 'end_date', 'comment', 'sota_ref',
                   'pota_ref', 'wwff_ref', 'iota_ref', 'sat_name', 'sat_mode', 'my_gridsquare', 'square', 'configs',
                   'qsos', 'selected_by')
    

class LoggerUserModelView(MyAdminModelView):

    column_hide_backrefs = False
    column_display_pk = True
    form_columns = ('name', 'email', 'password', 'admin', 'created_on', 'last_login', 'callsigns',
                    'events', 'rigs', 'configurations', 'antennas', 'selected_events')
    
class LoggerCallsignModelView(MyAdminModelView):

    column_hide_backrefs = False
    column_display_pk = True
    form_columns = ('name', 'primary')


class LoggerBandModelView(MyAdminModelView):

    column_hide_backrefs = False
    column_display_pk = True
    form_columns = ('name', 'rigs')


class LoggerRigModelView(MyAdminModelView):

    column_hide_backrefs = False
    column_display_pk = True
    form_columns = ('name', 'manufacturer', 'comment',
                    'configurations', 'bands')
    

class LoggerAntennaModelView(MyAdminModelView):

    column_hide_backrefs = False
    column_display_pk = True
    form_columns = ('name', 'manufacturer', 'comment',
                    'configurations')


class LoggerConfigurationModelView(MyAdminModelView):

    column_hide_backrefs = False
    column_display_pk = True
    form_columns = ('name', 'comment', 'qsos', 'events')