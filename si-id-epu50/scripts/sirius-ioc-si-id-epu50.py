#!/usr/bin/env python-sirius
"""SI EPU ID IOC Launcher."""

import os as os
import argparse

from si_id_epu50 import constants as cte
from si_id_epu50 import si_id_epu50 as ioc_module


# NOTE: maximum epics array size
os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '100000'

AUTOSAVE_DEFAULT_REQUEST_FILE = os.path.join(
    os.path.dirname(__file__), 'config', 'autosave_epu.req')
AUTOSAVE_DEFAULT_SAVE_LOCATION = os.path.join(
    os.path.dirname(__file__), 'config')

DEFAULT_PV_PREFIX = 'SI-10SB:ID-EPU50:'
BBB_DEFAULT_ADDR = '10.128.110.160'


def getArgs():
    """ Return command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--pv-prefix', dest='pv_prefix', type=str, required=False,
        default=DEFAULT_PV_PREFIX, help="Prefix for EPICS IOC PVs"
        )
    parser.add_argument(
        '--drive-msg-port', dest='msg_port', type=int, required=False,
        default=cte.RS485_TCP_DEFAULT_PORT, help="TCP port for drive messages"
        )
    parser.add_argument(
        '--drive-io-port', dest='io_port', type=int, required=False,
        default=cte.GPIO_TCP_DEFAULT_PORT,
        help="TCP port for virtual I/O commands"
        )
    parser.add_argument(
        '--beaglebone-addr', dest='beaglebone_addr', type=str, required=False,
        default=BBB_DEFAULT_ADDR, help="Beaglebone IP address"
        )
    parser.add_argument(
        '--autosave-dir', dest='autosave_dir', type=str, required=False,
        default=cte.AUTOSAVE_DEFAULT_SAVE_LOCATION, help="Autosave save directory"
        )
    parser.add_argument(
        '--request-file', dest='request_file', type=str, required=False,
        default=cte.AUTOSAVE_DEFAULT_REQUEST_FILE, help="Autosave request file name"
        )
    args = parser.parse_args()
    return args


def main():
    """Launch EPU50 ID IOC."""
    args = getArgs()
    ioc_module.run(args)


if __name__ == "__main__":
    main()
