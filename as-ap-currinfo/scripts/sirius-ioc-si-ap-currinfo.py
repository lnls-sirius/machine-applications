#!/usr/bin/env python-sirius
"""SI-AP-CurrentInfo IOC executable."""

from as_ap_currinfo import as_ap_currinfo as ioc_module

ioc_module.run('si')
