#!/usr/local/bin/python-sirius -u
"""IOC Module."""
import sys as _sys
import logging as _log
import signal as _signal
import argparse as _argparse
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
import main as _main
from siriuspy.timesys.time_data import Triggers

INTERVAL = 0.1
stop_event = False
PREFIX = ''
DB_FILENAME = 'my_pvs.txt'

_hl_trig = Triggers().hl_triggers
TRIG_LISTS = {
    'si-dip-quads': ['SI-Glob:TI-Quads:', 'SI-Glob:TI-Dips:'],
    'si-sexts-skews': ['SI-Glob:TI-Sexts:', 'SI-Glob:TI-Skews:'],
    'si-corrs': ['SI-Glob:TI-Corrs:'],
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
    stop_event = True


def _print_pvs_in_file(db):
    with open(DB_FILENAME, 'w') as f:
        for key in sorted(db.keys()):
            f.write('{0:20s}\n'.format(key))
    _log.info(DB_FILENAME+' file generated with {0:d} pvs.'.format(len(db)))


class _PCASDriver(_pcaspy.Driver):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.app.driver = self

    def read(self, reason):
        _log.debug("Sending read of {0:s} to App.".format(reason))
        value = self.app.read(reason)
        if value is None:
            _log.debug("PV {0:s} read by App. Trying drivers database."
                       .format(reason))
            return super().read(reason)
        else:
            _log.debug("App returned {0:s} for PV {1:s}."
                       .format(str(value), reason))
            return value

    def write(self, reason, value):
        app_ret = self.app.write(reason, value)
        if app_ret:
            self.setParam(reason, value)
        self.updatePVs()
        return app_ret


def run(events=True, clocks=True, triggers='all'):
    """Start the IOC."""

    trig_list = TRIG_LISTS.get(triggers, [])

    level = _log.INFO
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
    app = _main.App(events=events, clocks=clocks, triggers_list=trig_list)
    _log.info('Generating database file.')
    db = app.get_database()
    _print_pvs_in_file(db)

    # create a new simple pcaspy server and driver to respond client's requests
    _log.info('Creating Server.')
    server = _pcaspy.SimpleServer()
    _log.info('Setting Server Database.')
    server.createPV(PREFIX, db)
    _log.info('Creating Driver.')
    pcas_driver = _PCASDriver(app)

    # Connects to low level PVs
    _log.info('Openning connections with Low Level IOCs.')
    app.connect()

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    _log.info('Starting Server Thread.')
    server_thread.start()

    # main loop
    # while not stop_event.is_set():
    while not stop_event:
        pcas_driver.app.process(INTERVAL)

    _log.info('Stoping Server Thread...')
    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()
    _log.info('Server Thread stopped.')
    _log.info('Good Bye.')


if __name__ == '__main__':
    parser = _argparse.ArgumentParser(description="Run Timing IOC.")
    parser.add_argument('-e', '--events', action='store_true', default=False,
                        help="Manage High Level Events")
    parser.add_argument('-c', '--clocks', action='store_true', default=False,
                        help="Manage High Level Clocks")
    parser.add_argument('-t', "--triggers", type=str, default='none',
                        help="Which Triggers to manage",
                        choices=sorted(TRIG_LISTS.keys()))
    args = parser.parse_args()
    run(**args)
