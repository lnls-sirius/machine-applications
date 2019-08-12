#!/usr/local/bin/python-sirius -u
"""TB AP PosAng IOC executable for horizontal correctors CH-Sept."""

import sys
from as_ap_posang import as_ap_posang as ioc_module

corrs_type = sys.argv[1]
ioc_module.run('tb', corrs_type)
