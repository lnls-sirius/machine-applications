import pcaspy
import sys
import os
import traceback
import globals
import iocDriver
import epu_db

if __name__ == '__main__':
    # create CA server
    server = pcaspy.SimpleServer()
    # config access security
    server.initAccessSecurityFile(
        globals.access_security_filename, PREFIX=epu_db.pv_prefix
        )
    # instantiate PV database
    server.createPV(epu_db.pv_prefix, epu_db.pvdb)
    # create pcaspy driver
    driver = iocDriver.EPUSupport()

    while True:
        try:
            # process CA transactions
            server.process(globals.ca_process_rate)
        except Exception:
            traceback.print_exc(file=sys.stdout)
            os._exit(0)
