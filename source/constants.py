import argparse
import toml
from pydantic import BaseModel
from typing import Optional

###########################################
# Temporary global constants
MINIMUM_GAP=+22
MAXIMUM_GAP=+300
MINIMUM_PHASE=-25
MAXIMUM_PHASE=+25
SERIAL_PORT='/dev/USB0'
A_DRIVE_ADDRESS=21
B_DRIVE_ADDRESS=21
I_DRIVE_ADDRESS=21
S_DRIVE_ADDRESS=21
BAUD_RATE=19200
ECODRIVE_LOG_FILE_PATH='ecodrive_control.log'
EPU_LOG_FILE_PATH='epu_control.log'
###########################################

# dummy function for debugging
def dummy(val=0):
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
msg_device_busy = 'Cmd failed: Device is busy'
#msg_speed_tolerance_error = (
#    'Error: Inconsistent speed configuration between drives')

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
### bool constants
bool_no = 0
bool_yes = 1
### rec decimal places
position_precision = 3
### rec scan rate in sec
scan_rate = 0.1

## EPICS access security
access_security_filename = 'epu.as'

## CA server
### transaction update rate
ca_process_rate = 0.1

## pydantic data validation
class EpuConfig(BaseModel):
    drive_A_address: str
    drive_B_address: Optional[int] = None
    drive_S_address: Optional[int] = None
    drive_I_address: Optional[int] = None
    baud_rate: int
    min_gap: float
    max_gap: float
    min_phase: float
    max_phase: float
    ecodrive_log_file_path: str
    epu_log_file_path: str

## loads config data
with open('../config/config.toml') as f:
    config = toml.load('../config/config.toml')

epu_config = EpuConfig(**config['EPU'])

## EPU config
drive_A_address = epu_config.drive_A_address
drive_B_address = epu_config.drive_B_address
drive_S_address = epu_config.drive_S_address
drive_I_address = epu_config.drive_I_address
baud_rate = epu_config.baud_rate
min_gap = epu_config.min_gap
max_gap = epu_config.max_gap
min_phase = epu_config.min_phase
max_phase = epu_config.max_phase
ecodrive_log_file_path = epu_config.ecodrive_log_file_path
epu_log_file_path = epu_config.epu_log_file_path

# input arguments
def getArgs():
    """ Return command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--pv-prefix', dest='pv_prefix', type=str, required=True, help="$P EPICS IOC prefix")
    parser.add_argument('--drive-A-port', dest='drive_A_port', type=str, required=False, default='', help="Drive A serial port name")
    parser.add_argument('--drive-B-port', dest='drive_B_port', type=str, required=False, default='', help="Drive B serial port name")
    parser.add_argument('--drive-S-port', dest='drive_S_port', type=str, required=False, default='', help="Drive S serial port name")
    parser.add_argument('--drive-I-port', dest='drive_I_port', type=str, required=False, default='', help="Drive I serial port name")
    parser.add_argument('--beaglebone-addr', dest='beaglebone_addr', type=str, required=False, default='', help="Beaglebone IP address")
    args = parser.parse_args()
    return args

args = getArgs()

## IOC parameters
pv_prefix = args.pv_prefix
drive_A_port = args.drive_A_port
drive_B_port = args.drive_B_port
drive_S_port = args.drive_S_port
drive_I_port = args.drive_I_port
beaglebone_addr = args.beaglebone_addr
