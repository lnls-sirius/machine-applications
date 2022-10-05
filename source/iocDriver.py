import pcaspy
import threading
import globals
from utils import asynch, schedule


class EPUDriver(pcaspy.Driver):
    def __init__(self):
        super(EPUDriver, self).__init__()
    # EPICS read
    def read(self, reason):
        if reason == 'RAND':
            NOP
        else:
            value = self.getParam(reason)
        return value
    # EPICS write
    def write(self, reason, value):
        status = True
        # take proper actions
        if reason == 'COMMAND':
            if not self.tid:
                command = value
                if command:
                    self.tid = threading.Thread(target=self.exampleAsynExec,args=(command,))
                    self.tid.start()
            else:
                status = False
        else:
            status = False
        # store the values
        if status:
            self.setParam(reason, value)
        return status
    # Example periodic function
    @asynch
    @schedule(globals.driver_update_rate)
    def periodic_driver_update():
        print('example')
    # Example asynchronous write
    def exampleAsynExec(self, command):
        print("DEBUG: Asyn exec ", command)
        # set status BUSY
        self.setParam('STATUS', 1)
        self.updatePVs()
        # run shell
        try:
            NOP
        except Exception:
            self.setParam('ERROR', str(sys.exc_info()[1]))
            self.setParam('OUTPUT', '')
        else:
            self.setParam('ERROR', proc.stderr.read().rstrip())
            self.setParam('OUTPUT', proc.stdout.read().rstrip())
        self.callbackPV('COMMAND')
        # set status DONE
        self.setParam('STATUS', 0)
        self.updatePVs()
        self.tid = None
        print("DEBUG: Finish ", command)