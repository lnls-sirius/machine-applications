"""Main module of AS-AP-PosAng IOC."""

import time as _time
import numpy as _np
from epics import PV as _PV

from siriuspy import util as _util
from siriuspy.callbacks import Callback as _Callback
from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.clientconfigdb import ConfigDBClient as _ConfigDBClient, \
    ConfigDBException as _ConfigDBException
from siriuspy.pwrsupply.csdev import Const as _PSC

from siriuspy.posang.csdev import Const as _PAConst, \
    get_posang_database as _get_database


# Constants
_ALLSET = 0xf
_ALLCLR = 0x0


class App(_Callback):
    """Main application for handling injection in transport lines."""

    def __init__(self, tl, corrs_type):
        """Class constructor."""
        super().__init__()
        self._pvs_database = _get_database(tl, corrs_type)

        # consts
        self._TL = tl.upper()
        self._CORRSTYPE = corrs_type
        if self._TL == 'TS':
            CORRH = (_PAConst.TS_CORRH_POSANG_CHSEPT
                     if self._CORRSTYPE == 'ch-sept'
                     else _PAConst.TS_CORRH_POSANG_SEPTSEPT)
            CORRV = _PAConst.TS_CORRV_POSANG
        elif self._TL == 'TB':
            CORRH = _PAConst.TB_CORRH_POSANG
            CORRV = _PAConst.TB_CORRV_POSANG

        self._status = _ALLSET
        self._orbx_deltapos = 0
        self._orby_deltapos = 0
        self._orbx_deltaang = 0
        self._orby_deltaang = 0
        self._setnewrefkick_cmd_count = 0
        self._config_ps_cmd_count = 0

        self.cdb_client = _ConfigDBClient(
            config_type=self._TL.lower()+'_posang_respm')
        [done, corrparams] = self._get_corrparams()
        if done:
            self._config_name = corrparams[0]
            self._respmat_x = corrparams[1]
            self._respmat_y = corrparams[2]

        self._correctors = dict()
        self._correctors['CH1'] = _SiriusPVName(CORRH[0])
        self._correctors['CH2'] = _SiriusPVName(CORRH[1])
        if len(CORRH) == 3:
            self._correctors['CH3'] = _SiriusPVName(CORRH[2])
        self._correctors['CV1'] = _SiriusPVName(CORRV[0])
        self._correctors['CV2'] = _SiriusPVName(CORRV[1])
        self._corrs2id = {v: k for k, v in self._correctors.items()}

        self._corr_check_connection = dict()
        self._corr_check_pwrstate_sts = dict()
        self._corr_check_opmode_sts = dict()
        self._corr_check_ctrlmode_mon = dict()
        # obs: ignore PU on OpMode and CtrlMode checks
        for corr_id, corr in self._correctors.items():
            self._corr_check_connection[corr_id] = 0
            self._corr_check_pwrstate_sts[corr_id] = 0
            if 'Sept' in corr.dev:
                self._corr_check_opmode_sts[corr_id] = _PSC.States.SlowRef
                self._corr_check_ctrlmode_mon[corr_id] = _PSC.Interface.Remote
            else:
                self._corr_check_opmode_sts[corr_id] = 1
                self._corr_check_ctrlmode_mon[corr_id] = 1

        # Connect to correctors
        self._corr_kick_sp_pvs = {}
        self._corr_kick_rb_pvs = {}
        self._corr_pwrstate_sel_pvs = {}
        self._corr_pwrstate_sts_pvs = {}
        self._corr_opmode_sel_pvs = {}
        self._corr_opmode_sts_pvs = {}
        self._corr_ctrlmode_mon_pvs = {}
        self._corr_refkick = {}

        for corr in self._correctors.values():
            pss = corr.substitute(prefix=_vaca_prefix)
            self._corr_kick_sp_pvs[corr] = _PV(
                pss.substitute(propty_name='Kick', propty_suffix='SP'),
                connection_timeout=0.05)

            self._corr_refkick[corr] = 0
            self._corr_kick_rb_pvs[corr] = _PV(
                pss.substitute(propty_name='Kick', propty_suffix='RB'),
                callback=self._callback_init_refkick,
                connection_callback=self._connection_callback_corr_kick_pvs,
                connection_timeout=0.05)

            self._corr_pwrstate_sel_pvs[corr] = _PV(
                pss.substitute(propty_name='PwrState', propty_suffix='Sel'),
                connection_timeout=0.05)
            self._corr_pwrstate_sts_pvs[corr] = _PV(
                pss.substitute(propty_name='PwrState', propty_suffix='Sts'),
                callback=self._callback_corr_pwrstate_sts,
                connection_timeout=0.05)
            if 'Sept' not in corr.dev:
                self._corr_opmode_sel_pvs[corr] = _PV(
                    pss.substitute(propty_name='OpMode', propty_suffix='Sel'),
                    connection_timeout=0.05)
                self._corr_opmode_sts_pvs[corr] = _PV(
                    pss.substitute(propty_name='OpMode', propty_suffix='Sts'),
                    callback=self._callback_corr_opmode_sts,
                    connection_timeout=0.05)

                self._corr_ctrlmode_mon_pvs[corr] = _PV(
                    pss.substitute(propty_name='CtrlMode',
                                   propty_suffix='Mon'),
                    callback=self._callback_corr_ctrlmode_mon,
                    connection_timeout=0.05)

    def init_database(self):
        """Set initial PV values."""
        self.run_callbacks('ConfigName-SP', self._config_name)
        self.run_callbacks('ConfigName-RB', self._config_name)
        self.run_callbacks('RespMatX-Mon', self._respmat_x)
        self.run_callbacks('RespMatY-Mon', self._respmat_y)
        self.run_callbacks('Log-Mon', 'Started.')

    @property
    def pvs_database(self):
        return self._pvs_database

    def process(self, interval):
        """Sleep."""
        _time.sleep(interval)

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        status = False
        if reason == 'DeltaPosX-SP':
            updated = self._update_delta(value, self._orbx_deltaang, 'x')
            if updated:
                self._orbx_deltapos = value
                self.run_callbacks('DeltaPosX-RB', value)
                status = True

        elif reason == 'DeltaAngX-SP':
            updated = self._update_delta(self._orbx_deltapos, value, 'x')
            if updated:
                self._orbx_deltaang = value
                self.run_callbacks('DeltaAngX-RB', value)
                status = True

        elif reason == 'DeltaPosY-SP':
            updated = self._update_delta(value, self._orby_deltaang, 'y')
            if updated:
                self._orby_deltapos = value
                self.run_callbacks('DeltaPosY-RB', value)
                status = True

        elif reason == 'DeltaAngY-SP':
            updated = self._update_delta(self._orby_deltapos, value, 'y')
            if updated:
                self._orby_deltaang = value
                self.run_callbacks('DeltaAngY-RB', value)
                status = True

        elif reason == 'SetNewRefKick-Cmd':
            updated = self._update_ref()
            if updated:
                self._setnewrefkick_cmd_count += 1
                self.run_callbacks(
                    'SetNewRefKick-Cmd', self._setnewrefkick_cmd_count)

        elif reason == 'ConfigPS-Cmd':
            done = self._config_ps()
            if done:
                self._config_ps_cmd_count += 1
                self.run_callbacks('ConfigPS-Cmd', self._config_ps_cmd_count)

        elif reason == 'ConfigName-SP':
            [done, corrparams] = self._get_corrparams(value)
            if done:
                self._set_config_name(value)
                self._config_name = corrparams[0]
                self.run_callbacks('ConfigName-RB', self._config_name)
                self._respmat_x = corrparams[1]
                self.run_callbacks('RespMatX-Mon', self._respmat_x)
                self._respmat_y = corrparams[2]
                self.run_callbacks('RespMatY-Mon', self._respmat_y)
                self._update_delta(
                    self._orbx_deltapos, self._orbx_deltaang, 'x')
                self._update_delta(
                    self._orby_deltapos, self._orby_deltaang, 'y')
                self.run_callbacks('Log-Mon', 'Updated correction matrices.')
                status = True
            else:
                self.run_callbacks(
                    'Log-Mon', 'ERR:Configuration not found in configdb.')

        return status  # return True to invoke super().write of PCASDriver

    def _get_corrparams(self, config_name=''):
        """Get response matrix from configurations database."""
        try:
            if not config_name:
                config_name = self._get_config_name()
            mats = self.cdb_client.get_config_value(config_name)
        except _ConfigDBException:
            return [False, []]

        respmat_x = [item for sublist in mats['respm-x'] for item in sublist]
        respmat_y = [item for sublist in mats['respm-y'] for item in sublist]
        return [True, [config_name, respmat_x, respmat_y]]

    def _get_config_name(self):
        fname = './' + self._TL.lower() + '-posang.txt'
        try:
            f = open(fname, 'r')
            config_name = f.read().strip('\n')
            f.close()
        except Exception:
            f = open(fname, 'w+')
            config_name = self._get_default_config_name()
            f.write(config_name)
            f.close()
        return config_name

    def _set_config_name(self, config_name):
        f = open('/home/sirius/iocs-log/' + self._TL.lower() + '-ap-posang/' +
                 self._TL.lower() + '-posang.txt', 'w+')
        f.write(config_name)
        f.close()

    def _get_default_config_name(self):
        if self._TL == 'TB':
            return 'Default_CHSept'
        else:
            if self._CORRSTYPE == 'sept-sept':
                return 'TS.V04.01-M1.SeptSept'
            else:
                return 'TS.V04.01-M1'

    def _update_delta(self, delta_pos, delta_ang, orbit):
        if orbit == 'x':
            respmat = self._respmat_x
            corr1 = self._correctors['CH1']
            c1_unit_factor = 1e-6  # urad to rad
            corr2 = self._correctors['CH2']
            c2_unit_factor = 1e-3  # mrad to rad
            if 'CH3' in self._correctors.keys():
                c1_unit_factor = 1e-3  # mrad to rad
                corr3 = self._correctors['CH3']
                c3_kick_sp_pv = self._corr_kick_sp_pvs[corr3]
                c3_refkick = self._corr_refkick[corr3]
                c3_unit_factor = 1e-3  # mrad to rad
        else:
            respmat = self._respmat_y
            corr1 = self._correctors['CV1']
            c1_unit_factor = 1e-6  # urad to rad
            corr2 = self._correctors['CV2']
            c2_unit_factor = 1e-6  # urad to rad

        c1_kick_sp_pv = self._corr_kick_sp_pvs[corr1]
        c2_kick_sp_pv = self._corr_kick_sp_pvs[corr2]
        c1_refkick = self._corr_refkick[corr1]
        c2_refkick = self._corr_refkick[corr2]

        if self._status == _ALLCLR:
            # Convert to respm units (SI):
            #  - deltas position and angle from mrad and mm to rad and meters
            #  - refkicks from urad or mrad to rad
            delta_pos_meters = delta_pos*1e-3
            delta_ang_rad = delta_ang*1e-3
            c1_refkick_rad = c1_refkick*c1_unit_factor
            c2_refkick_rad = c2_refkick*c2_unit_factor
            if 'CH3' in self._correctors.keys():
                c3_refkick_rad = c3_refkick*c3_unit_factor

            [[c1_deltakick_rad], [c2_deltakick_rad]] = _np.dot(
                _np.linalg.inv(_np.reshape(respmat, (2, 2), order='C')),
                _np.array([[delta_pos_meters], [delta_ang_rad]]))

            # Convert kicks from rad to correctors units
            vl1 = (c1_refkick_rad + c1_deltakick_rad)/c1_unit_factor
            c1_kick_sp_pv.put(vl1)
            if 'CH3' in self._correctors.keys():
                vl2 = (c2_refkick_rad + c1_deltakick_rad)/c2_unit_factor
                c2_kick_sp_pv.put(vl2)
                vl3 = (c3_refkick_rad + c2_deltakick_rad)/c3_unit_factor
                c3_kick_sp_pv.put(vl3)
            else:
                vl2 = (c2_refkick_rad + c2_deltakick_rad)/c2_unit_factor
                c2_kick_sp_pv.put(vl2)

            self.run_callbacks('Log-Mon', 'Applied new delta.')
            return True
        else:
            self.run_callbacks(
                'Log-Mon', 'ERR:Failed on applying new delta.')
            return False

    def _update_ref(self):
        if (self._status & 0x1) == 0:  # Check connection
            # updates reference
            for corr_id, corr in self._correctors.items():
                value = self._corr_kick_rb_pvs[corr].get()
                # Get correctors kick in urad (PS) or mrad (PU).
                self._corr_refkick[corr] = value
                self.run_callbacks(
                    'RefKick' + corr_id + '-Mon', value)

            # the deltas from new kick references are zero
            self._orbx_deltapos = 0
            self.run_callbacks('DeltaPosX-SP', 0)
            self.run_callbacks('DeltaPosX-RB', 0)
            self._orbx_deltaang = 0
            self.run_callbacks('DeltaAngX-SP', 0)
            self.run_callbacks('DeltaAngX-RB', 0)
            self._orby_deltapos = 0
            self.run_callbacks('DeltaPosY-SP', 0)
            self.run_callbacks('DeltaPosY-RB', 0)
            self._orby_deltaang = 0
            self.run_callbacks('DeltaAngY-SP', 0)
            self.run_callbacks('DeltaAngY-RB', 0)

            self.run_callbacks('Log-Mon', 'Updated Kick References.')
            updated = True
        else:
            self.run_callbacks('Log-Mon', 'ERR:Some pv is disconnected.')
            updated = False
        return updated

    def _callback_init_refkick(self, pvname, value, cb_info, **kws):
        """Initialize RefKick-Mon pvs and remove this callback."""
        if value is None:
            return
        corr = _SiriusPVName(pvname).device_name
        corr_id = self._corrs2id[corr]

        # Get reference. Correctors kick in urad (PS) or mrad (PU).
        self._corr_refkick[corr] = value
        self.run_callbacks(
            'RefKick' + corr_id + '-Mon', self._corr_refkick[corr])

        # Remove callback
        cb_info[1].remove_callback(cb_info[0])

    def _connection_callback_corr_kick_pvs(self, pvname, conn, **kws):
        if not conn:
            self.run_callbacks('Log-Mon', 'WARN:'+pvname+' disconnected.')

        corr_id = self._corrs2id[_SiriusPVName(pvname).device_name]
        self._corr_check_connection[corr_id] = (1 if conn else 0)

        # Change the first bit of correction status
        self._status = _util.update_bit(
            v=self._status, bit_pos=0,
            bit_val=any(q == 0 for q in self._corr_check_connection.values()))
        self.run_callbacks('Status-Mon', self._status)

    def _callback_corr_pwrstate_sts(self, pvname, value, **kws):
        if value != _PSC.PwrStateSts.On:
            self.run_callbacks('Log-Mon', 'WARN:'+pvname+' is not On.')

        corr_id = self._corrs2id[_SiriusPVName(pvname).device_name]
        self._corr_check_pwrstate_sts[corr_id] = value

        # Change the second bit of correction status
        self._status = _util.update_bit(
            v=self._status, bit_pos=1,
            bit_val=any(q != _PSC.PwrStateSts.On
                        for q in self._corr_check_pwrstate_sts.values()))
        self.run_callbacks('Status-Mon', self._status)

    def _callback_corr_opmode_sts(self, pvname, value, **kws):
        self.run_callbacks('Log-Mon', 'WARN:'+pvname+' changed.')

        corr_id = self._corrs2id[_SiriusPVName(pvname).device_name]
        self._corr_check_opmode_sts[corr_id] = value

        # Change the third bit of correction status
        self._status = _util.update_bit(
            v=self._status, bit_pos=2,
            bit_val=any(s != _PSC.States.SlowRef
                        for s in self._corr_check_opmode_sts.values()))
        self.run_callbacks('Status-Mon', self._status)

    def _callback_corr_ctrlmode_mon(self,  pvname, value, **kws):
        if value != _PSC.Interface.Remote:
            self.run_callbacks('Log-Mon', 'WARN:'+pvname+' is not Remote.')

        corr_id = self._corrs2id[_SiriusPVName(pvname).device_name]
        self._corr_check_ctrlmode_mon[corr_id] = value

        # Change the fourth bit of correction status
        self._status = _util.update_bit(
            v=self._status, bit_pos=3,
            bit_val=any(q != _PSC.Interface.Remote
                        for q in self._corr_check_ctrlmode_mon.values()))
        self.run_callbacks('Status-Mon', self._status)

    def _config_ps(self):
        for corr in self._correctors:
            corr_index = self._correctors.index(corr)
            if self._corr_pwrstate_sel_pvs[corr].connected:
                self._corr_pwrstate_sel_pvs[corr].put(1)
                if corr_index != 1:
                    self._corr_opmode_sel_pvs[corr].put(0)
            else:
                self.run_callbacks(
                    'Log-Mon', 'ERR:' + corr + ' is disconnected.')
                return False
        self.run_callbacks('Log-Mon', 'Configuration sent to correctors.')
        return True
