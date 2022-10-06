import pcaspy
import threading
import traceback
import globals
import epu_db as _db
import SerialPortTests

def isPvName(reason, pvname):
    """ This function is a wrapper to allow
        scripts to inspect this source code
        for the PV names being used
    """
    return reason == pvname

class EPUSupport(pcaspy.Driver):
    """ EPU device support for the pcaspy server
    """
    def __init__(self):
        super(EPUSupport, self).__init__()
        # lock for critical operations
        self.lock = threading.Lock()
        # list of diagnostic messages
        self.diag_msg_list = []
        # EPU driver will manage and control
        # main features of device operation
        self.epu_driver = SerialPortTests.Epu()
        # start periodic polling function
        self.eid = threading.Event()
        self.tid_periodic = threading.Thread(target=self.periodic, daemon=True)
        self.tid_periodic.start()
    # periodic function
    def periodic(self):
        while True:
            self.eid.wait(globals.poll_interval)
            print('do something')
    # EPICS write
    def write(self, reason, value):
        status = True
        # take action according to PV name
        ## change gap set point
        if isPvName(reason, _db.pv_gap_sp):
            if value:
                status = self.asynExec(reason, globals.dummy, value)
            else:
                status = False
        ## change phase set point
        elif isPvName(reason, _db.pv_phase_sp):
            if value:
                status = self.asynExec(reason, globals.dummy, value)
            else:
                status = False
        ## cmd to move and change gap
        elif isPvName(reason, _db.pv_change_gap_cmd):
            status = self.asynExec(reason, globals.dummy)
        ## cmd to move and change phase
        elif isPvName(reason, _db.pv_change_phase_cmd):
            status = self.asynExec(reason, globals.dummy)
        ## select to enable/disable A and B drives
        elif isPvName(reason, _db.pv_enbl_ab_sel):
            if value:
                status = self.asynExec(reason, globals.dummy, value)
            else:
                status = False
        ## select to enable/disable S and I drives
        elif isPvName(reason, _db.pv_enbl_si_sel):
            if value:
                status = self.asynExec(reason, globals.dummy, value)
            else:
                status = False
        ## select to release/halt A and B drives
        elif isPvName(reason, _db.pv_release_ab_sel):
            if value:
                status = self.asynExec(reason, globals.dummy, value)
            else:
                status = False
        ## select to release/halt S and I drives
        elif isPvName(reason, _db.pv_release_si_sel):
            if value:
                status = self.asynExec(reason, globals.dummy, value)
            else:
                status = False
        ## cmd to enable and release A and B drives
        elif isPvName(reason, _db.pv_enbl_and_release_ab_cmd):
            status = self.asynExec(reason, globals.dummy)
            self.setParam(_db.pv_enbl_ab_sel, globals.bool_yes)
            self.setParam(_db.pv_release_ab_sel, globals.bool_yes)
            self.updatePVs()
        ## cmd to enable and release S and I drives
        elif isPvName(reason, _db.pv_enbl_and_release_si_cmd):
            status = self.asynExec(reason, globals.dummy)
            self.setParam(_db.pv_enbl_si_sel, globals.bool_yes)
            self.setParam(_db.pv_release_si_sel, globals.bool_yes)
            self.updatePVs()
        ## cmd to disable and halt A and B drives
        elif isPvName(reason, _db.pv_dsbl_and_halt_ab_cmd):
            status = self.asynExec(reason, globals.dummy)
            self.setParam(_db.pv_enbl_ab_sel, globals.bool_no)
            self.setParam(_db.pv_release_ab_sel, globals.bool_no)
            self.updatePVs()
        ## cmd to disable and halt S and I drives
        elif isPvName(reason, _db.pv_dsbl_and_halt_si_cmd):
            status = self.asynExec(reason, globals.dummy)
            self.setParam(_db.pv_enbl_si_sel, globals.bool_no)
            self.setParam(_db.pv_release_si_sel, globals.bool_no)
            self.updatePVs()
        ## no match to pv names
        else:
            status = False
        # end of write
        return status

    def asynExec(self, reason, func, *args, **kwargs):
        """ Call function in new thread and send
            callback for pv specified by reason
        """
        def execAndNotify(reason, func, *args, **kwargs):
            """ Call function and then callback after completion
            """
            # set busy status
            self.setParam(_db.pv_is_busy_mon, globals.bool_yes)
            self.updatePVs()
            # call function
            try:
                func(*args, **kwargs)
            except Exception:
                self.setParam(
                    _db.pv_ioc_msg_mon, str(traceback.format_exc())
                    )
            self.callbackPV(reason)
            # clear busy status
            self.setParam(_db.pv_is_busy_mon, globals.bool_no)
            self.updatePVs()
            self.lock.release()
        if self.lock.acquire(blocking=False):
            tid = (
                threading.Thread(
                    target=execAndNotify,
                    args=(reason, func, *args),
                    kwargs=kwargs
                )
            )
            tid.start()
            return True
        else:
            # inform that device is busy
            self.setParam(_db.pv_ioc_msg_mon, globals.msg_device_busy)
            self.updatePVs()
            return False
