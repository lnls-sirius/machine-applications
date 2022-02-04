#!/usr/bin/env python-sirius -u
"""SI ID Phase-K Converter IOC Launcher."""

import sys
import os
from si_id_conv import si_id_conv as ioc_module


# NOTE: maximum epics array size
os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '100000'


def main():
    """Launch ID Conv IOC."""
    args = [arg for arg in sys.argv[1:]]
    ioc_module.run(args)


if __name__ == "__main__":
    main()
