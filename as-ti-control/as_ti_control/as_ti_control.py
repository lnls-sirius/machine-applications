"""IOC Module."""
import sys as _sys
import logging as _log
import signal as _signal
from threading import Event as _Event
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
from as_ti_control import main as _main
from siriuspy.util import get_last_commit_hash as _get_version
from siriuspy.envars import vaca_prefix as PREFIX
from siriuspy.search import HLTimeSearch as _HLTimeSearch

__version__ = _get_version()
INTERVAL = 0.1
stop_event = _Event()

_hl_trig = _HLTimeSearch.get_hl_triggers()
TRIG_LISTS = {
    'si-dip-quads': ['SI-Glob:TI-Quads:', 'SI-Glob:TI-Dips:'],
    'si-sexts-skews': ['SI-Glob:TI-Sexts:', 'SI-Glob:TI-Skews:'],
    'si-corrs': ['SI-Glob:TI-Corrs:'],
    'si-dig': [
        'SI-01SA:TI-HTuneS:', 'SI-01SA:TI-InjK:',
        'SI-13C4:TI-DCCT:', 'SI-14C4:TI-DCCT:',
        'SI-16C4:TI-GBPM:', 'SI-17C4:TI-VTuneP:',
        'SI-17SA:TI-HTuneP:', 'SI-18C4:TI-VTuneS:',
        'SI-19C4:TI-VPing:', 'SI-19SP:TI-GSL15:',
        'SI-20SB:TI-GSL07:', 'SI-01SA:TI-HPing:'],
    'li-all': [
        'LI-01:TI-EGun:MultBun', 'LI-01:TI-EGun:SglBun',
        'LI-01:TI-ICT-1:', 'LI-01:TI-ICT-2:',
        'LI-01:TI-Modltr-1:', 'LI-01:TI-Modltr-2:',
        'LI-Fam:TI-BPM:', 'LI-Fam:TI-Scrn:',
        'LI-Glob:TI-LLRF-1:', 'LI-Glob:TI-LLRF-2:',
        'LI-Glob:TI-LLRF-3:', 'LI-Glob:TI-RFAmp-1:',
        'LI-Glob:TI-RFAmp-2:', 'LI-Glob:TI-SHAmp:'],
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


def _print_pvs_in_file(db, fname):
    with open('pvs/' + fname, 'w') as f:
        for key in sorted(db.keys()):
            f.write(PREFIX+'{0:40s}\n'.format(key))
    _log.info(fname+' file generated with {0:d} pvs.'.format(len(db)))


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


def run(evg_params=True, triggers='all', debug=False):
    """Start the IOC."""
    trig_list = TRIG_LISTS.get(triggers, [])

    level = _log.DEBUG if debug else _log.INFO
    fmt = ('%(levelname)7s | %(asctime)s | ' +
           '%(module)15s.%(funcName)20s[%(lineno)4d] ::: %(message)s')
    _log.basicConfig(format=fmt, datefmt='%F %T', level=level,
                     stream=_sys.stdout)
    #  filename=LOG_FILENAME, filemode='w')
    _log.info('Starting...')

    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # Creates App object
    _log.info('Creating App.')
    app = _main.App(evg_params=evg_params, triggers_list=trig_list)
    _log.info('Generating database file.')
    fname = 'AS-TI-'
    fname += 'EVG-PARAMS-' if evg_params else ''
    fname += triggers.upper() + '-' if triggers != 'none' else ''
    db = app.get_database()
    db.update({fname+'Version-Cte': {'type': 'string', 'value': __version__}})
    _print_pvs_in_file(db, fname=fname+'pvs.txt')

    # create a new simple pcaspy server and driver to respond client's requests
    _log.info('Creating Server.')
    server = _pcaspy.SimpleServer()
    _log.info('Setting Server Database.')
    server.createPV(PREFIX, db)
    _log.info('Creating Driver.')
    pcas_driver = _Driver(app)

    # Connects to low level PVs
    _log.info('Openning connections with Low Level IOCs.')
    app.connect()

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    _log.info('Starting Server Thread.')
    server_thread.start()

    # main loop
    while not stop_event.is_set():
        pcas_driver.app.process(INTERVAL)

    _log.info('Stoping Server Thread...')
    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()
    _log.info('Server Thread stopped.')
    _log.info('Good Bye.')
