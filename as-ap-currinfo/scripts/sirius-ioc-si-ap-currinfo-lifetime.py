#!/usr/bin/env -S python-sirius -u
"""SI-AP-CurrentInfo-Lifetime IOC executable."""

from as_ap_currinfo.lifetime import lifetime as ioc_module
ioc_module.run()
