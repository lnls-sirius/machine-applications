#!/usr/bin/env python-sirius -u
"""BO AP Tune Correction IOC executable."""

from as_ap_opticscorr.tune import tune as ioc_module
ioc_module.run('bo')
