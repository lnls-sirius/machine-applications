import pcaspy
import sys
import os
import traceback
import constants as _cte
import iocDriver
import epu_db

if __name__ == '__main__':
    if epu_db.pv_prefix == '':
        raise ValueError('PV prefix is missing')
    # create CA server
    server = pcaspy.SimpleServer()
    # config access security
    server.initAccessSecurityFile(
        _cte.access_security_filename, PREFIX=epu_db.pv_prefix
        )
    # instantiate PV database
    server.createPV(epu_db.pv_prefix, epu_db.pvdb)
    # create pcaspy driver
    driver = iocDriver.EPUSupport()

    while True:
        try:
            # process CA transactions
            server.process(_cte.ca_process_rate)
        except Exception:
            traceback.print_exc(file=sys.stdout)
            os._exit(0)
