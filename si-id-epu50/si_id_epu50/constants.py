"""Constants module."""

import os as _os
from typing import Optional
import traceback
import yaml


################# ETHERNET #####################
GPIO_TCP_DEFAULT_PORT = 5050
RS485_TCP_DEFAULT_PORT = 5052

############### GPIO COMMANDS ##################
BSMP_WRITE = 0x20
BSMP_READ = 0x10

HALT_CH_AB = 0x10
START_CH_AB = 0x20
ENABLE_CH_AB = 0x30

HALT_CH_SI = 0x11
START_CH_SI = 0x21
ENABLE_CH_SI = 0x31

RESET_CH_AB = 0x40
RESET_CH_SI = 0x41

############### EPU constants ################
DEFAULT_PATH = '/home/sirius/iocs-log/si-id-epu50/'
AUTOSAVE_DEFAULT_SAVE_LOCATION = DEFAULT_PATH
AUTOSAVE_DEFAULT_REQUEST_FILE = _os.path.join(
    _os.path.dirname(__file__), 'config', 'autosave_epu.req')


class EpuConfig:
    """EpuConfig."""

    A_DRIVE_ADDRESS: str = 21
    B_DRIVE_ADDRESS: Optional[int] = 22
    S_DRIVE_ADDRESS: Optional[int] = 12
    I_DRIVE_ADDRESS: Optional[int] = 11
    BAUD_RATE: int = 19200
    MINIMUM_GAP: float = +22  # [mm]
    MAXIMUM_GAP: float = +300  # [mm]
    MINIMUM_PHASE: float = -25  # [mm]
    MAXIMUM_PHASE: float = +25  # [mm]
    MINIMUM_VELOCITY: float = +0.6  # [mm/min]
    MAXIMUM_VELOCITY: float = +500  # [mm/min]
    ECODRIVE_LOG_FILE_PATH: str = 'ecodrive_control.log'
    EPU_LOG_FILE_PATH: str = 'epu_control.log'


## config
a_drive_address = EpuConfig.A_DRIVE_ADDRESS
b_drive_address = EpuConfig.B_DRIVE_ADDRESS
s_drive_address = EpuConfig.S_DRIVE_ADDRESS
i_drive_address = EpuConfig.I_DRIVE_ADDRESS
baud_rate = EpuConfig.BAUD_RATE
minimum_gap = EpuConfig.MINIMUM_GAP
maximum_gap = EpuConfig.MAXIMUM_GAP
minimum_phase = EpuConfig.MINIMUM_PHASE
maximum_phase = EpuConfig.MAXIMUM_PHASE
minimum_velo_mm_per_min = EpuConfig.MINIMUM_VELOCITY  # [mm/min]
minimum_velo_mm_per_sec = minimum_velo_mm_per_min / 60  # [mm/s]
maximum_velo_mm_per_min = EpuConfig.MAXIMUM_VELOCITY  # [mm/min]
maximum_velo_mm_per_sec = maximum_velo_mm_per_min / 60  # [mm/s]
ecodrive_log_file_path = EpuConfig.ECODRIVE_LOG_FILE_PATH
epu_log_file_path = EpuConfig.EPU_LOG_FILE_PATH

######## Drive error codes and messages #########
fname = _os.path.join(
        _os.path.dirname(__file__), 'config', 'drive_messages.yaml')
with open(fname, "r") as f:
    try:
        drive_code_dict = yaml.safe_load(f)
        drive_diag_msgs = drive_code_dict['diagnostic_messages']
    except Exception:
        print(traceback.format_exc())

default_unknown_diag_msg = "? Unknown diagnostic code"

######### Key diagnostic codes meaning ##########

operational_diag_codes = ['A211']
powered_on_diag_codes = ['A012', 'A010', 'A211']

################## Autosave #####################
autosave_update_rate = 10.0
autosave_num_backup_files = 10

# constants

id_period_length = 50  # [mm]
id_parked_gap = 300  # [mm]
id_parked_phase = 0  # [mm]

## Driver configuration
driver_update_rate = 0.2

## Device support
### error msg array size
error_msg_arr_size = 10
### interval for reading from driver
poll_interval = 0.1
### tolerance for speed difference between drives
speed_tol = 0.0
### IOC messages
msg_clear = ""
msg_device_busy = 'Cmd failed: Device is busy'

## EPICS record fields
### rec units string
no_units = ''
position_units = 'mm'
velo_units = 'mm/s'
# array size limits
max_msg_size = 200
max_long_msg_size = 2000
### rec enums
bool_enums = ['No', 'Yes']
bool_dsbl_enbl = ['Dsbl', 'Enbl']
polarization_states = [
    'none', 'circularn', 'horizontal', 'circularp', 'vertical']
### bool constants
bool_no = 0
bool_yes = 1
### rec decimal places
position_precision = 3
### rec scan rate in sec
scan_rate = 0.1

## EPICS access security
access_security_filename = _os.path.join(
        _os.path.dirname(__file__), 'access_rules.as')

## CA server
### transaction update rate
ca_process_rate = 0.1
