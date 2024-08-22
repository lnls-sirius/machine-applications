#!/usr/bin/env python-sirius
"""SI AP Tune Correction IOC executable."""

from as_ap_opticscorr.tune import tune as ioc_module

ioc_module.run('si')
