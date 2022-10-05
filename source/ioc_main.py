import pcaspy
import sys
import os
import traceback
import globals
import iocDriver
import epu_db

if __name__ == '__main__':
    server = pcaspy.SimpleServer()
    server.createPV(epu_db.pv_prefix, epu_db.pvdb)
    driver = iocDriver.EPUDriver()

    while True:
        try:
            # process CA transactions
            server.process(globals.ca_process_rate)
        except Exception:
            traceback.print_exc(file=sys.stdout)
            os._exit(0)
