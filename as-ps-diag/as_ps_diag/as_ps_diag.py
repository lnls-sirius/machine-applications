#!/usr/local/bin/python-sirius
"""AS PS Diagnostic."""

import os as _os
import sys as _sys
import signal as _signal
import logging as _log

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools

from .driver import PSDiagDriver as _PSDiagDriver

from siriuspy import util as _util
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy.util import get_timestamp as _get_timestamp
from siriuspy.util import configure_log_file as _config_log_file
from siriuspy.util import print_ioc_banner as _print_ioc_banner
from siriuspy.csdevice.psdiag import get_ps_diag_propty_database as \
    _get_database
from siriuspy.search import PSSearch as _PSSearch


_COMMIT_HASH = _util.get_last_commit_hash()

INTERVAL = 0.1
_stop_event = False


def _stop_now(signum, frame):
    global _stop_event
    _log.warning(_signal.Signals(signum).name +
                 ' received at ' + _get_timestamp())
    _sys.stdout.flush()
    _sys.stderr.flush()
    _stop_event = True


def _attribute_access_security_group(server, db):
    for k, v in db.items():
        if k.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            v.update({'asg': 'rbpv'})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')


def run(section='', sub_section='', device='', debug=False):
    """Run IOC."""
    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # configure log
    _config_log_file(debug=debug)

    _log.info("Loding power supplies")
    _log.info("{:12s}: {}".format('\tSection', section or 'None'))
    _log.info("{:12s}: {}".format('\tSub Section', sub_section or 'None'))
    _log.info("{:12s}: {}".format('\tDevice', device or 'None'))

    server = _pcaspy.SimpleServer()
    device_filter = dict()
    if section:
        device_filter['sec'] = section
    if sub_section:
        device_filter['sub'] = sub_section
    if device:
        device_filter['dev'] = device
    device_filter['dis'] = 'PS'
    psnames = _PSSearch.get_psnames(device_filter)

    if not psnames:
        _log.warning('No devices found. Aborting.')
        _sys.exit(0)

    # create PV database
    prefix = _vaca_prefix
    pvdb = dict()
    for psname in psnames:
        _log.debug('{:32s}'.format(psname))
        db = _get_database(psname)
        for key, value in db.items():
            if key == 'DiagVersion-Cte':
                value['value'] = _COMMIT_HASH
            pvname = psname + ':' + key
            print(pvname)
            pvdb[pvname] = value
    _log.info("Creating server with %d devices and '%s' prefix",
              len(psnames), prefix)
    _attribute_access_security_group(server, pvdb)
    server.createPV(prefix, pvdb)

    # create driver
    _log.info('Creating driver')
    try:
        driver = _PSDiagDriver(prefix, psnames)
    except Exception:
        _log.error('Failed to create driver. Aborting', exc_info=True)
        _sys.exit(1)

    _print_ioc_banner(
        'AS PS Diagnostic', pvdb,
        'IOC that provides current sp/mon diagnostics for the power supplies.',
        '0.2', prefix)

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    server_thread.start()

    driver.scanning = True
    while not _stop_event:
        server.process(INTERVAL)

    driver.scanning = False
    driver.quit = True

    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()
    # _sys.exit(0)