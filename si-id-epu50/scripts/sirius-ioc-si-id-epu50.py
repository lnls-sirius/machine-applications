#!/usr/bin/env python-sirius
"""SI EPU ID IOC Launcher."""

import sys
import os
from si_id_epu50 import si_id_epu50 as ioc_module


# NOTE: maximum epics array size
os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '100000'


def main():
    """Launch EPU50 ID IOC."""
    args = [arg for arg in sys.argv[1:]]
    ioc_module.run(args)


if __name__ == "__main__":
    main()
