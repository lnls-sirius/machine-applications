import pcaspy
import threading
import traceback
import time
import constants as _cte
import epu_db as _db
import epu

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

def isValid(value):
    """ Checks if a given parameter is
        valid as a PV value
    """
    return value != None

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
            self.epu_driver = epu.Epu(callback_update=self.priority_call)
            print('Epu driver initialized')
        except Exception:
            print('Could not init epu driver')
        # start periodic polling function
        self.eid = threading.Event()
        self.init_vars()
        self.tid_periodic = threading.Thread(target=self.periodic, daemon=True)
        self.tid_periodic.start()
    # variable initialization
    def init_vars(self):
        self._old_gap = self.epu_driver.gap
        self._old_gap_sample_timestamp = time.time()
        self._old_phase = self.epu_driver.phase
        self._old_phase_sample_timestamp = time.time()
    # increment pv value
    def incParam(self, pv_name, inc=1):
        _old_value = self.getParam(pv_name)
        self.setParam(pv_name, _old_value+inc)
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
            self.eid.wait(_cte.poll_interval)
            # read allowed to move status
            if (
                isValid(self.epu_driver.gap_change_allowed)
                and self.epu_driver.gap_change_allowed
                ):
                self.setParam(
                    _db.pv_allowed_change_gap_mon,
                    _cte.bool_yes)
            else:
                self.setParam(
                    _db.pv_allowed_change_gap_mon,
                    _cte.bool_no)
            if (
                isValid(self.epu_driver.phase_change_allowed)
                and self.epu_driver.phase_change_allowed
            ):
                self.setParam(
                    _db.pv_allowed_change_phase_mon,
                    _cte.bool_yes)
            else:
                self.setParam(
                    _db.pv_allowed_change_phase_mon,
                    _cte.bool_no)
            # update combined position pvs
            ## gap pos
            if isValid(self.epu_driver.gap_target):
                self.setParam(
                    _db.pv_gap_rb,
                    self.epu_driver.gap_target)
            if isValid(self.epu_driver.gap):
                self.setParam(
                    _db.pv_gap_mon,
                    self.epu_driver.gap)
            ## phase pos
            if isValid(self.epu_driver.phase_target):
                self.setParam(
                    _db.pv_phase_rb,
                    self.epu_driver.phase_target)
            if isValid(self.epu_driver.phase):
                self.setParam(
                    _db.pv_phase_mon,
                    self.epu_driver.phase)
            # update speed pvs
            ## gap target speed
            if isValid(self.epu_driver.gap_target_velocity):
                self.setParam(
                    _db.pv_gap_velo_rb,
                    self.epu_driver.gap_target_velocity)
            ## phase target speed
            if isValid(self.epu_driver.phase_target_velocity):
                self.setParam(
                    _db.pv_phase_velo_rb,
                    self.epu_driver.phase_target_velocity)
            ## individual axes target speed
            if isValid(self.epu_driver.a_target_velocity):
                self.setParam(
                    _db.pv_a_target_velo_mon,
                    self.epu_driver.a_target_velocity)
            if isValid(self.epu_driver.b_target_velocity):
                self.setParam(
                    _db.pv_b_target_velo_mon,
                    self.epu_driver.b_target_velocity)
            if isValid(self.epu_driver.s_target_velocity):
                self.setParam(
                    _db.pv_s_target_velo_mon,
                    self.epu_driver.s_target_velocity)
            if isValid(self.epu_driver.i_target_velocity):
                self.setParam(
                    _db.pv_i_target_velo_mon,
                    self.epu_driver.i_target_velocity)
            ## gap speed
            if isValid(self.epu_driver.gap):
                _time_now = time.time()
                _gap_now = self.epu_driver.gap
                self.setParam(
                    _db.pv_gap_velo_mon,
                    (_gap_now - self._old_gap) / (_time_now - self._old_gap_sample_timestamp))
                self._old_gap = _gap_now
                self._old_gap_sample_timestamp = _time_now
            ## phase speed
            if isValid(self.epu_driver.phase):
                _time_now = time.time()
                _phase_now = self.epu_driver.phase
                self.setParam(
                    _db.pv_phase_velo_mon,
                    (_phase_now - self._old_phase) / (_time_now - self._old_phase_sample_timestamp))
                self.old_phase = _phase_now
                self.old_phase_sample_timestamp = _time_now
            # update resolver readings
            if isValid(self.epu_driver.a_resolver_gap):
                self.setParam(
                    _db.pv_drive_a_resolver_pos_mon,
                    self.epu_driver.a_resolver_gap)
            if isValid(self.epu_driver.b_resolver_gap):
                self.setParam(
                    _db.pv_drive_b_resolver_pos_mon,
                    self.epu_driver.b_resolver_gap)
            if isValid(self.epu_driver.s_resolver_phase):
                self.setParam(
                    _db.pv_drive_s_resolver_pos_mon,
                    self.epu_driver.s_resolver_phase)
            if isValid(self.epu_driver.i_resolver_phase):
                self.setParam(
                    _db.pv_drive_i_resolver_pos_mon,
                    self.epu_driver.i_resolver_phase)
            # update enable and halt status
            if isValid(self.epu_driver.gap_enable):
                self.setParam(
                    _db.pv_enbl_ab_sts,
                    self.epu_driver.gap_enable)
            if isValid(self.epu_driver.phase_enable):
                self.setParam(
                    _db.pv_enbl_si_sts,
                    self.epu_driver.phase_enable)
            if isValid(self.epu_driver.gap_halt_released):
                self.setParam(
                    _db.pv_release_ab_sts,
                    self.epu_driver.gap_halt_released)
            if isValid(self.epu_driver.phase_halt_released):
                self.setParam(
                    _db.pv_release_si_sts,
                    self.epu_driver.phase_halt_released)
            if isValid(self.epu_driver.gap_enable_and_halt_released):
                self.setParam(
                    _db.pv_enbl_and_release_ab_sts,
                    self.epu_driver.gap_enable_and_halt_released)
            if isValid(self.epu_driver.phase_enable_and_halt_released):
                self.setParam(
                    _db.pv_enbl_and_release_si_sts,
                    self.epu_driver.phase_enable_and_halt_released)
            # update diagnostic codes
            if isValid(self.epu_driver.a_diag_code):
                self.setParam(
                    _db.pv_drive_a_diag_code_mon,
                    self.epu_driver.a_diag_code)
            if isValid(self.epu_driver.b_diag_code):
                self.setParam(
                    _db.pv_drive_b_diag_code_mon,
                    self.epu_driver.b_diag_code)
            if isValid(self.epu_driver.s_diag_code):
              self.setParam(
                    _db.pv_drive_s_diag_code_mon,
                    self.epu_driver.s_diag_code)
            if isValid(self.epu_driver.i_diag_code):
                self.setParam(
                    _db.pv_drive_i_diag_code_mon,
                    self.epu_driver.i_diag_code)
            # check overall fault state
            if (
                isValid(self.epu_driver.a_diag_code)
                and isValid(self.epu_driver.b_diag_code)
                and isValid(self.epu_driver.s_diag_code)
                and isValid(self.epu_driver.i_diag_code)
                ):
                not_ok = not (
                    self.epu_driver.a_diag_code == ' A211'
                    and self.epu_driver.b_diag_code == ' A211'
                    and self.epu_driver.b_diag_code == ' A211'
                    and self.epu_driver.b_diag_code == ' A211'
                    )
            else:
                not_ok = True
            self.setParam(
                _db.pv_status_mon,
                not_ok)
            # update moving status
            if isValid(self.epu_driver.a_is_moving):
                self.setParam(
                    _db.pv_drive_a_is_moving_mon,
                    self.epu_driver.a_is_moving)
            if isValid(self.epu_driver.b_is_moving):
                self.setParam(
                    _db.pv_drive_b_is_moving_mon,
                    self.epu_driver.b_is_moving)
            if isValid(self.epu_driver.s_is_moving):
                self.setParam(
                    _db.pv_drive_s_is_moving_mon,
                    self.epu_driver.s_is_moving)
            if isValid(self.epu_driver.i_is_moving):
                self.setParam(
                    _db.pv_drive_i_is_moving_mon,
                    self.epu_driver.i_is_moving)
            if isValid(self.epu_driver.is_moving):
                if self.epu_driver.is_moving:
                    self.setParam(
                        _db.pv_is_moving_mon,
                        _cte.bool_yes)
                else:
                    self.setParam(
                        _db.pv_is_moving_mon,
                        _cte.bool_no)
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
                self.setParam(_db.pv_beamline_enbl_sts, value)
                self.setParam(_db.pv_beamline_enbl_mon, value)
                self.updatePVs()
            else:
                status = False
        ## clear IOC log
        elif isPvName(reason, _db.pv_clear_log_cmd):
            # clear ioc msg
            self.setParam(_db.pv_ioc_msg_mon, _cte.msg_clear)
            # increment cmd pv
            self.incParam(_db.pv_clear_log_cmd)
            self.updatePVs()
        ## change gap set point
        if isPvName(reason, _db.pv_gap_sp):
            if (value >= _cte.minimum_gap
                    and value <= _cte.maximum_gap
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
            if (value >= _cte.minimum_phase
                    and value <= _cte.maximum_phase
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
            if (value > _cte.minimum_velo_mm_per_sec
                    and value <= _cte.maximum_velo_mm_per_sec
                    ):
                self.setParam(_db.pv_gap_max_velo_sp, value)
                self.setParam(_db.pv_gap_max_velo_rb, value)
                self.updatePVs()
            else:
                status = False
        ## change phase maximum velocity set point
        elif isPvName(reason, _db.pv_phase_max_velo_sp):
            if (value > _cte.minimum_velo_mm_per_sec
                    and value <= _cte.maximum_velo_mm_per_sec
                    ):
                self.setParam(_db.pv_phase_max_velo_sp, value)
                self.setParam(_db.pv_phase_max_velo_rb, value)
                self.updatePVs()
            else:
                status = False
        ## change gap velocity set point
        elif isPvName(reason, _db.pv_gap_velo_sp):
            soft_max_velo = self.getParam(_db.pv_gap_max_velo_sp)
            if (value > _cte.minimum_velo_mm_per_sec
                    and value <= _cte.maximum_velo_mm_per_sec
                    and value <= soft_max_velo
                    ):
                # convert velocity to mm/min
                _val_per_min = value * 60
                status = self.asynExec(
                    reason, self.epu_driver.gap_set_velocity, _val_per_min)
                if status:
                    self.setParam(_db.pv_gap_velo_sp, value)
                    self.updatePVs()
            else:
                status = False
        ## change phase velocity set point
        elif isPvName(reason, _db.pv_phase_velo_sp):
            soft_max_velo = self.getParam(_db.pv_phase_max_velo_sp)
            if (value > _cte.minimum_velo_mm_per_sec
                    and value <= _cte.maximum_velo_mm_per_sec
                    and value <= soft_max_velo
                    ):
                # convert velocity to mm/min
                _val_per_min = value * 60
                status = self.asynExec(
                    reason, self.epu_driver.phase_set_velocity, _val_per_min)
                if status:
                    self.setParam(_db.pv_phase_velo_sp, value)
                    self.updatePVs()
            else:
                status = False
        ## cmd to move and change gap
        elif isPvName(reason, _db.pv_change_gap_cmd):
            if _db.pv_allowed_change_gap_mon == _cte.bool_yes:
                status = self.asynExec(reason, self.epu_driver.gap_start)
                # increment cmd pv
                self.incParam(_db.pv_change_gap_cmd)
                self.updatePVs()
            else:
                status = False
        ## cmd to move and change phase
        elif isPvName(reason, _db.pv_change_phase_cmd):
            if _db.pv_allowed_change_phase_mon == _cte.bool_yes:
                status = self.asynExec(reason, self.epu_driver.phase_start)
                # increment cmd pv
                self.incParam(_db.pv_change_phase_cmd)
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
            and _db.pv_enbl_ab_sel == _cte.bool_yes):
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
            and _db.pv_enbl_si_sel == _cte.bool_yes):
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
            self.incParam(_db.pv_stop_cmd)
            # halt motor drives
            self.setParam(_db.pv_release_ab_sel, _cte.bool_no)
            self.setParam(_db.pv_release_si_sel, _cte.bool_no)
            # update pvs
            self.updatePVs()
        elif isPvName(reason, _db.pv_stop_ab_cmd):
            status = self.asynExec(reason, self.epu_driver.gap_stop)
            # increment cmd pv
            self.incParam(_db.pv_stop_ab_cmd)
            # halt motor drives
            self.setParam(_db.pv_release_ab_sel, _cte.bool_no)
            # update pvs
            self.updatePVs()
        elif isPvName(reason, _db.pv_stop_si_cmd):
            status = self.asynExec(reason, self.epu_driver.phase_stop)
            # increment cmd pv
            self.incParam(_db.pv_stop_si_cmd)
            # halt motor drives
            self.setParam(_db.pv_release_si_sel, _cte.bool_no)
            # update pvs
            self.updatePVs()
        ## cmd to turn on power of A and B drives
        elif isPvName(reason, _db.pv_enbl_pwr_ab_cmd):
            status = self.asynExec(reason, _cte.dummy)
            # increment cmd pv
            self.incParam(_db.pv_enbl_pwr_ab_cmd)
            # update pvs
            self.updatePVs()
        ## cmd to turn on power of S and I drives
        elif isPvName(reason, _db.pv_enbl_pwr_si_cmd):
            status = self.asynExec(reason, _cte.dummy)
            # increment cmd pv
            self.incParam(_db.pv_enbl_pwr_si_cmd)
            # update pvs
            self.updatePVs()
        ## cmd to turn on power of all drives
        elif isPvName(reason, _db.pv_enbl_pwr_all_cmd):
            status = self.asynExec(reason, _cte.dummy)
            # increment cmd pv
            self.incParam(_db.pv_enbl_pwr_all_cmd)
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
            self.setParam(_db.pv_is_busy_mon, _cte.bool_yes)
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
            self.setParam(_db.pv_is_busy_mon, _cte.bool_no)
            self.updatePVs()
            self.lock.release()
        if self.lock.acquire(blocking=False):
            tid = (
                threading.Thread(
                    target=execAndNotify,
                    args=(reason, func, *args),
                    kwargs=kwargs,
                    daemon=True
                )
            )
            tid.start()
            return True
        else:
            # inform that device is busy
            self.setParam(_db.pv_ioc_msg_mon, _cte.msg_device_busy)
            self.updatePVs()
            return False
