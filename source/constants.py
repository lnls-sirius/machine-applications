import argparse
import toml
from pydantic import BaseModel
from typing import Optional

########## Global constants #############
MINIMUM_GAP=+22
MAXIMUM_GAP=+300
MINIMUM_PHASE=-25
MAXIMUM_PHASE=+25
SERIAL_PORT='/dev/pts/12'
A_DRIVE_ADDRESS=21
B_DRIVE_ADDRESS=22
I_DRIVE_ADDRESS=11
S_DRIVE_ADDRESS=12
BAUD_RATE=19200
ECODRIVE_LOG_FILE_PATH='ecodrive_control.log'
EPU_LOG_FILE_PATH='epu_control.log'
GPIO_TCP_PORT=5050
RS485_TCP_PORT=9993
TCP_IP='10.0.28.100'
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
access_security_filename = 'epu.as'

## CA server
### transaction update rate
ca_process_rate = 0.1

## pydantic data validation
class EpuConfig(BaseModel):
    A_drive_address: str
    B_drive_address: Optional[int] = None
    S_drive_address: Optional[int] = None
    I_drive_address: Optional[int] = None
    baud_rate: int
    min_gap: float
    max_gap: float
    min_phase: float
    max_phase: float
    max_velo: float
    ecodrive_log_file_path: str
    epu_log_file_path: str

## loads config data
with open('../config/config.toml') as f:
    config = toml.load('../config/config.toml')

epu_config = EpuConfig(**config['EPU'])

## EPU config
A_drive_address = epu_config.A_drive_address
B_drive_address = epu_config.B_drive_address
S_drive_address = epu_config.S_drive_address
I_drive_address = epu_config.I_drive_address
baud_rate = epu_config.baud_rate
min_gap = epu_config.min_gap
max_gap = epu_config.max_gap
min_phase = epu_config.min_phase
max_phase = epu_config.max_phase
max_velo_mm_per_min = epu_config.max_velo # mm/min
max_velo = max_velo_mm_per_min / 60 # mm/sec
ecodrive_log_file_path = epu_config.ecodrive_log_file_path
epu_log_file_path = epu_config.epu_log_file_path

#input arguments
def getArgs():
    """ Return command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--pv-prefix', dest='pv_prefix', type=str, required=True, help="$P EPICS IOC prefix")
    parser.add_argument('--drive-msg-port', dest='msg_port', type=str, required=False, default='', help="TCP port for drive messages")
    parser.add_argument('--drive-io-port', dest='io_port', type=str, required=False, default='', help="TCP port for virtual I/O commands")
    parser.add_argument('--beaglebone-addr', dest='beaglebone_addr', type=str, required=False, default='', help="Beaglebone IP address")
    args = parser.parse_args()
    return args

args = getArgs()

# IOC parameters
pv_prefix = args.pv_prefix
msg_port = args.msg_port
io_port = args.io_port
beaglebone_addr = args.beaglebone_addr
