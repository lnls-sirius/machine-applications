import constants
from pcaspy import Severity as _Severity

# prefix
pv_prefix = constants.pv_prefix

#############################################
# Map variable -> pv name
## general
pv_is_busy_mon = 'IsBusy-Mon'
pv_ioc_msg_mon = 'Log-Mon'
pv_gap_sp = 'Gap-SP'
pv_gap_rb = 'Gap-RB'
pv_gap_mon = 'Gap-Mon'
pv_phase_sp = 'Phase-SP'
pv_phase_rb = 'Phase-RB'
pv_phase_mon = 'Phase-Mon'
pv_gap_velo_mon = 'GapSpeed-Mon'
pv_phase_velo_mon = 'PhaseSpeed-Mon'
pv_allowed_change_gap_mon = 'AllowedToChangeGap-Mon'
pv_allowed_change_phase_mon = 'AllowedToChangePhase-Mon'
pv_change_gap_cmd = 'ChangeGap-Cmd'
pv_change_phase_cmd = 'ChangePhase-Cmd'
pv_enbl_ab_sel = 'EnblAB-Sel'
pv_enbl_ab_sts = 'EnblAB-Sts'
pv_enbl_si_sel = 'EnblSI-Sel'
pv_enbl_si_sts = 'EnblSI-Sts'
pv_release_ab_sel = 'ReleaseAB-Sel'
pv_release_ab_sts = 'ReleaseAB-Sts'
pv_release_si_sel = 'ReleaseSI-Sel'
pv_release_si_sts = 'ReleaseSI-Sts'
pv_enbl_and_release_ab_sel = 'EnblAndReleaseAB-Sel'
pv_enbl_and_release_si_sel = 'EnblAndReleaseSI-Sel'
pv_enbl_and_release_ab_sts = 'EnblAndReleaseAB-Sts'
pv_enbl_and_release_si_sts = 'EnblAndReleaseSI-Sts'
pv_is_moving_mon = 'Moving-Mon'
pv_stop_cmd = 'Stop-Cmd'
## drive A
pv_drive_a_resolver_pos_mon = 'DriveAResolverPos-Mon'
pv_drive_a_encoder_pos_mon = 'DriveAEncoderPos-Mon'
pv_drive_a_velo_mon = 'DriveASpeed-Mon'
pv_drive_a_diag_code_mon = 'DriveADiagCode-Mon'
pv_drive_a_diag_msg_mon = 'DriveADiagMsg-Mon'
pv_drive_a_is_moving_mon = 'DriveAMoving-Mon'
## drive B
pv_drive_b_resolver_pos_mon = 'DriveBResolverPos-Mon'
pv_drive_b_encoder_pos_mon = 'DriveBEncoderPos-Mon'
pv_drive_b_velo_mon = 'DriveBSpeed-Mon'
pv_drive_b_diag_code_mon = 'DriveBDiagCode-Mon'
pv_drive_b_diag_msg_mon = 'DriveBDiagMsg-Mon'
pv_drive_b_is_moving_mon = 'DriveBMoving-Mon'
## drive S
pv_drive_s_resolver_pos_mon = 'DriveSResolverPos-Mon'
pv_drive_s_encoder_pos_mon = 'DriveSEncoderPos-Mon'
pv_drive_s_velo_mon = 'DriveSSpeed-Mon'
pv_drive_s_diag_code_mon = 'DriveSDiagCode-Mon'
pv_drive_s_diag_msg_mon = 'DriveSDiagMsg-Mon'
pv_drive_s_is_moving_mon = 'DriveSMoving-Mon'
## drive I
pv_drive_i_resolver_pos_mon = 'DriveIResolverPos-Mon'
pv_drive_i_encoder_pos_mon = 'DriveIEncoderPos-Mon'
pv_drive_i_velo_mon = 'DriveISpeed-Mon'
pv_drive_i_diag_code_mon = 'DriveIDiagCode-Mon'
pv_drive_i_diag_msg_mon = 'DriveIDiagMsg-Mon'
pv_drive_i_is_moving_mon = 'DriveIMoving-Mon'

