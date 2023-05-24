"""IOC driver module."""

import threading
import traceback
import time
import pcaspy

from . import constants as _cte
from . import epu_db as _db
from . import epu as _epu


class EPUSupport(pcaspy.Driver):
    """EPU device support for the pcaspy server."""

    def __init__(self, args):
        """."""
        self.args = args
        super(EPUSupport, self).__init__()

        # lock for critical operations
        self.lock = threading.Lock()
        # EPU driver will manage and control
        # main features of device operation
        try:
            self.epu_driver = _epu.Epu(
                args=args,
                callback_update=self.priority_call)
            print('Epu driver initialized')
        except Exception:
            print('Could not init epu driver')
            raise
        # start periodic polling function
        self.eid = threading.Event()
        self.init_vars()
        self.tid_periodic = threading.Thread(
            target=self.periodic, daemon=True
            )
        self.tid_periodic.start()

    def init_vars(self):
        """Variable initialization."""
        # auxiliary variables
        self._old_gap = self.epu_driver.gap
        self._old_gap_sample_timestamp = time.time()
        self._old_phase = self.epu_driver.phase
        self._old_phase_sample_timestamp = time.time()
        self._busy_counter = 0

        # init set point pv values
        self.setParam(
            _db.pv_gap_sp,
            self.epu_driver.gap_target
            )
        self.setParam(
            _db.pv_phase_sp,
            self.epu_driver.phase_target
            )
        self.setParam(
            _db.pv_gap_velo_sp,
            self.epu_driver.gap_target_velocity/60
            )
        self.setParam(
            _db.pv_phase_velo_sp,
            self.epu_driver.phase_target_velocity/60
            )
        self.setParam(
            _db.pv_enbl_ab_sel,
            self.epu_driver.gap_enable
            )
        self.setParam(
            _db.pv_enbl_si_sel,
            self.epu_driver.phase_enable
            )
        self.setParam(
            _db.pv_release_ab_sel,
            self.epu_driver.gap_halt_released
            )
        self.setParam(
            _db.pv_release_si_sel,
            self.epu_driver.phase_halt_released
            )
        self.setParam(
            _db.pv_enbl_and_release_ab_sel,
            self.epu_driver.gap_enable_and_halt_released
            )
        self.setParam(
            _db.pv_enbl_and_release_si_sel,
            self.epu_driver.phase_enable_and_halt_released
            )
        # update PVs
        self.updatePVs()

    def incParam(self, pv_name, inc=1):
        """Increment pv value."""
        _old_value = self.getParam(pv_name)
        self.setParam(pv_name, _old_value+inc)

    def priority_call(self):
        """Priority callback."""
        # update encoder readings
        self.setParam(
            _db.pv_gap_mon,
            self.epu_driver.gap
            )
        self.setParam(
            _db.pv_phase_mon,
            self.epu_driver.phase
            )
        # update PVs
        self.updatePVs()

    def periodic(self):
        """Periodic function."""
        while True:
            self.eid.wait(_cte.poll_interval)
            driver = self.epu_driver
            # update connection status
            if EPUSupport.isValid(driver.tcp_connected):
                self.setParam(
                    _db.pv_tcp_connected_mon,
                    driver.tcp_connected
                    )
            if EPUSupport.isValid(driver.gpio_connected):
                self.setParam(
                    _db.pv_gpio_connected_mon,
                    driver.gpio_connected
                    )
            if EPUSupport.isValid(driver.a_drive.rs485_connected):
                self.setParam(
                    _db.pv_drive_a_connected_mon,
                    driver.a_drive.rs485_connected
                    )
            if EPUSupport.isValid(driver.b_drive.rs485_connected):
                self.setParam(
                    _db.pv_drive_b_connected_mon,
                    driver.b_drive.rs485_connected
                    )
            if EPUSupport.isValid(driver.s_drive.rs485_connected):
                self.setParam(
                    _db.pv_drive_s_connected_mon,
                    driver.s_drive.rs485_connected
                    )
            if EPUSupport.isValid(driver.i_drive.rs485_connected):
                self.setParam(
                    _db.pv_drive_i_connected_mon,
                    driver.i_drive.rs485_connected
                    )
            if EPUSupport.isValid(driver.tcp_connected) \
                    and EPUSupport.isValid(driver.gpio_connected) \
                    and EPUSupport.isValid(driver.a_drive.rs485_connected) \
                    and EPUSupport.isValid(driver.b_drive.rs485_connected) \
                    and EPUSupport.isValid(driver.s_drive.rs485_connected) \
                    and EPUSupport.isValid(driver.i_drive.rs485_connected):
                if driver.tcp_connected \
                        and driver.gpio_connected \
                        and driver.a_drive.rs485_connected \
                        and driver.b_drive.rs485_connected \
                        and driver.s_drive.rs485_connected \
                        and driver.i_drive.rs485_connected:
                    self.setParam(
                        _db.pv_epu_connected_mon,
                        _cte.bool_yes
                    )
                else:
                    self.setParam(
                        _db.pv_epu_connected_mon,
                        _cte.bool_no
                    )
            else:
                self.setParam(
                    _db.pv_epu_connected_mon,
                    _cte.bool_no
                )
            # update allowed to move status
            if EPUSupport.isValid(driver.gap_change_allowed) \
                    and driver.gap_change_allowed:
                self.setParam(
                    _db.pv_allowed_change_gap_mon,
                    _cte.bool_yes)
            else:
                self.setParam(
                    _db.pv_allowed_change_gap_mon,
                    _cte.bool_no
                    )
            if EPUSupport.isValid(driver.phase_change_allowed) \
                    and driver.phase_change_allowed:
                self.setParam(
                    _db.pv_allowed_change_phase_mon,
                    _cte.bool_yes)
            else:
                self.setParam(
                    _db.pv_allowed_change_phase_mon,
                    _cte.bool_no)

            # --- update combined position pvs

            # gap pos
            if EPUSupport.isValid(driver.gap_target):
                self.setParam(
                    _db.pv_gap_rb,
                    driver.gap_target
                    )

            # gap updates only by callback during motion
            if not driver.gap_is_moving:
                if EPUSupport.isValid(driver.gap):
                    self.setParam(
                        _db.pv_gap_mon,
                        driver.gap
                        )

            # phase pos
            if EPUSupport.isValid(driver.phase_target):
                self.setParam(
                    _db.pv_phase_rb,
                    driver.phase_target
                    )

            # phase updates only by callback during motion
            if not driver.phase_is_moving:
                if EPUSupport.isValid(driver.phase):
                    self.setParam(
                        _db.pv_phase_mon,
                        driver.phase
                        )

            # --- update speed pvs

            # gap target speed
            if EPUSupport.isValid(driver.gap_target_velocity):
                self.setParam(
                    _db.pv_gap_velo_rb,
                    driver.gap_target_velocity/60
                    )
            # phase target speed
            if EPUSupport.isValid(driver.phase_target_velocity):
                self.setParam(
                    _db.pv_phase_velo_rb,
                    driver.phase_target_velocity/60
                    )
            # individual axes target speed
            if EPUSupport.isValid(driver.a_target_velocity):
                self.setParam(
                    _db.pv_a_target_velo_mon,
                    driver.a_target_velocity/60
                    )
            if EPUSupport.isValid(driver.b_target_velocity):
                self.setParam(
                    _db.pv_b_target_velo_mon,
                    driver.b_target_velocity/60
                    )
            if EPUSupport.isValid(driver.s_target_velocity):
                self.setParam(
                    _db.pv_s_target_velo_mon,
                    driver.s_target_velocity/60
                    )
            if EPUSupport.isValid(driver.i_target_velocity):
                self.setParam(
                    _db.pv_i_target_velo_mon,
                    driver.i_target_velocity/60
                    )
            # gap speed
            if EPUSupport.isValid(driver.gap):
                _time_now = time.time()
                _gap_now = driver.gap
                self.setParam(
                    _db.pv_gap_velo_mon,
                    (_gap_now - self._old_gap)
                    / (_time_now - self._old_gap_sample_timestamp)
                    )
                self._old_gap = _gap_now
                self._old_gap_sample_timestamp = _time_now
            # phase speed
            if EPUSupport.isValid(driver.phase):
                _time_now = time.time()
                _phase_now = driver.phase
                self.setParam(
                    _db.pv_phase_velo_mon,
                    (_phase_now - self._old_phase)
                    / (_time_now - self._old_phase_sample_timestamp)
                    )
                self.old_phase = _phase_now
                self.old_phase_sample_timestamp = _time_now
            # update resolver readings
            if EPUSupport.isValid(driver.a_resolver_gap):
                self.setParam(
                    _db.pv_drive_a_resolver_pos_mon,
                    driver.a_resolver_gap
                    )
            if EPUSupport.isValid(driver.b_resolver_gap):
                self.setParam(
                    _db.pv_drive_b_resolver_pos_mon,
                    driver.b_resolver_gap
                    )
            if EPUSupport.isValid(driver.s_resolver_phase):
                self.setParam(
                    _db.pv_drive_s_resolver_pos_mon,
                    driver.s_resolver_phase
                    )
            if EPUSupport.isValid(driver.i_resolver_phase):
                self.setParam(
                    _db.pv_drive_i_resolver_pos_mon,
                    driver.i_resolver_phase
                    )
            # update encoder readings
            if EPUSupport.isValid(driver.a_encoder_gap):
                self.setParam(
                    _db.pv_drive_a_encoder_pos_mon,
                    driver.a_encoder_gap
                    )
            if EPUSupport.isValid(driver.b_encoder_gap):
                self.setParam(
                    _db.pv_drive_b_encoder_pos_mon,
                    driver.b_encoder_gap
                    )
            if EPUSupport.isValid(driver.s_encoder_phase):
                self.setParam(
                    _db.pv_drive_s_encoder_pos_mon,
                    driver.s_encoder_phase
                    )
            if EPUSupport.isValid(driver.i_encoder_phase):
                self.setParam(
                    _db.pv_drive_i_encoder_pos_mon,
                    driver.i_encoder_phase
                    )
            # update enable and halt status
            if EPUSupport.isValid(driver.gap_enable):
                self.setParam(
                    _db.pv_enbl_ab_sts,
                    driver.gap_enable
                    )
            if EPUSupport.isValid(driver.phase_enable):
                self.setParam(
                    _db.pv_enbl_si_sts,
                    driver.phase_enable
                    )
            if EPUSupport.isValid(driver.gap_halt_released):
                self.setParam(
                    _db.pv_release_ab_sts,
                    driver.gap_halt_released
                    )
            if EPUSupport.isValid(driver.phase_halt_released):
                self.setParam(
                    _db.pv_release_si_sts,
                    driver.phase_halt_released
                    )
            if EPUSupport.isValid(driver.gap_enable_and_halt_released):
                self.setParam(
                    _db.pv_enbl_and_release_ab_sts,
                    driver.gap_enable_and_halt_released
                    )
            if EPUSupport.isValid(driver.phase_enable_and_halt_released):
                self.setParam(
                    _db.pv_enbl_and_release_si_sts,
                    driver.phase_enable_and_halt_released
                    )
            # update diagnostic codes and messages
            if EPUSupport.isValid(driver.a_diag_code):
                self.setParam(
                    _db.pv_drive_a_diag_code_mon,
                    driver.a_diag_code
                    )
                self.setParam(
                    _db.pv_drive_a_diag_msg_mon,
                    _cte.drive_diag_msgs.get(
                        driver.a_diag_code,
                        _cte.default_unknown_diag_msg
                        )
                    )
            if EPUSupport.isValid(driver.b_diag_code):
                self.setParam(
                    _db.pv_drive_b_diag_code_mon,
                    driver.b_diag_code
                    )
                self.setParam(
                    _db.pv_drive_b_diag_msg_mon,
                    _cte.drive_diag_msgs.get(
                        driver.b_diag_code,
                        _cte.default_unknown_diag_msg
                        )
                    )
            if EPUSupport.isValid(driver.s_diag_code):
                self.setParam(
                    _db.pv_drive_s_diag_code_mon,
                    driver.s_diag_code
                    )
                self.setParam(
                    _db.pv_drive_s_diag_msg_mon,
                    _cte.drive_diag_msgs.get(
                        driver.s_diag_code,
                        _cte.default_unknown_diag_msg
                        )
                    )
            if EPUSupport.isValid(driver.i_diag_code):
                self.setParam(
                    _db.pv_drive_i_diag_code_mon,
                    driver.i_diag_code
                    )
                self.setParam(
                    _db.pv_drive_i_diag_msg_mon,
                    _cte.drive_diag_msgs.get(
                        driver.i_diag_code,
                        _cte.default_unknown_diag_msg
                        )
                    )
            # check overall fault state
            ## gap
            if (
                    EPUSupport.isValid(driver.a_diag_code)
                    and EPUSupport.isValid(driver.b_diag_code)
            ):
                gap_not_ok = not (
                    driver.a_diag_code in _cte.operational_diag_codes
                    and driver.b_diag_code in _cte.operational_diag_codes
                    )
            else:
                gap_not_ok = True
            self.setParam(_db.pv_gap_status_mon, gap_not_ok)
            ## phase
            if (
                    EPUSupport.isValid(driver.s_diag_code)
                    and EPUSupport.isValid(driver.i_diag_code)
            ):
                phase_not_ok = not (
                    driver.s_diag_code in _cte.operational_diag_codes
                    and driver.i_diag_code in _cte.operational_diag_codes
                    )
            else:
                phase_not_ok = True
            self.setParam(_db.pv_status_mon, phase_not_ok)
            ## both
            not_ok = gap_not_ok or phase_not_ok
            self.setParam(_db.pv_status_mon, not_ok)
            # check if drives are powered on
            if (
                    EPUSupport.isValid(driver.a_diag_code)
                    and EPUSupport.isValid(driver.b_diag_code)
                    and driver.a_diag_code in _cte.powered_on_diag_codes
                    and driver.b_diag_code in _cte.powered_on_diag_codes
            ):
                self.setParam(
                    _db.pv_pwr_ab_mon,
                    _cte.bool_yes
                    )
            else:
                self.setParam(
                    _db.pv_pwr_ab_mon,
                    _cte.bool_no
                    )
            if (
                    EPUSupport.isValid(driver.s_diag_code)
                    and EPUSupport.isValid(driver.i_diag_code)
                    and driver.s_diag_code in _cte.powered_on_diag_codes
                    and driver.i_diag_code in _cte.powered_on_diag_codes
            ):
                self.setParam(
                    _db.pv_pwr_si_mon,
                    _cte.bool_yes
                    )
            else:
                self.setParam(
                    _db.pv_pwr_si_mon,
                    _cte.bool_no
                    )
            # update moving status
            if EPUSupport.isValid(driver.gap_is_moving):
                self.setParam(
                    _db.pv_drive_a_is_moving_mon,
                    driver.gap_is_moving
                    )
                self.setParam(
                    _db.pv_drive_b_is_moving_mon,
                    driver.gap_is_moving
                    )
            if EPUSupport.isValid(driver.phase_is_moving):
                self.setParam(
                    _db.pv_drive_s_is_moving_mon,
                    driver.phase_is_moving
                    )
                self.setParam(
                    _db.pv_drive_i_is_moving_mon,
                    driver.phase_is_moving
                    )
            if (
                    EPUSupport.isValid(driver.gap_is_moving)
                    and EPUSupport.isValid(driver.phase_is_moving)
            ):
                if driver.gap_is_moving or driver.phase_is_moving:
                    self.setParam(
                        _db.pv_is_moving_mon,
                        _cte.bool_yes
                        )
                else:
                    self.setParam(
                        _db.pv_is_moving_mon,
                        _cte.bool_no
                        )
            # update read-only PVs
            self.updatePVs()

    def write(self, reason, value):
        """EPICS write."""
        status = True
        driver = self.epu_driver

        # ---take action according to PV name

        # enable control from beamlines
        if EPUSupport.isPvName(reason, _db.pv_beamline_enbl_sel):
            if EPUSupport.isBoolNum(value):
                self.setParam(_db.pv_beamline_enbl_sel, value)
                self.setParam(_db.pv_beamline_enbl_sts, value)
                self.setParam(_db.pv_beamline_enbl_mon, value)
                self.updatePVs()
            else:
                status = False

        # clear IOC log
        elif EPUSupport.isPvName(reason, _db.pv_clear_log_cmd):
            # clear ioc msg
            self.setParam(_db.pv_ioc_msg_mon, _cte.msg_clear)
            # increment cmd pv
            self.incParam(_db.pv_clear_log_cmd)
            self.updatePVs()

        # clear drive errors
        elif EPUSupport.isPvName(reason, _db.pv_clear_error_cmd):
            # clear driver errors
            status = self.asynExec(reason, driver.a_drive.clear_error)
            status = self.asynExec(reason, driver.b_drive.clear_error)
            status = self.asynExec(reason, driver.s_drive.clear_error)
            status = self.asynExec(reason, driver.i_drive.clear_error)
            # increment cmd pv
            self.incParam(_db.pv_clear_error_cmd)
            self.updatePVs()

        # change gap set point
        if EPUSupport.isPvName(reason, _db.pv_gap_sp):
            if (value >= _cte.minimum_gap
                    and value <= _cte.maximum_gap):
                status = self.asynExec(
                    reason, driver.gap_set, value)
                if status:
                    self.setParam(_db.pv_gap_sp, value)
                    self.updatePVs()
            else:
                status = False

        # change phase set point
        elif EPUSupport.isPvName(reason, _db.pv_phase_sp):
            if (value >= _cte.minimum_phase
                    and value <= _cte.maximum_phase):
                status = self.asynExec(
                    reason, driver.phase_set, value)
                if status:
                    self.setParam(_db.pv_phase_sp, value)
                    self.updatePVs()
            else:
                status = False

        # change gap maximum velocity set point
        elif EPUSupport.isPvName(reason, _db.pv_gap_max_velo_sp):
            if (value > _cte.minimum_velo_mm_per_sec
                    and value <= _cte.maximum_velo_mm_per_sec):
                self.setParam(_db.pv_gap_max_velo_sp, value)
                self.setParam(_db.pv_gap_max_velo_rb, value)
                if value < self.getParam(_db.pv_gap_velo_sp):
                    _val_per_min = value * 60
                    status = self.asynExec(
                        reason, driver.gap_set_velocity, _val_per_min)
                    if status:
                        self.setParam(_db.pv_gap_velo_sp, value)
                self.updatePVs()
            else:
                status = False

        # change phase maximum velocity set point
        elif EPUSupport.isPvName(reason, _db.pv_phase_max_velo_sp):
            if (value > _cte.minimum_velo_mm_per_sec
                    and value <= _cte.maximum_velo_mm_per_sec):
                self.setParam(_db.pv_phase_max_velo_sp, value)
                self.setParam(_db.pv_phase_max_velo_rb, value)
                if value < self.getParam(_db.pv_phase_velo_sp):
                    _val_per_min = value * 60
                    status = self.asynExec(
                        reason, driver.phase_set_velocity, _val_per_min)
                    if status:
                        self.setParam(_db.pv_phase_velo_sp, value)
                self.updatePVs()
            else:
                status = False

        # change gap velocity set point
        elif EPUSupport.isPvName(reason, _db.pv_gap_velo_sp):
            soft_max_velo = self.getParam(_db.pv_gap_max_velo_sp)
            if (value > _cte.minimum_velo_mm_per_sec
                    and value <= _cte.maximum_velo_mm_per_sec
                    and value <= soft_max_velo):
                # convert velocity to mm/min
                _val_per_min = value * 60
                status = self.asynExec(
                    reason, driver.gap_set_velocity, _val_per_min)
                if status:
                    self.setParam(_db.pv_gap_velo_sp, value)
                    self.updatePVs()
            else:
                status = False

        # change phase velocity set point
        elif EPUSupport.isPvName(reason, _db.pv_phase_velo_sp):
            soft_max_velo = self.getParam(_db.pv_phase_max_velo_sp)
            if (value > _cte.minimum_velo_mm_per_sec
                    and value <= _cte.maximum_velo_mm_per_sec
                    and value <= soft_max_velo):
                # convert velocity to mm/min
                _val_per_min = value * 60
                status = self.asynExec(
                    reason, driver.phase_set_velocity, _val_per_min)
                if status:
                    self.setParam(_db.pv_phase_velo_sp, value)
                    self.updatePVs()
            else:
                status = False

        # cmd to move and change gap
        elif EPUSupport.isPvName(reason, _db.pv_change_gap_cmd):
            if (not driver.gap_is_moving and
                    self.getParam(_db.pv_allowed_change_gap_mon) == _cte.bool_yes):
                status = self.asynExec(
                    reason, driver.gap_start, _cte.bool_yes
                    )
                # increment cmd pv
                self.incParam(_db.pv_change_gap_cmd)
                self.updatePVs()
            else:
                status = False

        # cmd to move and change phase
        elif EPUSupport.isPvName(reason, _db.pv_change_phase_cmd):
            if (not driver.phase_is_moving and
                    self.getParam(_db.pv_allowed_change_phase_mon) == _cte.bool_yes):
                status = self.asynExec(
                    reason, driver.phase_start, _cte.bool_yes
                    )
                # increment cmd pv
                self.incParam(_db.pv_change_phase_cmd)
                self.updatePVs()
            else:
                status = False

        # select to enable/disable A and B drives
        elif EPUSupport.isPvName(reason, _db.pv_enbl_ab_sel):
            if EPUSupport.isBoolNum(value):
                status = self.asynExec(
                    reason, driver.gap_set_enable, bool(value))
                if status:
                    self.setParam(_db.pv_enbl_ab_sel, value)
                    self.updatePVs()
            else:
                status = False

        # select to enable/disable S and I drives
        elif EPUSupport.isPvName(reason, _db.pv_enbl_si_sel):
            if EPUSupport.isBoolNum(value):
                status = self.asynExec(
                    reason, driver.phase_set_enable, bool(value))
                if status:
                    self.setParam(_db.pv_enbl_si_sel, value)
                    self.updatePVs()
            else:
                status = False

        # select to release/halt A and B drives
        elif EPUSupport.isPvName(reason, _db.pv_release_ab_sel):
            if EPUSupport.isBoolNum(value):
                status = self.asynExec(
                    reason, driver.gap_release_halt, bool(value))
                if status:
                    self.setParam(_db.pv_release_ab_sel, value)
                    self.updatePVs()
            else:
                status = False

        # select to release/halt S and I drives
        elif EPUSupport.isPvName(reason, _db.pv_release_si_sel):
            if EPUSupport.isBoolNum(value):
                status = self.asynExec(
                    reason, driver.phase_release_halt, bool(value))
                if status:
                    self.setParam(_db.pv_release_si_sel, value)
                    self.updatePVs()
            else:
                status = False

        # cmd to enable and release A and B drives
        elif EPUSupport.isPvName(reason, _db.pv_enbl_and_release_ab_sel):
            if EPUSupport.isBoolNum(value):
                status = self.asynExec(
                    reason, driver.gap_enable_and_release_halt, bool(value))
                if status:
                    # update enbl and release pvs
                    self.setParam(_db.pv_enbl_ab_sel, value)
                    self.setParam(_db.pv_release_ab_sel, value)
                    # update pv
                    self.setParam(_db.pv_enbl_and_release_ab_sel, value)
                    self.updatePVs()
            else:
                status = False

        # cmd to enable and release S and I drives
        elif EPUSupport.isPvName(reason, _db.pv_enbl_and_release_si_sel):
            if EPUSupport.isBoolNum(value):
                status = self.asynExec(
                    reason, driver.phase_enable_and_release_halt,
                    bool(value)
                    )
                if status:
                    # update enbl and release pvs
                    self.setParam(_db.pv_enbl_si_sel, value)
                    self.setParam(_db.pv_release_si_sel, value)
                    # update pv
                    self.setParam(_db.pv_enbl_and_release_si_sel, value)
                    self.updatePVs()
            else:
                status = False
        elif EPUSupport.isPvName(reason, _db.pv_stop_cmd):
            status = self.asynExec(reason, driver.stop_all)
            # increment cmd pv
            self.incParam(_db.pv_stop_cmd)
            # halt motor drives
            self.setParam(_db.pv_release_ab_sel, _cte.bool_no)
            self.setParam(_db.pv_release_si_sel, _cte.bool_no)
            # update pvs
            self.updatePVs()
        elif EPUSupport.isPvName(reason, _db.pv_stop_ab_cmd):
            status = self.asynExec(reason, driver.gap_stop)
            # increment cmd pv
            self.incParam(_db.pv_stop_ab_cmd)
            # halt motor drives
            self.setParam(_db.pv_release_ab_sel, _cte.bool_no)
            # update pvs
            self.updatePVs()
        elif EPUSupport.isPvName(reason, _db.pv_stop_si_cmd):
            status = self.asynExec(reason, driver.phase_stop)
            # increment cmd pv
            self.incParam(_db.pv_stop_si_cmd)
            # halt motor drives
            self.setParam(_db.pv_release_si_sel, _cte.bool_no)
            # update pvs
            self.updatePVs()

        # cmd to turn on power of A and B drives
        elif EPUSupport.isPvName(reason, _db.pv_enbl_pwr_ab_cmd):
            status = self.asynExec(reason, driver.gap_turn_on)
            # increment cmd pv
            self.incParam(_db.pv_enbl_pwr_ab_cmd)
            # update pvs
            self.updatePVs()

        # cmd to turn on power of S and I drives
        elif EPUSupport.isPvName(reason, _db.pv_enbl_pwr_si_cmd):
            status = self.asynExec(reason, driver.phase_turn_on)
            # increment cmd pv
            self.incParam(_db.pv_enbl_pwr_si_cmd)
            # update pvs
            self.updatePVs()

        # cmd to turn on power of all drives
        elif EPUSupport.isPvName(reason, _db.pv_enbl_pwr_all_cmd):
            status = self.asynExec(reason, driver.turn_on_all)
            # increment cmd pv
            self.incParam(_db.pv_enbl_pwr_all_cmd)
            # update pvs
            self.updatePVs()

        # no match to pv names
        else:
            status = False
        # end of write
        return status

    def asynExec(self, reason, func, *args, **kwargs):
        """Call function in new thread and send callback for pv specified by reason."""
        def execAndNotify(reason, func, *args, **kwargs):
            """ Call function and then callback after completion
            """
            # set busy status
            self._busy_counter += 1
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
            self._busy_counter -= 1
            if self._busy_counter == 0:
                self.setParam(_db.pv_is_busy_mon, _cte.bool_no)
            self.updatePVs()
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

    def asynExecWithLock(self, reason, func, *args, **kwargs):
        """Call function in new thread, using lock, and send callback for pv specified by reason."""
        def execNotifyAndUnlock(reason, func, *args, **kwargs):
            """ Call function and then callback after completion
            """
            # set busy status
            self._busy_counter += 1
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
            self._busy_counter -= 1
            if self._busy_counter == 0:
                self.setParam(_db.pv_is_busy_mon, _cte.bool_no)
            self.updatePVs()
            self.lock.release()
        if self.lock.acquire(blocking=False):
            tid = (
                threading.Thread(
                    target=execNotifyAndUnlock,
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

    @staticmethod
    def isPvName(reason, pvname):
        """ This function is a wrapper to allow
            scripts to inspect this source code
            for the PV names being used
        """
        return reason == pvname

    @staticmethod
    def isBoolNum(value):
        """ This function checks if an integer
            value could represent a bool, i.e.,
            if it is 0 or 1
        """
        return value in (0, 1)

    @staticmethod
    def isValid(value):
        """Checks if a given parameter is valid as a PV value."""
        return value is not None

    @staticmethod
    def inTolerance(value1, value2, tol):
        """Check if given parameter is within tolerance."""
        return abs(value1 - value2) <= tol
