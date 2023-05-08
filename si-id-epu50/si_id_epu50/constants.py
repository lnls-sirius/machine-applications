"""Constants module."""

import os as _os
from typing import Optional
import traceback
import yaml
import toml
from pydantic import BaseModel

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


## pydantic data validation
class EpuConfig(BaseModel):
    """EpuConfig."""

    A_DRIVE_ADDRESS: str
    B_DRIVE_ADDRESS: Optional[int] = None
    S_DRIVE_ADDRESS: Optional[int] = None
    I_DRIVE_ADDRESS: Optional[int] = None
    BAUD_RATE: int
    MINIMUM_GAP: float
    MAXIMUM_GAP: float
    MINIMUM_PHASE: float
    MAXIMUM_PHASE: float
    MINIMUM_VELOCITY: float
    MAXIMUM_VELOCITY: float
    ECODRIVE_LOG_FILE_PATH: str
    EPU_LOG_FILE_PATH: str


## loads config data
fname = _os.path.join(
        _os.path.dirname(__file__), 'config', 'config.toml')
config = toml.load(fname)

epu_config = EpuConfig(**config['EPU'])

## config
a_drive_address = epu_config.A_DRIVE_ADDRESS
b_drive_address = epu_config.B_DRIVE_ADDRESS
s_drive_address = epu_config.S_DRIVE_ADDRESS
i_drive_address = epu_config.I_DRIVE_ADDRESS
baud_rate = epu_config.BAUD_RATE
minimum_gap = epu_config.MINIMUM_GAP
maximum_gap = epu_config.MAXIMUM_GAP
minimum_phase = epu_config.MINIMUM_PHASE
maximum_phase = epu_config.MAXIMUM_PHASE
minimum_velo_mm_per_min = epu_config.MINIMUM_VELOCITY  # mm/min
minimum_velo_mm_per_sec = minimum_velo_mm_per_min / 60  # mm/sec
maximum_velo_mm_per_min = epu_config.MAXIMUM_VELOCITY  # mm/min
maximum_velo_mm_per_sec = maximum_velo_mm_per_min / 60  # mm/sec
ecodrive_log_file_path = epu_config.ECODRIVE_LOG_FILE_PATH
epu_log_file_path = epu_config.EPU_LOG_FILE_PATH

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


# dummy function for debugging
def dummy(val=0):
    """Dummy function for debugging."""
    if val != 0:
        print('dummy {}'.format(val))
    else:
        print('dummy')


# constants
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