#############################################
# Database
pvdb = {
    #############################################
    # General
    pv_is_busy_mon : {
        'type' : 'enum',
        'count' : 1,
        'enums' : constants.bool_enums,
        'states' : [_Severity.NO_ALARM, _Severity.NO_ALARM],
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_ioc_msg_mon : {
        'type' : 'char',
        'count' : constants.max_long_msg_size,
        'mdel' : -1,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_gap_sp : {
        'type' : 'float',
        'prec' : constants.position_precision,
        'count' : 1,
        'unit' : constants.position_units,
        'mdel' : -1,
        'asyn' : True,
        'asg' : 'default',
    },
    pv_gap_rb : {
        'type' : 'float',
        'prec' : constants.position_precision,
        'count' : 1,
        'unit' : constants.position_units,
        'mdel' : -1,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_gap_mon : {
        'type' : 'float',
        'prec' : constants.position_precision,
        'count' : 1,
        'unit' : constants.position_units,
        'mdel' : -1,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_phase_sp : {
        'type' : 'float',
        'prec' : constants.position_precision,
        'count' : 1,
        'unit' : constants.position_units,
        'mdel' : -1,
        'asyn' : True,
        'asg' : 'default',
    },
    pv_phase_rb : {
        'type' : 'float',
        'prec' : constants.position_precision,
        'count' : 1,
        'unit' : constants.position_units,
        'mdel' : -1,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_phase_mon : {
        'type' : 'float',
        'prec' : constants.position_precision,
        'count' : 1,
        'unit' : constants.position_units,
        'mdel' : -1,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_gap_velo_mon : {
        'type' : 'float',
        'prec' : constants.position_precision,
        'count' : 1,
        'unit' : constants.velo_units,
        'mdel' : -1,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_phase_velo_mon : {
        'type' : 'float',
        'prec' : constants.position_precision,
        'count' : 1,
        'unit' : constants.velo_units,
        'mdel' : -1,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_allowed_change_gap_mon : {
        'type' : 'enum',
        'count' : 1,
        'enums' : constants.bool_enums,
        'states' : [_Severity.NO_ALARM, _Severity.NO_ALARM],
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_allowed_change_phase_mon : {
        'type' : 'enum',
        'count' : 1,
        'enums' : constants.bool_enums,
        'states' : [_Severity.NO_ALARM, _Severity.NO_ALARM],
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_change_gap_cmd : {
        'type' : 'int',
        'count' : 1,
        'mdel' : -1,
        'asyn' : True,
        'asg' : 'default',
        'value' : 0,
    },
    pv_change_phase_cmd : {
        'type' : 'int',
        'count' : 1,
        'mdel' : -1,
        'asyn' : True,
        'asg' : 'default',
        'value' : 0,
    },
    pv_enbl_ab_sel : {
        'type' : 'enum',
        'count' : 1,
        'enums' : constants.bool_enums,
        'states' : [_Severity.NO_ALARM, _Severity.NO_ALARM],
        'mdel' : -1,
        'asyn' : True,
        'asg' : 'default',
    },
    pv_enbl_ab_sts : {
        'type' : 'enum',
        'count' : 1,
        'enums' : constants.bool_enums,
        'states' : [_Severity.NO_ALARM, _Severity.NO_ALARM],
        'mdel' : -1,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_enbl_si_sel : {
        'type' : 'enum',
        'count' : 1,
        'enums' : constants.bool_enums,
        'states' : [_Severity.NO_ALARM, _Severity.NO_ALARM],
        'mdel' : -1,
        'asyn' : True,
        'asg' : 'default',
    },
    pv_enbl_si_sts : {
        'type' : 'enum',
        'count' : 1,
        'enums' : constants.bool_enums,
        'states' : [_Severity.NO_ALARM, _Severity.NO_ALARM],
        'mdel' : -1,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_release_ab_sel : {
        'type' : 'enum',
        'count' : 1,
        'enums' : constants.bool_enums,
        'states' : [_Severity.NO_ALARM, _Severity.NO_ALARM],
        'mdel' : -1,
        'asyn' : True,
        'asg' : 'default',
    },
    pv_release_ab_sts : {
        'type' : 'enum',
        'count' : 1,
        'enums' : constants.bool_enums,
        'states' : [_Severity.NO_ALARM, _Severity.NO_ALARM],
        'mdel' : -1,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_release_si_sel : {
        'type' : 'enum',
        'count' : 1,
        'enums' : constants.bool_enums,
        'states' : [_Severity.NO_ALARM, _Severity.NO_ALARM],
        'mdel' : -1,
        'asyn' : True,
        'asg' : 'default',
    },
    pv_release_si_sts : {
        'type' : 'enum',
        'count' : 1,
        'enums' : constants.bool_enums,
        'states' : [_Severity.NO_ALARM, _Severity.NO_ALARM],
        'mdel' : -1,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_enbl_and_release_ab_sel : {
        'type' : 'enum',
        'count' : 1,
        'enums' : constants.bool_enums,
        'states' : [_Severity.NO_ALARM, _Severity.NO_ALARM],
        'mdel' : -1,
        'asyn' : True,
        'asg' : 'default',
    },
    pv_enbl_and_release_si_sel : {
        'type' : 'enum',
        'count' : 1,
        'enums' : constants.bool_enums,
        'states' : [_Severity.NO_ALARM, _Severity.NO_ALARM],
        'mdel' : -1,
        'asyn' : True,
        'asg' : 'default',
    },
    pv_enbl_and_release_ab_sts : {
        'type' : 'enum',
        'count' : 1,
        'enums' : constants.bool_enums,
        'states' : [_Severity.NO_ALARM, _Severity.NO_ALARM],
        'mdel' : -1,
        'asyn' : False,
        'asg' : 'default',
    },
    pv_enbl_and_release_si_sts : {
        'type' : 'enum',
        'count' : 1,
        'enums' : constants.bool_enums,
        'states' : [_Severity.NO_ALARM, _Severity.NO_ALARM],
        'mdel' : -1,
        'asyn' : False,
        'asg' : 'default',
    },
    pv_stop_cmd : {
        'type' : 'int',
        'count' : 1,
        'mdel' : -1,
        'asyn' : True,
        'asg' : 'default',
        'value' : 0,
    },
    #############################################
    # Drive A
    pv_drive_a_resolver_pos_mon : {
        'type' : 'float',
        'prec' : constants.position_precision,
        'count' : 1,
        'unit' : constants.position_units,
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_drive_a_encoder_pos_mon : {
        'type' : 'float',
        'prec' : constants.position_precision,
        'count' : 1,
        'unit' : constants.position_units,
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_drive_a_velo_mon : {
        'type' : 'float',
        'prec' : constants.position_precision,
        'count' : 1,
        'unit' : constants.velo_units,
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_drive_a_diag_code_mon : {
        'type' : 'int',
        'count' : 1,
        'unit' : constants.no_units,
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_drive_a_diag_msg_mon : {
        'type' : 'char',
        'count' : constants.max_msg_size,
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_drive_a_is_moving_mon : {
        'type' : 'enum',
        'count' : 1,
        'enums' : constants.bool_enums,
        'states' : [_Severity.NO_ALARM, _Severity.NO_ALARM],
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    #############################################
    # Drive B
    pv_drive_b_resolver_pos_mon : {
        'type' : 'float',
        'prec' : constants.position_precision,
        'count' : 1,
        'unit' : constants.position_units,
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_drive_b_encoder_pos_mon : {
        'type' : 'float',
        'prec' : constants.position_precision,
        'count' : 1,
        'unit' : constants.position_units,
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_drive_b_velo_mon : {
        'type' : 'float',
        'prec' : constants.position_precision,
        'count' : 1,
        'unit' : constants.velo_units,
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_drive_b_diag_code_mon : {
        'type' : 'int',
        'count' : 1,
        'unit' : constants.no_units,
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_drive_b_diag_msg_mon : {
        'type' : 'char',
        'count' : constants.max_msg_size,
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_drive_b_is_moving_mon : {
        'type' : 'enum',
        'count' : 1,
        'enums' : constants.bool_enums,
        'states' : [_Severity.NO_ALARM, _Severity.NO_ALARM],
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    #############################################
    # Drive S
    pv_drive_s_resolver_pos_mon : {
        'type' : 'float',
        'prec' : constants.position_precision,
        'count' : 1,
        'unit' : constants.position_units,
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_drive_s_encoder_pos_mon : {
        'type' : 'float',
        'prec' : constants.position_precision,
        'count' : 1,
        'unit' : constants.position_units,
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_drive_s_velo_mon : {
        'type' : 'float',
        'prec' : constants.position_precision,
        'count' : 1,
        'unit' : constants.velo_units,
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_drive_s_diag_code_mon : {
        'type' : 'int',
        'count' : 1,
        'unit' : constants.no_units,
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_drive_s_diag_msg_mon : {
        'type' : 'char',
        'count' : constants.max_msg_size,
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_drive_s_is_moving_mon : {
        'type' : 'enum',
        'count' : 1,
        'enums' : constants.bool_enums,
        'states' : [_Severity.NO_ALARM, _Severity.NO_ALARM],
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    #############################################
    # Drive I
    pv_drive_i_resolver_pos_mon : {
        'type' : 'float',
        'prec' : constants.position_precision,
        'count' : 1,
        'unit' : constants.position_units,
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_drive_i_encoder_pos_mon : {
        'type' : 'float',
        'prec' : constants.position_precision,
        'count' : 1,
        'unit' : constants.position_units,
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_drive_i_velo_mon : {
        'type' : 'float',
        'prec' : constants.position_precision,
        'count' : 1,
        'unit' : constants.velo_units,
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_drive_i_diag_code_mon : {
        'type' : 'int',
        'count' : 1,
        'unit' : constants.no_units,
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_drive_i_diag_msg_mon : {
        'type' : 'char',
        'count' : constants.max_msg_size,
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
    pv_drive_i_is_moving_mon : {
        'type' : 'enum',
        'count' : 1,
        'enums' : constants.bool_enums,
        'states' : [_Severity.NO_ALARM, _Severity.NO_ALARM],
        'mdel' : -1,
        'scan' : constants.scan_rate,
        'asyn' : False,
        'asg' : 'readonly',
    },
}
