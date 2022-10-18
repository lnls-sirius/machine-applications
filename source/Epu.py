
from curses import baudrate
import threading, logging
from . import constants, EcoDrive

class Epu():

    BAUD_RATE=constants.BAUD_RATE
    MAX_GAP = 300
    MIN_GAP = 22
    MAX_PHASE = +25
    MIN_PHASE = -25
    A_DRIVE_ADDRESS = constants.A_DRIVE_ADDRESS
    B_DRIVE_ADDRESS = 22
    I_DRIVE_ADDRESS = 11
    S_DRIVE_ADDRESS = 12

    def __init__(self, min_gap, max_gap, min_phase, max_phase):

        self.lock = threading.RLock()

        self.a_drive = EcoDrive(address=self.A_DRIVE_ADDRESS, baudrate=self.BAUD_RATE,
                        min_limit=self.MIN_GAP, max_limit=self.MAX_GAP)
        self.b_drive = EcoDrive(address=constants.B_DRIVE_ADDRESS, min_limit=min_gap, max_limit=max_gap)
        self.i_drive = EcoDrive(address=constants.I_DRIVE_ADDRESS, min_limit=min_phase, max_limit=max_gap)
        self.s_drive = EcoDrive(address=constants.S_DRIVE_ADDRESS, min_limit=min_phase, max_limit=max_gap)
        
        self.MIN_GAP = min_gap
        self.MAX_GAP = max_gap
        self.MIN_PHASE = min_phase
        self.MAX_PHASE = max_phase

        self.a_gap = self.a_drive.resolver_position
        self.a_status = self.a_drive.diagnostic_code
        self.a_target = self.a_drive.get_target_position()
        self.a_target_reached = self.a_drive.target_position_reached()
        self.a_halt, self.a_enable = self.a_drive.get_halten_status()
        self.b_gap = self.a_drive.resolver_position()
        self.b_status = self.a_drive.diagnostic_message()
        self.b_target = self.a_drive.get_target_position()
        self.b_target_reached = self.a_drive.target_position_reached()
        self.b_halt, self.a_enable = self.a_drive.get_halten_status()

    # Methods called by pcaspy
    def 

    def update(self):
        with self.lock:
            self.drive_a_gap = self.a_drive.resolver_position()
            self.drive_b_gap = self.a_drive.resolver_position()
            self.a_status = self.a_drive.diagnostic_message()
            self.a_target = self.a_drive.get_target_position()
            self.a_target_reached = self.a_drive.target_position_reached()
            self.a_halt, self.a_enable = self.a_drive.get_halten_status()
            self.b_gap = self.a_drive.resolver_position()

    def get_gap_a(self):
        return self.a_drive.resolver_position()

    def verify_gap_limits(self, t_gap) -> bool:
        if self.MIN_GAP <= t_gap <= self.MAX_GAP: return True
        else: return False
    
    def verify_phase_limits(self, t_phase) -> bool:
        if self.min_phase <= t_phase <= self.max_phase: return True
        else: return False

    def set_gap(self, target_gap):
        if self.verify_gap_limits(target_gap):
            self.a_drive.set_target_position(target_gap)
            self.b_drive.set_target_position(target_gap)
            if target_gap == self.a_drive.get_target_position():
                if target_gap == self.b_drive.get_target_position(): # Put a nested if insted of a logic and for easier debugging.
                    return 1
                else: return -1
            else: return -2
        else: return -3

    def set_phase(self, target_phase):
        if self.verify_phase_limits(target_phase):
            self.i_drive.set_target_position(target_phase)
            self.s_drive.set_target_position(target_phase)
            if target_phase == self.i_drive.get_target_position():
                if target_phase == self.s_drive.get_target_position(): # Put a nested if insted of a logic and for easier debugging.
                    return 1
                else: return -1
            else: return -2
        else: return -3

    def set_counter_phase(self, target_phase):
        if self.verify_phase_limits(target_phase):
            self.i_drive.set_target_position(-target_phase)  # see pacmon source code line 1124
            self.s_drive.set_target_position(target_phase)
            if (target_phase * (-1)) == self.i_drive.get_target_position():
                if target_phase == self.s_drive.get_target_position(): # Put a nested if insted of a logic and for easier debugging.
                    return 1
                else: return -1
            else: return -2
        else: return -3

    def start(self):
        pass
    def free_halt(self):
        pass
    def enable(self):
        pass

#teste = Epu(a_address=epu_config.drive_a_address, b_address=epu_config.drive_b_address,\
#        min_gap=epu_config.min_gap, max_gap=epu_config.max_gap, min_phase=epu_config.min_phase, max_phase=epu_config.max_phase)


eco_test = EcoDrive(address='21', serial_port="/dev/pts/10")
eco_test.send("BCD:21")
print(eco_test.raw_read())
print(eco_test.get_target_position())
print(eco_test.diagnostic_message())
# status
# resolver
# encoder
# target
# target_reached
# halt
# enable
# start