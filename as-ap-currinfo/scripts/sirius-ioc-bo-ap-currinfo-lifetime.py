#!/usr/local/bin/python-sirius -u
"""BO-AP-CurrentInfo-Lifetime IOC executable."""

from as_ap_currinfo.lifetime import lifetime as ioc_module
ioc_module.run('bo')
