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

def isBoolNum(value):
    """ This function checks if an integer
        value could represent a bool, i.e.,
        if it is 0 or 1
    """
    return value == 0 or value == 1

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
        try:
            self.epu_driver = SerialPortTests.Epu()
            print('Epu driver initialized')
        except Exception:
            print('Could not init epu driver')
        # start periodic polling function
        self.eid = threading.Event()
        self.tid_periodic = threading.Thread(target=self.periodic, daemon=True)
        self.tid_periodic.start()
    # periodic function
    def periodic(self):
        while True:
            self.eid.wait(globals.poll_interval)
            pass
    # EPICS write
    def write(self, reason, value):
        status = True
        # take action according to PV name
        ## change gap set point
        if isPvName(reason, _db.pv_gap_sp):
            if value:
                if (value >= globals.min_gap
                        and value <= globals.max_gap
                        ):
                    status = self.asynExec(reason, globals.dummy, value)
                    if status:
                        self.setParam(_db.pv_gap_sp, value)
                        self.updatePVs()
                else:
                    status = False
            else:
                status = False
        ## change phase set point
        elif isPvName(reason, _db.pv_phase_sp):
            if value:
                if (value >= globals.min_phase
                        and value <= globals.max_phase
                        ):
                    status = self.asynExec(reason, globals.dummy, value)
                    if status:
                        self.setParam(_db.pv_phase_sp, value)
                        self.updatePVs()
                else:
                    status = False
            else:
                status = False
        ## cmd to move and change gap
        elif isPvName(reason, _db.pv_change_gap_cmd):
            if _db.pv_allowed_change_gap_mon == globals.bool_yes:
                status = self.asynExec(reason, globals.dummy)
            else:
                status = False
        ## cmd to move and change phase
        elif isPvName(reason, _db.pv_change_phase_cmd):
            if _db.pv_allowed_change_phase_mon == globals.bool_yes:
                status = self.asynExec(reason, globals.dummy)
            else:
                status = False
        ## select to enable/disable A and B drives
        elif isPvName(reason, _db.pv_enbl_ab_sel):
            if value:
                if isBoolNum(value):
                    status = self.asynExec(reason, globals.dummy, value)
                    if status:
                        self.setParam(_db.pv_enbl_ab_sel, value)
                        self.updatePVs()
                else:
                    status = False
            else:
                status = False
        ## select to enable/disable S and I drives
        elif isPvName(reason, _db.pv_enbl_si_sel):
            if value:
                if isBoolNum(value):
                    status = self.asynExec(reason, globals.dummy, value)
                    if status:
                        self.setParam(_db.pv_enbl_si_sel, value)
                        self.updatePVs()
                else:
                    status = False
            else:
                status = False
        ## select to release/halt A and B drives
        elif isPvName(reason, _db.pv_release_ab_sel):
            if value:
                if isBoolNum(value):
                    status = self.asynExec(reason, globals.dummy, value)
                    if status:
                        self.setParam(_db.pv_release_ab_sel, value)
                        self.updatePVs()
                else:
                    status = False
            else:
                status = False
        ## select to release/halt S and I drives
        elif isPvName(reason, _db.pv_release_si_sel):
            if value:
                if isBoolNum(value):
                    status = self.asynExec(reason, globals.dummy, value)
                    if status:
                        self.setParam(_db.pv_release_si_sel, value)
                        self.updatePVs()
                else:
                    status = False
            else:
                status = False
        ## cmd to enable and release A and B drives
        elif isPvName(reason, _db.pv_enbl_and_release_ab_cmd):
            status = self.asynExec(reason, globals.dummy)
            if status:
                self.setParam(_db.pv_enbl_ab_sel, globals.bool_yes)
                self.setParam(_db.pv_release_ab_sel, globals.bool_yes)
                self.updatePVs()
        ## cmd to enable and release S and I drives
        elif isPvName(reason, _db.pv_enbl_and_release_si_cmd):
            status = self.asynExec(reason, globals.dummy)
            if status:
                self.setParam(_db.pv_enbl_si_sel, globals.bool_yes)
                self.setParam(_db.pv_release_si_sel, globals.bool_yes)
                self.updatePVs()
        ## cmd to disable and halt A and B drives
        elif isPvName(reason, _db.pv_dsbl_and_halt_ab_cmd):
            status = self.asynExec(reason, globals.dummy)
            if status:
                self.setParam(_db.pv_enbl_ab_sel, globals.bool_no)
                self.setParam(_db.pv_release_ab_sel, globals.bool_no)
                self.updatePVs()
        ## cmd to disable and halt S and I drives
        elif isPvName(reason, _db.pv_dsbl_and_halt_si_cmd):
            status = self.asynExec(reason, globals.dummy)
            if status:
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
