import pcaspy
import threading
import traceback
import constants
import epu_db as _db
import Epu

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

def inTolerance(value1, value2, tol):
    return abs(value1 - value2) <= tol

class EPUSupport(pcaspy.Driver):
    """ EPU device support for the pcaspy server
    """
    def __init__(self):
        super(EPUSupport, self).__init__()
        # lock for critical operations
        self.lock = threading.Lock()
        # EPU driver will manage and control
        # main features of device operation
        try:
            self.epu_driver = Epu.Epu(callback_update=self.priority_call)
            print('Epu driver initialized')
        except Exception:
            print('Could not init epu driver')
        # start periodic polling function
        self.eid = threading.Event()
        self.tid_periodic = threading.Thread(target=self.periodic, daemon=True)
        self.tid_periodic.start()
    # priority callback
    def priority_call(self):
        # update encoder readings
        self.setParam(
            _db.pv_drive_a_encoder_pos_mon,
            self.epu_driver.a_encoder_gap)
        self.setParam(
            _db.pv_drive_b_encoder_pos_mon,
            self.epu_driver.b_encoder_gap)
        self.setParam(
            _db.pv_drive_s_encoder_pos_mon,
            self.epu_driver.s_encoder_phase)
        self.setParam(
            _db.pv_drive_i_encoder_pos_mon,
            self.epu_driver.i_encoder_phase)
        # update PVs
        self.updatePVs()
    # periodic function
    def periodic(self):
        while True:
            self.eid.wait(constants.poll_interval)
            # read allowed to move status
            if self.epu_driver.gap_change_allowed:
                self.setParam(
                    _db.pv_allowed_change_gap_mon,
                    constants.bool_yes)
            else:
                self.setParam(
                    _db.pv_allowed_change_gap_mon,
                    constants.bool_no)
            if self.epu_driver.phase_change_allowed:
                self.setParam(
                    _db.pv_allowed_change_phase_mon,
                    constants.bool_yes)
            else:
                self.setParam(
                    _db.pv_allowed_change_phase_mon,
                    constants.bool_no)
            # update combined position pvs
            self.setParam(
                _db.pv_gap_rb,
                self.epu_driver.gap_target)
            self.setParam(
                _db.pv_gap_mon,
                self.epu_driver.gap)
            self.setParam(
                _db.pv_phase_rb,
                self.epu_driver.phase_target)
            self.setParam(
                _db.pv_phase_mon,
                self.epu_driver.phase)
            # update resolver readings
            self.setParam(
                _db.pv_drive_a_resolver_pos_mon,
                self.epu_driver.a_resolver_gap)
            self.setParam(
                _db.pv_drive_b_resolver_pos_mon,
                self.epu_driver.b_resolver_gap)
            self.setParam(
                _db.pv_drive_s_resolver_pos_mon,
                self.epu_driver.s_resolver_phase)
            self.setParam(
                _db.pv_drive_i_resolver_pos_mon,
                self.epu_driver.i_resolver_phase)
            # update enable and halt status
            self.setParam(
                _db.pv_enbl_ab_sts,
                self.epu_driver.gap_enable)
            self.setParam(
                _db.pv_enbl_si_sts,
                self.epu_driver.phase_enable)
            self.setParam(
                _db.pv_release_ab_sts,
                self.epu_driver.gap_halt_released)
            self.setParam(
                _db.pv_release_si_sts,
                self.epu_driver.phase_halt_released)
            self.setParam(
                _db.pv_enbl_and_release_ab_sts,
                self.epu_driver.gap_enable_and_halt_released)
            self.setParam(
                _db.pv_enbl_and_release_si_sts,
                self.epu_driver.phase_enable_and_halt_released)
            # update speed pvs
            self.setParam(
                _db.pv_gap_velo_mon,
                self.epu_driver.gap_velocity)
            self.setParam(
                _db.pv_phase_velo_mon,
                self.epu_driver.phase_velocity)
            self.setParam(
                _db.pv_drive_a_velo_mon,
                self.epu_driver.a_act_velocity)
            self.setParam(
                _db.pv_drive_b_velo_mon,
                self.epu_driver.b_act_velocity)
            self.setParam(
                _db.pv_drive_s_velo_mon,
                self.epu_driver.s_act_velocity)
            self.setParam(
                _db.pv_drive_i_velo_mon,
                self.epu_driver.i_act_velocity)
            # update diagnostic codes
            self.setParam(
                _db.pv_drive_a_diag_code_mon,
                self.epu_driver.a_diag_code)
            self.setParam(
                _db.pv_drive_b_diag_code_mon,
                self.epu_driver.b_diag_code)
            self.setParam(
                _db.pv_drive_s_diag_code_mon,
                self.epu_driver.s_diag_code)
            self.setParam(
                _db.pv_drive_i_diag_code_mon,
                self.epu_driver.i_diag_code)
            # check overall fault state
            not_ok = not (
                self.epu_driver.a_diag_code == ' A211'
                and self.epu_driver.b_diag_code == ' A211'
                and self.epu_driver.b_diag_code == ' A211'
                and self.epu_driver.b_diag_code == ' A211'
            )
            self.setParam(
                _db.pv_status_mon,
                not_ok)
            # update moving status
            self.setParam(
                _db.pv_drive_a_is_moving_mon,
                self.epu_driver.a_is_moving)
            self.setParam(
                _db.pv_drive_b_is_moving_mon,
                self.epu_driver.b_is_moving)
            self.setParam(
                _db.pv_drive_s_is_moving_mon,
                self.epu_driver.s_is_moving)
            self.setParam(
                _db.pv_drive_i_is_moving_mon,
                self.epu_driver.i_is_moving)
            if self.epu_driver.is_moving:
                self.setParam(_db.pv_is_moving_mon, constants.bool_yes)
            else:
                self.setParam(_db.pv_is_moving_mon, constants.bool_no)
            # update read-only PVs
            self.updatePVs()
    # EPICS write
    def write(self, reason, value):
        status = True
        # take action according to PV name
        ## enable control from beamlines
        if isPvName(reason, _db.pv_beamline_enbl_sel):
            if isBoolNum(value):
                self.setParam(_db.pv_beamline_enbl_sel, value)
                self.updatePVs()
            else:
                status = False
        ## clear IOC log
        elif isPvName(reason, _db.pv_clear_log_cmd):
            # clear ioc msg
            self.setParam(_db.pv_ioc_msg_mon, constants.msg_clear)
            # increment cmd pv
            old_value = self.getParam(_db.pv_change_gap_cmd)
            self.setParam(_db.pv_change_gap_cmd, old_value+1)
            self.updatePVs()
        ## change gap set point
        if isPvName(reason, _db.pv_gap_sp):
            if (value >= constants.min_gap
                    and value <= constants.max_gap
                    ):
                status = self.asynExec(
                    reason, self.epu_driver.gap_set, value)
                if status:
                    self.setParam(_db.pv_gap_sp, value)
                    self.updatePVs()
            else:
                status = False
        ## change phase set point
        elif isPvName(reason, _db.pv_phase_sp):
            if (value >= constants.min_phase
                    and value <= constants.max_phase
                    ):
                status = self.asynExec(
                    reason, self.epu_driver.phase_set, value)
                if status:
                    self.setParam(_db.pv_phase_sp, value)
                    self.updatePVs()
            else:
                status = False
        ## change gap maximum velocity set point
        elif isPvName(reason, _db.pv_gap_max_velo_sp):
            if (value > 0
                    and value <= constants.max_velo
                    ):
                self.setParam(_db.pv_gap_max_velo_sp, value)
                self.setParam(_db.pv_gap_max_velo_rb, value)
                self.updatePVs()
            else:
                status = False
        ## change phase maximum velocity set point
        elif isPvName(reason, _db.pv_phase_max_velo_sp):
            if (value > 0
                    and value <= constants.max_velo
                    ):
                self.setParam(_db.pv_phase_max_velo_sp, value)
                self.setParam(_db.pv_phase_max_velo_rb, value)
                self.updatePVs()
            else:
                status = False
        ## change gap velocity set point
        elif isPvName(reason, _db.pv_gap_velo_sp):
            soft_max_velo = self.getParam(_db.pv_gap_max_velo_sp)
            if (value > 0
                    and value <= constants.max_velo
                    and value <= soft_max_velo
                    ):
                status = self.asynExec(
                    reason, self.epu_driver.gap_velo_config_set, value)
                if status:
                    self.setParam(_db.pv_gap_velo_sp, value)
                    self.updatePVs()
            else:
                status = False
        ## change phase velocity set point
        elif isPvName(reason, _db.pv_phase_velo_sp):
            soft_max_velo = self.getParam(_db.pv_phase_max_velo_sp)
            if (value > 0
                    and value <= constants.max_velo
                    and value <= soft_max_velo
                    ):
                status = self.asynExec(
                    reason, self.epu_driver.phase_velo_config_set, value)
                if status:
                    self.setParam(_db.pv_phase_velo_sp, value)
                    self.updatePVs()
            else:
                status = False
        ## cmd to move and change gap
        elif isPvName(reason, _db.pv_change_gap_cmd):
            if _db.pv_allowed_change_gap_mon == constants.bool_yes:
                status = self.asynExec(reason, self.epu_driver.start_gap)
                # increment cmd pv
                old_value = self.getParam(_db.pv_change_gap_cmd)
                self.setParam(_db.pv_change_gap_cmd, old_value+1)
                self.updatePVs()
            else:
                status = False
        ## cmd to move and change phase
        elif isPvName(reason, _db.pv_change_phase_cmd):
            if _db.pv_allowed_change_phase_mon == constants.bool_yes:
                status = self.asynExec(reason, self.epu_driver.start_phase)
                # increment cmd pv
                old_value = self.getParam(_db.pv_change_phase_cmd)
                self.setParam(_db.pv_change_phase_cmd, old_value+1)
                self.updatePVs()
            else:
                status = False
        ## select to enable/disable A and B drives
        elif isPvName(reason, _db.pv_enbl_ab_sel):
            if isBoolNum(value):
                status = self.asynExec(
                    reason, self.epu_driver.gap_set_enable, bool(value))
                if status:
                    self.setParam(_db.pv_enbl_ab_sel, value)
                    self.updatePVs()
            else:
                status = False
        ## select to enable/disable S and I drives
        elif isPvName(reason, _db.pv_enbl_si_sel):
            if isBoolNum(value):
                status = self.asynExec(
                    reason, self.epu_driver.phase_set_enable, bool(value))
                if status:
                    self.setParam(_db.pv_enbl_si_sel, value)
                    self.updatePVs()
            else:
                status = False
        ## select to release/halt A and B drives
        elif isPvName(reason, _db.pv_release_ab_sel):
            if (isBoolNum(value)
            and _db.pv_enbl_ab_sel == constants.bool_yes):
                status = self.asynExec(
                    reason, self.epu_driver.gap_release_halt, bool(value))
                if status:
                    self.setParam(_db.pv_release_ab_sel, value)
                    self.updatePVs()
            else:
                status = False
        ## select to release/halt S and I drives
        elif isPvName(reason, _db.pv_release_si_sel):
            if (isBoolNum(value)
            and _db.pv_enbl_si_sel == constants.bool_yes):
                status = self.asynExec(
                    reason, self.epu_driver.phase_release_halt, bool(value))
                if status:
                    self.setParam(_db.pv_release_si_sel, value)
                    self.updatePVs()
            else:
                status = False
        ## cmd to enable and release A and B drives
        elif isPvName(reason, _db.pv_enbl_and_release_ab_sel):
            if isBoolNum(value):
                status = self.asynExec(
                    reason, self.epu_driver.gap_enable_and_release_halt, bool(value))
                if status:
                    # update enbl and release pvs
                    self.setParam(_db.pv_enbl_ab_sel, value)
                    self.setParam(_db.pv_release_ab_sel, value)
                    # update pv
                    self.setParam(_db.pv_enbl_and_release_ab_sel, value)
                    self.updatePVs()
            else:
                status = False
        ## cmd to enable and release S and I drives
        elif isPvName(reason, _db.pv_enbl_and_release_si_sel):
            if isBoolNum(value):
                status = self.asynExec(
                    reason, self.epu_driver.phase_enable_and_release_halt, bool(value))
                if status:
                    # update enbl and release pvs
                    self.setParam(_db.pv_enbl_si_sel, value)
                    self.setParam(_db.pv_release_si_sel, value)
                    # update pv
                    self.setParam(_db.pv_enbl_and_release_si_sel, value)
                    self.updatePVs()
            else:
                status = False
        elif isPvName(reason, _db.pv_stop_cmd):
            status = self.asynExec(reason, self.epu_driver.stop_all)
            # increment cmd pv
            old_value = self.getParam(_db.pv_stop_cmd)
            self.setParam(_db.pv_stop_cmd, old_value+1)
            # halt motor drives
            self.setParam(_db.pv_release_ab_sel, constants.bool_no)
            self.setParam(_db.pv_release_si_sel, constants.bool_no)
            # update pvs
            self.updatePVs()
        elif isPvName(reason, _db.pv_stop_ab_cmd):
            status = self.asynExec(reason, self.epu_driver.gap_stop)
            # increment cmd pv
            old_value = self.getParam(_db.pv_stop_ab_cmd)
            self.setParam(_db.pv_stop_ab_cmd, old_value+1)
            # halt motor drives
            self.setParam(_db.pv_release_ab_sel, constants.bool_no)
            # update pvs
            self.updatePVs()
        elif isPvName(reason, _db.pv_stop_si_cmd):
            status = self.asynExec(reason, self.epu_driver.phase_stop)
            # increment cmd pv
            old_value = self.getParam(_db.pv_stop_si_cmd)
            self.setParam(_db.pv_stop_si_cmd, old_value+1)
            # halt motor drives
            self.setParam(_db.pv_release_si_sel, constants.bool_no)
            # update pvs
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
            self.setParam(_db.pv_is_busy_mon, constants.bool_yes)
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
            self.setParam(_db.pv_is_busy_mon, constants.bool_no)
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
            self.setParam(_db.pv_ioc_msg_mon, constants.msg_device_busy)
            self.updatePVs()
            return False
