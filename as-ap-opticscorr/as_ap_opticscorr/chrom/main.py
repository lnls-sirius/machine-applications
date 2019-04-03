"""Main module of AS-AP-ChromCorr IOC."""

import time as _time
import epics as _epics

import siriuspy as _siriuspy
from siriuspy.servconf.conf_service import ConfigService as _ConfigService
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.csdevice.opticscorr import Const as _Const

from as_ap_opticscorr.opticscorr_utils import (
        OpticsCorr as _OpticsCorr,
        get_config_name as _get_config_name,
        set_config_name as _set_config_name)
import as_ap_opticscorr.chrom.pvs as _pvs

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate simingly repeatitive flat code (they may be
#      easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive'
#      (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes,
#      suffixes, etc)


# Constants
_ALLSET = 0x1f
_ALLCLR_SYNCON = 0x00
_ALLCLR_SYNCOFF = 0x10


class App:
    """Main application for handling chromaticity correction."""

    pvs_database = None

    def __init__(self, driver):
        """Class constructor."""
        _pvs.print_banner_and_save_pv_list()
        self._PREFIX_VACA = _pvs.get_pvs_vaca_prefix()
        self._ACC = _pvs.get_pvs_section()
        self._SFAMS = _pvs.get_corr_fams()

        self._driver = driver

        self._chrom_sp = [0, 0]
        self._chrom_rb = [0, 0]

        self._status = _ALLSET
        self._sfam_check_connection = len(self._SFAMS)*[0]
        self._sfam_check_pwrstate_sts = len(self._SFAMS)*[0]
        self._sfam_check_opmode_sts = len(self._SFAMS)*[-1]
        self._sfam_check_ctrlmode_mon = len(self._SFAMS)*[1]

        self._apply_corr_cmd_count = 0
        self._config_ma_cmd_count = 0
        self._lastcalc_sl = len(self._SFAMS)*[0]

        self._sfam_sl_rb = len(self._SFAMS)*[0]

        if self._ACC == 'SI':
            self._corr_method = _Const.CorrMeth.Proportional
            self._sync_corr = _Const.SyncCorr.Off
            self._config_timing_cmd_count = 0
            self._timing_check_config = 6*[0]
        else:
            self._corr_method = _Const.CorrMeth.Additional
            self._sync_corr = _Const.SyncCorr.Off

        # Get focusing and defocusing families
        sfam_focusing = []
        sfam_defocusing = []
        for fam in self._SFAMS:
            if 'SF' in fam:
                sfam_focusing.append(fam)
            else:
                sfam_defocusing.append(fam)
        sfam_focusing = tuple(sfam_focusing)
        sfam_defocusing = tuple(sfam_defocusing)

        # Initialize correction parameters from local file and configdb
        config_name = _get_config_name(acc=self._ACC.lower(),
                                       opticsparam='chrom')
        [done, corrparams] = self._get_corrparams(config_name)
        if done:
            self.driver.setParam('ConfigName-SP', config_name)
            self.driver.setParam('ConfigName-RB', config_name)
            self._nominal_matrix = corrparams[0]
            self.driver.setParam('RespMat-Mon', self._nominal_matrix)
            self._sfam_nomsl = corrparams[1]
            self.driver.setParam('NominalSL-Mon', self._sfam_nomsl)
            self._nomchrom = corrparams[2]
            self.driver.setParam('NominalChrom-Mon', self._nomchrom)
            self._opticscorr = _OpticsCorr(
                magnetfams_ordering=self._SFAMS,
                nominal_matrix=self._nominal_matrix,
                nominal_intstrengths=self._sfam_nomsl,
                nominal_opticsparam=self._nomchrom,
                magnetfams_focusing=sfam_focusing,
                magnetfams_defocusing=sfam_defocusing)
        else:
            raise Exception("Could not read correction parameters from "
                            "configdb.")

        # Connect to Sextupoles Families
        self._sfam_sl_sp_pvs = {}
        self._sfam_sl_rb_pvs = {}
        self._sfam_pwrstate_sel_pvs = {}
        self._sfam_pwrstate_sts_pvs = {}
        self._sfam_opmode_sel_pvs = {}
        self._sfam_opmode_sts_pvs = {}
        self._sfam_ctrlmode_mon_pvs = {}

        for fam in self._SFAMS:
            self._sfam_sl_sp_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':SL-SP')

            self._sfam_sl_rb_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':SL-RB',
                callback=self._callback_estimate_chrom,
                connection_callback=self._connection_callback_sfam_sl_rb)

            self._sfam_pwrstate_sel_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':PwrState-Sel')
            self._sfam_pwrstate_sts_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':PwrState-Sts',
                callback=self._callback_sfam_pwrstate_sts)

            self._sfam_opmode_sel_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':OpMode-Sel')
            self._sfam_opmode_sts_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':OpMode-Sts',
                callback=self._callback_sfam_opmode_sts)

            self._sfam_ctrlmode_mon_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':CtrlMode-Mon',
                callback=self._callback_sfam_ctrlmode_mon)

        # Connect to Timing
        if self._ACC == 'SI':
            self._timing_sexts_state_sel = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-Sexts:State-Sel')
            self._timing_sexts_state_sts = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-Sexts:State-Sts',
                callback=self._callback_timing_state)

            self._timing_sexts_evgparam_sel = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-Sexts:EVGParam-Sel')
            self._timing_sexts_evgparam_sts = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-Sexts:EVGParam-Sts',
                callback=self._callback_timing_state)

            self._timing_sexts_pulses_sp = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-Sexts:Pulses-SP')
            self._timing_sexts_pulses_rb = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-Sexts:Pulses-RB',
                callback=self._callback_timing_state)

            self._timing_sexts_duration_sp = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-Sexts:Duration-SP')
            self._timing_sexts_duration_rb = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-Sexts:Duration-RB',
                callback=self._callback_timing_state)

            self._timing_evg_chromsmode_sel = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-EVG:ChromsMode-Sel')
            self._timing_evg_chromsmode_sts = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-EVG:ChromsMode-Sts',
                callback=self._callback_timing_state)

            self._timing_evg_chromsdelay_sp = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-EVG:ChromsDelay-SP')
            self._timing_evg_chromsdelay_rb = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-EVG:ChromsDelay-RB',
                callback=self._callback_timing_state)

            self._timing_evg_chromsexttrig_cmd = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-EVG:ChromsExtTrig-Cmd')

        self.driver.setParam('Log-Mon', 'Started.')
        self.driver.updatePVs()

    @staticmethod
    def init_class():
        """Init class."""
        App.pvs_database = _pvs.get_pvs_database()

    @property
    def driver(self):
        """Return driver."""
        return self._driver

    def process(self, interval):
        """Sleep."""
        _time.sleep(interval)

    def read(self, reason):
        """Read from IOC database."""
        if reason == 'Version-Cte':
            if (self._status & 0x1) == 0:  # Check connection
                for fam in self._SFAMS:
                    limits = {}
                    data = self._sfam_sl_rb_pvs[fam].get_ctrlvars()
                    if self._sfam_sl_rb_pvs[fam].upper_disp_limit is not None:
                        limits['hilim'] = data['upper_disp_limit']
                        limits['lolim'] = data['lower_disp_limit']
                        limits['high'] = data['upper_alarm_limit']
                        limits['low'] = data['lower_alarm_limit']
                        limits['hihi'] = data['upper_warning_limit']
                        limits['lolo'] = data['lower_warning_limit']
                    self.driver.setParamInfo('SL'+fam+'-Mon', limits)
                self.driver.updatePVs()
        return None

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        status = False
        if reason == 'ChromX-SP':
            self._chrom_sp[0] = value
            self._calc_sl()
            self.driver.updatePVs()
            status = True

        elif reason == 'ChromY-SP':
            self._chrom_sp[1] = value
            self._calc_sl()
            self.driver.updatePVs()
            status = True

        elif reason == 'ApplyCorr-Cmd':
            done = self._apply_corr()
            if done:
                self._apply_corr_cmd_count += 1
                self.driver.setParam('ApplyCorr-Cmd',
                                     self._apply_corr_cmd_count)
                self.driver.updatePVs()

        elif reason == 'ConfigName-SP':
            [done, corrparams] = self._get_corrparams(value)
            if done:
                _set_config_name(acc=self._ACC.lower(),
                                 opticsparam='chrom',
                                 config_name=value)
                self.driver.setParam('ConfigName-RB', value)
                self._nominal_matrix = corrparams[0]
                self.driver.setParam('RespMat-Mon', self._nominal_matrix)
                self._sfam_nomsl = corrparams[1]
                self.driver.setParam('NominalSL-Mon', self._sfam_nomsl)
                self._nomchrom = corrparams[2]
                self.driver.setParam('NominalChrom-Mon', self._nomchrom)
                self._opticscorr.nominal_matrix = self._nominal_matrix
                self._opticscorr.nominal_intstrengths = self._sfam_nomsl
                self._opticscorr.nominal_opticsparam = self._nomchrom
                self._calc_sl()
                self.driver.setParam('Log-Mon',
                                     'Updated correction parameters.')
                self.driver.updatePVs()
                status = True
            else:
                self.driver.setParam(
                    'Log-Mon', 'ERR:Configuration not found in configdb.')
                self.driver.updatePVs()

        elif reason == 'CorrMeth-Sel':
            if value != self._corr_method:
                self._corr_method = value
                self.driver.setParam('CorrMeth-Sts', self._corr_method)
                self._calc_sl()
                self.driver.updatePVs()
                status = True

        elif reason == 'SyncCorr-Sel':
            if value != self._sync_corr:
                self._sync_corr = value

                done = self._config_ma()
                if done:
                    self._config_ma_cmd_count += 1
                    self.driver.setParam('ConfigMA-Cmd',
                                         self._config_ma_cmd_count)

                if value == 1:
                    done = self._config_timing()
                    if done:
                        self._config_timing_cmd_count += 1
                        self.driver.setParam('ConfigTiming-Cmd',
                                             self._config_timing_cmd_count)

                if (self._status & 0x1) == 0:
                    for fam in self._SFAMS:
                        fam_index = self._SFAMS.index(fam)
                        self._sfam_check_opmode_sts[fam_index] = (
                            self._sfam_opmode_sts_pvs[fam].value)

                    opmode = _PSConst.OpMode.SlowRefSync if value \
                        else _PSConst.OpMode.SlowRef
                    val = any(op != opmode
                              for op in self._sfam_check_opmode_sts)
                else:
                    val = 1

                self._status = _siriuspy.util.update_bit(
                    v=self._status, bit_pos=2, bit_val=val)

                self.driver.setParam('Status-Mon', self._status)
                self.driver.setParam('SyncCorr-Sts', self._sync_corr)
                self.driver.updatePVs()
                status = True

        elif reason == 'ConfigMA-Cmd':
            done = self._config_ma()
            if done:
                self._config_ma_cmd_count += 1
                self.driver.setParam('ConfigMA-Cmd',
                                     self._config_ma_cmd_count)
                self.driver.updatePVs()

        elif reason == 'ConfigTiming-Cmd':
            done = self._config_timing()
            if done:
                self._config_timing_cmd_count += 1
                self.driver.setParam('ConfigTiming-Cmd',
                                     self._config_timing_cmd_count)
                self.driver.updatePVs()

        return status  # return True to invoke super().write of PCASDriver

    def _get_corrparams(self, config_name):
        """Get response matrix from configurations database."""
        cs = _ConfigService()
        querry = cs.get_config(self._ACC.lower()+'_chromcorr_params',
                               config_name)
        querry_result = querry['code']

        if querry_result == 200:
            done = True
            params = querry['result']['value']

            nominal_matrix = [item for sublist in params['matrix']
                              for item in sublist]
            nominal_sl = params['nominal SLs']
            nominal_chrom = params['nominal chrom']
            return [done, [nominal_matrix, nominal_sl, nominal_chrom]]
        else:
            done = False
            return [done, []]

    def _calc_sl(self):
        delta_chromx = self._chrom_sp[0]-self._chrom_rb[0]
        delta_chromy = self._chrom_sp[1]-self._chrom_rb[1]

        if self._corr_method == _Const.CorrMeth.Proportional:
            lastcalc_deltasl = self._opticscorr.calculate_delta_intstrengths(
                method=0, grouping='svd',
                delta_opticsparam=[delta_chromx, delta_chromy])
        else:
            lastcalc_deltasl = self._opticscorr.calculate_delta_intstrengths(
                method=1, grouping='svd',
                delta_opticsparam=[delta_chromx, delta_chromy])

        for fam in self._SFAMS:
            fam_index = self._SFAMS.index(fam)
            current_sl = self._sfam_sl_rb_pvs[fam].get()
            if current_sl is None:
                return
            self._lastcalc_sl[fam_index] = (current_sl +
                                            lastcalc_deltasl[fam_index])
            self.driver.setParam('SL' + fam + '-Mon',
                                 self._lastcalc_sl[fam_index])

        self.driver.setParam('Log-Mon', 'Calculated SL values.')
        self.driver.updatePVs()

    def _apply_corr(self):
        if ((self._status == _ALLCLR_SYNCOFF and
                self._sync_corr == _Const.SyncCorr.Off) or
                self._status == _ALLCLR_SYNCON):
            pvs = self._sfam_sl_sp_pvs
            for fam in pvs:
                fam_index = self._SFAMS.index(fam)
                pv = pvs[fam]
                pv.put(self._lastcalc_sl[fam_index])
            self.driver.setParam('Log-Mon', 'Applied correction.')
            self.driver.updatePVs()

            if self._sync_corr == _Const.SyncCorr.On:
                self._timing_evg_chromsexttrig_cmd.put(0)
                self.driver.setParam('Log-Mon', 'Generated trigger.')
                self.driver.updatePVs()
            return True
        else:
            self.driver.setParam('Log-Mon', 'ERR:ApplyCorr-Cmd failed.')
            self.driver.updatePVs()
        return False

    def _connection_callback_sfam_sl_rb(self, pvname, conn, **kws):
        if not conn:
            self.driver.setParam('Log-Mon', 'WARN:'+pvname+' disconnected.')
            self.driver.updatePVs()

        fam_index = self._SFAMS.index(_SiriusPVName(pvname).dev)
        self._sfam_check_connection[fam_index] = (1 if conn else 0)

        # Change the first bit of correction status
        self._status = _siriuspy.util.update_bit(
            v=self._status, bit_pos=0,
            bit_val=any(s == 0 for s in self._sfam_check_connection))
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_estimate_chrom(self, pvname, value, **kws):
        fam_index = self._SFAMS.index(_SiriusPVName(pvname).dev)
        self._sfam_sl_rb[fam_index] = value

        sfam_deltasl = len(self._SFAMS)*[0]
        for fam in self._SFAMS:
            fam_index = self._SFAMS.index(fam)
            sfam_deltasl[fam_index] = (self._sfam_sl_rb[fam_index] -
                                       self._sfam_nomsl[fam_index])

        self._chrom_rb = self._opticscorr.calculate_opticsparam(sfam_deltasl)
        self.driver.setParam('ChromX-RB', self._chrom_rb[0])
        self.driver.setParam('ChromY-RB', self._chrom_rb[1])
        self.driver.updatePVs()

    def _callback_sfam_pwrstate_sts(self, pvname, value, **kws):
        if value != _PSConst.PwrStateSts.On:
            self.driver.setParam('Log-Mon', 'WARN:'+pvname+' is Off.')
            self.driver.updatePVs()

        fam_index = self._SFAMS.index(_SiriusPVName(pvname).dev)
        self._sfam_check_pwrstate_sts[fam_index] = value

        # Change the second bit of correction status
        self._status = _siriuspy.util.update_bit(
            v=self._status, bit_pos=1,
            bit_val=any(s != _PSConst.PwrStateSts.On
                        for s in self._sfam_check_pwrstate_sts))
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_sfam_opmode_sts(self, pvname, value, **kws):
        self.driver.setParam('Log-Mon', 'WARN:'+pvname+' changed.')
        self.driver.updatePVs()

        fam_index = self._SFAMS.index(_SiriusPVName(pvname).dev)
        self._sfam_check_opmode_sts[fam_index] = value

        # Change the third bit of correction status
        opmode = _PSConst.States.SlowRefSync if self._sync_corr \
            else _PSConst.States.SlowRef
        self._status = _siriuspy.util.update_bit(
            v=self._status, bit_pos=2,
            bit_val=any(s != opmode for s in self._sfam_check_opmode_sts))
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_sfam_ctrlmode_mon(self,  pvname, value, **kws):
        if value != _PSConst.Interface.Remote:
            self.driver.setParam('Log-Mon', 'WARN:'+pvname+' is not Remote.')
            self.driver.updatePVs()

        fam_index = self._SFAMS.index(_SiriusPVName(pvname).dev)
        self._sfam_check_ctrlmode_mon[fam_index] = value

        # Change the fourth bit of correction status
        self._status = _siriuspy.util.update_bit(
            v=self._status, bit_pos=3,
            bit_val=any(s != _PSConst.Interface.Remote
                        for s in self._sfam_check_ctrlmode_mon))
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_timing_state(self, pvname, value, **kws):
        if 'Sexts:State' in pvname:
            self._timing_check_config[0] = value  # Enbl
        elif 'Sexts:EVGParam' in pvname:
            self._timing_check_config[1] = (value == 1)  # Chroms
        elif 'Sexts:Pulses' in pvname:
            self._timing_check_config[2] = (value == 1)  # 1 pulse
        elif 'Sexts:Duration' in pvname:
            self._timing_check_config[3] = (value == 0.15)  # 150us
        elif 'ChromsMode' in pvname:
            self._timing_check_config[4] = (value == 3)  # External
        elif 'ChromsDelay' in pvname:
            self._timing_check_config[5] = (value == 0)  # 0s

        # Change the fifth bit of correction status
        self._status = _siriuspy.util.update_bit(
            v=self._status, bit_pos=4,
            bit_val=any(idx == 0 for idx in self._timing_check_config))
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _config_ma(self):
        opmode = self._sync_corr
        for fam in self._SFAMS:
            if self._sfam_pwrstate_sel_pvs[fam].connected:
                self._sfam_pwrstate_sel_pvs[fam].put(1)
                self._sfam_opmode_sel_pvs[fam].put(opmode)
            else:
                self.driver.setParam('Log-Mon',
                                     'ERR:' + fam + ' is disconnected.')
                self.driver.updatePVs()
                return False
        self.driver.setParam('Log-Mon', 'Sent configuration to sextupoles.')
        self.driver.updatePVs()
        return True

    def _config_timing(self):
        if not any(pv.connected is False for pv in [
                self._timing_sexts_state_sel,
                self._timing_sexts_evgparam_sel,
                self._timing_sexts_pulses_sp,
                self._timing_sexts_duration_sp,
                self._timing_evg_chromsmode_sel,
                self._timing_evg_chromsdelay_sp]):
            self._timing_sexts_state_sel.put(1)
            self._timing_sexts_evgparam_sel.put(1)
            self._timing_sexts_pulses_sp.put(1)
            self._timing_sexts_duration_sp.put(0.15)
            self._timing_evg_chromsmode_sel.put(3)
            self._timing_evg_chromsdelay_sp.put(0)
            self.driver.setParam('Log-Mon', 'Sent configuration to timing.')
            self.driver.updatePVs()
            return True
        else:
            self.driver.setParam('Log-Mon',
                                 'ERR:Some timing PV is disconnected.')
            self.driver.updatePVs()
            return False
