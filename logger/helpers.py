import datetime

from logger.models import QSO

EXPORT_FIELDS = ['my_name', 'my_cnty', 'my_city', 'my_postal_code', 'cqz', 'qth', 'my_cq_zone', 'swl', 'gridsquare', 'ituz', 'lat',
                 'my_gridsquare', 'my_itu_zone', 'my_lat', 'rst_rcvd', 'qsl_rcvd', 'lon', 'rst_sent', 'qsl_rcvd_via', 'my_lon', 'tx_pwr',
                 'qsl_sent', 'pfx', 'my_rig', 'qsl_sent_via', 'contest_id', 'my_antenna', 'my_wwff_ref', 'qso_random', 'wwff_ref',
                 'qso_complete', 'lotw_qsl_rcvd', 'my_street', 'sat_mode', 'lotw_qsl_sent', 'sig', 'iota', 'my_sig', 'sat_name', 'sig_info',
                 'srx', 'eqsl_qsl_rcvd', 'my_sig_info', 'srx_string', 'eqsl_qsl_sent', 'vucc_grids', 'stx', 'my_vucc_grids', 'stx_string', 
                 'usaca_counties', 'my_sota_ref', 'qrzcom_qso_upload_status', 'my_usaca_counties', 'band', 'sota_ref', 'state', 'id',
                 'my_iota', 'address', 'my_state', 'band_rx', 'my_iota_island_id', 'a_index', 'rig', 'mode', 'iota_island_id',
                 'k_index', 'submode', 'country', 'sfi', 'freq', 'my_country', 'ant_az', 'freq_rx', 'distance', 'ant_el', 'call',
                 'dxcc', 'comment', 'station_callsign', 'my_dxcc', 'cont', 'operator', 'name', 'email', 'owner_callsign', 'cnty']

EXPORT_DATES = ['qso_date', 'qso_date_off', 'qslrdate', 'qslsdate', 'lotw_qslsdate', 'lotw_qslrdate', 'eqsl_qslsdate', 'eqsl_qslrdate',
                'qrzcom_qso_upload_date']

EXPORT_TIMES = ['time_on', 'time_off']

def adiftext(qsos):
    '''returns ADIF text (ready for export) from a collection of QSOs'''
    # we want to export an ADIF header with information about our export and then an ADI row for each record
    header = {'ADIF_VER' : '3.1.2', 'CREATED_TIMESTAMP' : datetime.datetime.now().strftime("%Y%m%d %H%M%S"),
            'PROGRAMID' : 'OARC Logger', 'PROGRAMVERSION' : '0.1 Alpha'}
    ADIF = "OARC Logger ADIF Export\n"
    for key, value in header.items():
        ADIF += "".join("<%s:%s>%s\n" % (key, len(value), value))
    ADIF += "".join("<EOH>\n\n")
    for qso in qsos:
        for col in QSO.__table__.columns:
            if str(col).split('.')[1] in EXPORT_DATES: 
                if getattr(qso,str(col).split('.')[1]):
                    dateused = getattr(qso,str(col).split('.')[1])
                    ADIF += "".join("<{0}:8>{1:%Y%m%d}\n".format(str(col).split('.')[1], dateused))
                    continue
            if str(col).split('.')[1] in EXPORT_TIMES:
                if getattr(qso,str(col).split('.')[1]):
                    timeused = getattr(qso,str(col).split('.')[1])
                    ADIF += "".join("<{0}:6>{1:%H%M%S}\n".format(str(col).split('.')[1], timeused))
                    continue
            if str(col).split('.')[1] == "id":
                continue
            else:
                if getattr(qso,str(col).split('.')[1]):
                    ADIF += "".join("<%s:%s>%s \n" % (str(col).split('.')[1], len(str(getattr(qso,str(col).split('.')[1]))), str(getattr(qso,str(col).split('.')[1]))))
        ADIF += "".join("<EOR>\n\n")
    return ADIF
