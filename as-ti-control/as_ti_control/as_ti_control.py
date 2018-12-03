"""IOC Module."""

import os as _os
import logging as _log
import signal as _signal
from threading import Event as _Event
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
from as_ti_control import main as _main
from siriuspy import util as _util
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy.search import HLTimeSearch as _HLTimeSearch

__version__ = _util.get_last_commit_hash()
INTERVAL = 0.1
stop_event = _Event()

_hl_trig = _HLTimeSearch.get_hl_triggers()
TRIG_TYPES = {'as', 'si', 'bo', 'tb', 'ts', 'li', 'all', 'none'}


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


def _get_ioc_name_and_triggers(evg_params, triggers):
    ioc_name = 'as-ti'
    ioc_name += '-evg' if evg_params else ''
    ioc_name += ('-trig-' + triggers.lower()) if triggers != 'none' else ''

    if triggers.lower() not in TRIG_TYPES:
        _log.error("wrong input value for parameter 'triggers'.")
        return
    if triggers.lower().startswith('none'):
        trig_list = []
    elif not triggers.lower().startswith('all'):
        trig_list = _HLTimeSearch.get_hl_triggers({'sec': triggers.upper()})
    return ioc_name, trig_list


class _Driver(_pcaspy.Driver):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.app.driver = self

    def read(self, reason):
        _log.debug("Reading {0:s}.".format(reason))
        return super().read(reason)

    def write(self, reason, value):
        return self.app.write(reason, value)

    # def write(self, reason, value):
    #     app_ret = self.app.write(reason, value)
    #     if app_ret:
    #         self.setParam(reason, value)
    #         self.updatePVs()
    #         _log.info('{0:40s}: OK'.format(reason))
    #     else:
    #         _log.info('{0:40s}: not OK'.format(reason))
    #     return app_ret


def run(evg_params=True, triggers='all', force=False, wait=15, debug=False):
    """Start the IOC."""
    _util.configure_log_file(debug=debug)
    _log.info('Starting...')

    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # get IOC name and triggers list
    ioc_name, trig_list = _get_ioc_name_and_triggers(evg_params, triggers)
    # Creates App object
    _log.debug('Creating App Object.')
    app = _main.App(evg_params=evg_params, trig_list=trig_list)
    db = app.get_database()
    db['AS-Glob:TI-HighLvl-' + triggers.upper() + ':Version-Cte'] = {
                        'type': 'string', 'value': __version__}
    # check if IOC is already running
    running = _util.check_pv_online(
        pvname=_vaca_prefix + sorted(db.keys())[0],
        use_prefix=False, timeout=0.5)
    if running:
        _log.error('Another ' + ioc_name + ' is already running!')
        return
    _log.info('Generating database file.')
    _util.save_ioc_pv_list(
        ioc_name=ioc_name.lower(), prefix=('', _vaca_prefix), db=db)
    _log.info('File generated with {0:d} pvs.'.format(len(db)))
    _util.print_ioc_banner(
            ioc_name, db, 'High Level Timing IOC.', __version__, _vaca_prefix)
    # create a new simple pcaspy server and driver to respond client's requests
    _log.info('Creating Server.')
    server = _pcaspy.SimpleServer()
    _attribute_access_security_group(server, db)
    _log.info('Setting Server Database.')
    server.createPV(_vaca_prefix, db)
    _log.info('Creating Driver.')
    _Driver(app)

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    server_thread.daemon = True
    _log.info('Starting Server Thread.')
    server_thread.start()

    # Connects to low level PVs
    _log.info('Openning connections with Low Level IOCs.')
    app.connect(respect_ll_state=not force)

    if not force:
        tm = max(5, wait)
        _log.info('Waiting ' + str(tm) + ' seconds to start forcing.')
        stop_event.wait(tm)
        _log.info('Start forcing now.')
        if not stop_event.is_set():
            app.start_forcing()

    # main loop
    while not stop_event.is_set():
        app.process(INTERVAL)

    _log.info('Stoping Server Thread...')
    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()
    _log.info('Server Thread stopped.')
    _log.info('Good Bye.')
