#!/usr/local/bin/python-sirius -u
"""BO-AP-CurrentInfo-Current IOC executable."""

from as_ap_currinfo.current import current as ioc_module
ioc_module.run('bo')
