#!/usr/local/bin/python-sirius -u
"""SI-AP-CurrentInfo-Current IOC executable."""

from as_ap_currinfo.current import current as ioc_module
ioc_module.run('si')
