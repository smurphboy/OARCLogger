from flask import redirect, url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

admins = ['Simon']

class LoggerModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('users.login'))

    column_hide_backrefs = False
    column_display_pk = True


class LoggerEventModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('users.login'))

    column_hide_backrefs = False
    column_display_pk = True
    form_columns = ('name', 'type', 'start_date', 'end_date', 'comment', 'sota_ref',
                   'pota_ref', 'wwff_ref', 'iota_ref', 'sat_name', 'sat_mode', 'my_gridsquare', 'square', 'configs',
                   'qsos', 'selected_by')
    

class LoggerUserModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('users.login'))

    column_hide_backrefs = False
    column_display_pk = True
    form_columns = ('name', 'email', 'password', 'created_on', 'last_login', 'callsigns',
                    'events', 'rigs', 'configurations', 'antennas', 'selected_events')
    
class LoggerCallsignModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('users.login'))

    column_hide_backrefs = False
    column_display_pk = True
    form_columns = ('name', 'primary')


class LoggerBandModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('users.login'))

    column_hide_backrefs = False
    column_display_pk = True
    form_columns = ('name', 'rigs')


class LoggerRigModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('users.login'))

    column_hide_backrefs = False
    column_display_pk = True
    form_columns = ('name', 'manufacturer', 'comment',
                    'configurations', 'bands')
    

class LoggerAntennaModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('users.login'))

    column_hide_backrefs = False
    column_display_pk = True
    form_columns = ('name', 'manufacturer', 'comment',
                    'configurations')


class LoggerConfigurationModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('users.login'))

    column_hide_backrefs = False
    column_display_pk = True
    form_columns = ('name', 'comment', 'qsos', 'events')