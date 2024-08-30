#!/usr/bin/env python-sirius
"""BO AP Chromaticity Correction IOC executable."""

from as_ap_opticscorr.chrom import chrom as ioc_module

ioc_module.run('bo')
