"""IOC Module."""

import os as _os
import logging as _log
import signal as _signal
from threading import Event as _Event
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
from as_ti_control import main as _main
from siriuspy import util as _util
from siriuspy.envars import vaca_prefix as PREFIX
from siriuspy.search import HLTimeSearch as _HLTimeSearch

__version__ = _util.get_last_commit_hash()
INTERVAL = 0.1
stop_event = _Event()

_hl_trig = _HLTimeSearch.get_hl_triggers()
TRIG_LISTS = {
    'si-dip-quads': ['SI-Glob:TI-Quads:', 'SI-Glob:TI-Dips:'],
    'si-sexts-skews': ['SI-Glob:TI-Sexts:', 'SI-Glob:TI-Skews:'],
    'si-corrs': ['SI-Glob:TI-Corrs:'],
    'si-dig': [
        'SI-01SA:TI-TuneShkrH:', 'SI-01SA:TI-InjKckr:',
        'SI-13C4:TI-DCCT:', 'SI-14C4:TI-DCCT:',
        'SI-16C4:TI-GBPM:', 'SI-17C4:TI-TunePkupV:',
        'SI-17SA:TI-TunePkupH:', 'SI-18C4:TI-TuneShkrV:',
        'SI-19C4:TI-PingV:', 'SI-19SP:TI-GSL15:',
        'SI-20SB:TI-GSL07:', 'SI-01SA:TI-PingH:'],
    'li-inj': [
        'LI-01:TI-EGunAmpMB:', 'LI-01:TI-EGunAmpSB:',
        'LI-01:TI-Modltr-1:', 'LI-01:TI-Modltr-2:',
        'LI-Glob:TI-LLRF-1:', 'LI-Glob:TI-LLRF-2:',
        'LI-Glob:TI-LLRF-3:', 'LI-Glob:TI-RFAmp-1:',
        'LI-Glob:TI-RFAmp-2:', 'LI-Glob:TI-SHBAmp:'],
    'li-dig': [
        'LI-01:TI-ICT-1:', 'LI-01:TI-ICT-2:',
        'LI-Fam:TI-BPM:', 'LI-Fam:TI-Scrn:'],
    'bo-mags': ['BO-Glob:TI-Mags:'],
    'bo-si-bpms': ['BO-Fam:TI-BPM:', 'SI-Fam:TI-BPM:'],
    }
_tr_list = set(_hl_trig.keys())
for v in TRIG_LISTS.values():
    _tr_list -= set(v)
TRIG_LISTS['others'] = sorted(_tr_list)
TRIG_LISTS['all'] = sorted(_hl_trig.keys())
TRIG_LISTS['none'] = []


def _stop_now(signum, frame):
    _log.info('SIGINT received')
    global stop_event
    stop_event.set()


def _attribute_access_security_group(server, db):
    for k, v in db.items():
        if k.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            v.update({'asg': 'rbpv'})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')


class _Driver(_pcaspy.Driver):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.app.driver = self

    def write(self, reason, value):
        app_ret = self.app.write(reason, value)
        if app_ret:
            self.setParam(reason, value)
            self.updatePVs()
            _log.info('{0:40s}: OK'.format(reason))
        else:
            _log.info('{0:40s}: not OK'.format(reason))
        return app_ret


def run(evg_params=True, triggers='all', force=False, wait=15, debug=False):
    """Start the IOC."""
    trig_list = TRIG_LISTS.get(triggers, [])
    ioc_name = 'AS-TI'
    ioc_name += '-EVG-PARAMS' if evg_params else ''
    ioc_name += ('-' + triggers.upper()) if triggers != 'none' else ''

    _util.configure_log_file(filename=None, debug=debug)

    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # Creates App object
    app = _main.App(evg_params=evg_params, trig_list=trig_list)
    db = app.get_database()
    db[ioc_name + ':Version-Cte'] = {'type': 'string', 'value': __version__}

    # check if IOC is already running
    running = _util.check_pv_online(
        pvname=PREFIX + list(db.keys())[0], use_prefix=False, timeout=0.5)
    if running:
        _log.error('Another ' + ioc_name + ' is already running!')
        return

    _util.print_ioc_banner(
            ioc_name, db, 'High Level Timing IOC.', __version__, PREFIX)

    _log.info('Generating database file.')
    _util.save_ioc_pv_list(ioc_name.lower(), PREFIX, db)
    _log.info('File generated with {0:d} pvs.'.format(len(db)))

    # create a new simple pcaspy server and driver to respond client's requests
    _log.info('Creating Server.')
    server = _pcaspy.SimpleServer()
    _attribute_access_security_group(server, db)
    _log.info('Setting Server Database.')
    server.createPV(PREFIX, db)
    _log.info('Creating Driver.')
    pcas_driver = _Driver(app)

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    server_thread.daemon = True
    _log.info('Starting Server Thread.')
    server_thread.start()

    # Connects to low level PVs
    _log.info('Openning connections with Low Level IOCs.')
    app.connect(get_ll_state=not force)

    if not force:
        tm = max(5, wait)
        _log.info('Waiting ' + str(tm) + ' seconds to start forcing.')
        stop_event.wait(tm)
        _log.info('Start forcing now.')
        if not stop_event.is_set():
            app.start_forcing()

    # main loop
    while not stop_event.is_set():
        pcas_driver.app.process(INTERVAL)

    _log.info('Stoping Server Thread...')
    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()
    _log.info('Server Thread stopped.')
    _log.info('Good Bye.')
