"""Main Module of the program."""

import time as _time
import logging as _log
from functools import partial as _part
from threading import Thread as _Thread
import numpy as _np
from pcaspy import Driver as _PCasDriver
from .matrix import BaseMatrix as _BaseMatrix
from .orbit import BaseOrbit as _BaseOrbit
from .correctors import BaseCorrectors as _BaseCorrectors
from .base_class import BaseClass as _BaseClass, \
    compare_kicks as _compare_kicks

INTERVAL = 1


class SOFB(_BaseClass):
    """Main Class of the IOC."""

    def __init__(self, acc, prefix='', callback=None,
                 orbit=None, matrix=None, correctors=None):
        """Initialize Object."""
        super().__init__(acc, prefix=prefix, callback=callback)
        _log.info('Starting SOFB...')
        self.add_callback(self.update_driver)
        self._driver = None
        self._orbit = self._correctors = self._matrix = None
        self._auto_corr = self._csorb.ClosedLoop.Off
        self._auto_corr_freq = 1
        self._measuring_respmat = False
        self._ring_extension = 1
        self._corr_factor = {'ch': 1.00, 'cv': 1.00}
        self._max_kick = {'ch': 3000, 'cv': 3000}
        self._max_delta_kick = {'ch': 3000, 'cv': 3000}
        self._meas_respmat_kick = {'ch': 300, 'cv': 150}
        if self.acc == 'SI':
            self._corr_factor['rf'] = 1.00
            self._max_kick['rf'] = 3000
            self._max_delta_kick['rf'] = 500
            self._meas_respmat_kick['rf'] = 200
        self._meas_respmat_wait = 5  # seconds
        self._dtheta = None
        self._ref_corr_kicks = None
        self._thread = None

        self.orbit = orbit
        self.correctors = correctors
        self.matrix = matrix

    def get_map2write(self):
        """Get the database of the class."""
        db = {
            'ClosedLoop-Sel': self.set_auto_corr,
            'ClosedLoopFreq-SP': self.set_auto_corr_frequency,
            'MeasRespMat-Cmd': self.set_respmat_meas_state,
            'CalcDelta-Cmd': self.calc_correction,
            'DeltaFactorCH-SP': _part(self.set_corr_factor, 'ch'),
            'DeltaFactorCV-SP': _part(self.set_corr_factor, 'cv'),
            'MaxKickCH-SP': _part(self.set_max_kick, 'ch'),
            'MaxKickCV-SP': _part(self.set_max_kick, 'cv'),
            'MaxDeltaKickCH-SP': _part(self.set_max_delta_kick, 'ch'),
            'MaxDeltaKickCV-SP': _part(self.set_max_delta_kick, 'cv'),
            'MeasRespMatKickCH-SP': _part(self.set_respmat_kick, 'ch'),
            'MeasRespMatKickCV-SP': _part(self.set_respmat_kick, 'cv'),
            'MeasRespMatWait-SP': self.set_respmat_wait_time,
            'ApplyDelta-Cmd': self.apply_corr,
            }
        if self.isring:
            db['RingSize-SP'] = self.set_ring_extension
        if self.acc == 'SI':
            db['DeltaFactorRF-SP'] = _part(self.set_corr_factor, 'rf')
            db['MaxKickRF-SP'] = _part(self.set_max_kick, 'rf')
            db['MaxDeltaKickRF-SP'] = _part(self.set_max_delta_kick, 'rf')
            db['MeasRespMatKickRF-SP'] = _part(self.set_respmat_kick, 'rf')
        return db

    @property
    def orbit(self):
        return self._orbit

    @orbit.setter
    def orbit(self, orb):
        if isinstance(orb, _BaseOrbit):
            self._map2write.update(orb.get_map2write())
            self._orbit = orb

    @property
    def correctors(self):
        return self._correctors

    @correctors.setter
    def correctors(self, corrs):
        if isinstance(corrs, _BaseCorrectors):
            self._map2write.update(corrs.get_map2write())
            self._correctors = corrs

    @property
    def matrix(self):
        return self._matrix

    @matrix.setter
    def matrix(self, mat):
        if isinstance(mat, _BaseMatrix):
            self._map2write.update(mat.get_map2write())
            self._matrix = mat

    @property
    def driver(self):
        """Set the driver of the instance."""
        return self._driver

    @driver.setter
    def driver(self, driver):
        if isinstance(driver, _PCasDriver):
            self._driver = driver

    def process(self):
        """Run continuously in the main thread."""
        t0 = _time.time()
        self.status
        tf = _time.time()
        dt = INTERVAL - (tf-t0)
        if dt > 0:
            _time.sleep(dt)
        else:
            _log.debug('process took {0:f}ms.'.format((tf-t0)*1000))

    def set_ring_extension(self, val):
        val = 1 if val < 1 else int(val)
        val = self._csorb.MAX_RINGSZ if val > self._csorb.MAX_RINGSZ else val
        if val == self._ring_extension:
            return True
        ok = self.orbit.set_ring_extension(val)
        if not ok:
            return False
        ok &= self.matrix.set_ring_extension(val)
        if not ok:
            return False
        self._ring_extension = val
        self.run_callbacks('RingSize-RB', val)
        bpms = _np.array(self._csorb.BPM_POS)
        bpm_pos = [bpms + i*self._csorb.C0 for i in range(val)]
        bpm_pos = _np.hstack(bpm_pos)
        self.run_callbacks('BPMPosS-Mon', bpm_pos)
        return True

    def apply_corr(self, code):
        """Apply calculated kicks on the correctors."""
        if self.orbit.mode == self._csorb.SOFBMode.Offline:
            msg = 'ERR: Offline, cannot apply kicks.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        if self._thread and self._thread.is_alive():
            msg = 'ERR: Loop is Closed or MeasRespMat is On.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        if self._dtheta is None:
            msg = 'ERR: Cannot Apply Kick. Calc Corr first.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        _Thread(
            target=self._apply_corr, kwargs={'code': code},
            daemon=True).start()
        return True

    def calc_correction(self, _):
        """Calculate correction."""
        if self._thread and self._thread.is_alive():
            msg = 'ERR: Loop is Closed or MeasRespMat is On.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        _Thread(target=self._calc_correction, daemon=True).start()
        return True

    def set_respmat_meas_state(self, value):
        if value == self._csorb.MeasRespMatCmd.Start:
            self._start_meas_respmat()
        elif value == self._csorb.MeasRespMatCmd.Stop:
            self._stop_meas_respmat()
        elif value == self._csorb.MeasRespMatCmd.Reset:
            self._reset_meas_respmat()
        return True

    def set_auto_corr(self, value):
        if value == self._csorb.ClosedLoop.On:
            if self._auto_corr == self._csorb.ClosedLoop.On:
                msg = 'ERR: ClosedLoop is Already On.'
                self._update_log(msg)
                _log.error(msg[5:])
                return False
            if self._thread and self._thread.is_alive():
                msg = 'ERR: Cannot Correct, Measuring RespMat.'
                self._update_log(msg)
                _log.error(msg[5:])
                return False
            msg = 'Closing the Loop.'
            self._update_log(msg)
            _log.info(msg)
            self._auto_corr = value
            self._thread = _Thread(
                target=self._do_auto_corr, daemon=True)
            self._thread.start()
        elif value == self._csorb.ClosedLoop.Off:
            msg = 'Opening the Loop.'
            self._update_log(msg)
            _log.info(msg)
            self._auto_corr = value
        return True

    def set_auto_corr_frequency(self, value):
        self._auto_corr_freq = value
        self.run_callbacks('ClosedLoopFreq-RB', value)
        return True

    def set_max_kick(self, plane, value):
        self._max_kick[plane] = float(value)
        self.run_callbacks('MaxKick'+plane.upper()+'-RB', float(value))
        return True

    def set_max_delta_kick(self, plane, value):
        self._max_delta_kick[plane] = float(value)
        self.run_callbacks('MaxDeltaKick'+plane.upper()+'-RB', float(value))
        return True

    def set_corr_factor(self, plane, value):
        self._corr_factor[plane] = value/100
        msg = '{0:s} DeltaFactor set to {1:6.2f}'.format(plane.upper(), value)
        self._update_log(msg)
        _log.info(msg)
        self.run_callbacks('DeltaFactor'+plane.upper()+'-RB', value)
        return True

    def set_respmat_kick(self, plane, value):
        self._meas_respmat_kick[plane] = value
        self.run_callbacks('MeasRespMatKick'+plane.upper()+'-RB', value)
        return True

    def set_respmat_wait_time(self, value):
        self._meas_respmat_wait = value
        self.run_callbacks('MeasRespMatWait-RB', value)
        return True

    def _update_status(self):
        self._status = bool(
            self._correctors.status | self._matrix.status | self._orbit.status)
        self.run_callbacks('Status-Mon', self._status)

    def _apply_corr(self, code):
        nr_ch = self._csorb.NR_CH
        if self._dtheta is None:
            msg = 'Err: All kicks are zero.'
            self._update_log(msg)
            _log.warning(msg[6:])
            return
        dkicks = self._dtheta.copy()
        if code == self._csorb.ApplyDelta.CH:
            dkicks[nr_ch:] = 0
        elif code == self._csorb.ApplyDelta.CV:
            dkicks[:nr_ch] = 0
            if self.acc == 'SI':
                dkicks[-1] = 0
        elif self.acc == 'SI' and code == self._csorb.ApplyDelta.RF:
            dkicks[:-1] = 0
        msg = 'Applying {0:s} kicks.'.format(
                        self._csorb.ApplyDelta._fields[code])
        self._update_log(msg)
        _log.info(msg)
        kicks = self._process_kicks(self._ref_corr_kicks, dkicks)
        if kicks is None:
            return
        self.correctors.apply_kicks(kicks)

    def update_driver(self, pvname, value, **kwargs):
        if self._driver is not None:
            self._driver.setParam(pvname, value)
            self._driver.updatePV(pvname)

    def _stop_meas_respmat(self):
        if not self._measuring_respmat:
            msg = 'ERR: No Measurement ocurring.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        msg = 'Aborting measurement. Wait...'
        self._update_log(msg)
        _log.info(msg)
        self._measuring_respmat = False
        return True

    def _reset_meas_respmat(self):
        if self._measuring_respmat:
            msg = 'Cannot Reset, Measurement in process.'
            self._update_log(msg)
            _log.info(msg)
            return False
        msg = 'Reseting measurement status.'
        self._update_log(msg)
        _log.info(msg)
        self.run_callbacks('MeasRespMat-Mon', self._csorb.MeasRespMatMon.Idle)
        return True

    def _start_meas_respmat(self):
        if self.orbit.mode == self._csorb.SOFBMode.Offline:
            msg = 'ERR: Cannot Meas Respmat in Offline Mode'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        if self._measuring_respmat:
            msg = 'ERR: Measurement already in process.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        if self._thread and self._thread.is_alive():
            msg = 'ERR: Cannot Measure, Loop is Closed.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        msg = 'Starting RespMat measurement.'
        self._update_log(msg)
        _log.info(msg)
        self._measuring_respmat = True
        self._thread = _Thread(target=self._do_meas_respmat, daemon=True)
        self._thread.start()
        return True

    def _do_meas_respmat(self):
        self.run_callbacks(
            'MeasRespMat-Mon', self._csorb.MeasRespMatMon.Measuring)
        mat = list()
        orig_kicks = self.correctors.get_strength()
        enbllist = self.matrix.corrs_enbllist
        nr_corrs = len(orig_kicks)
        orbzero = self.orbit.get_orbit(True) * 0.0
        for i in range(nr_corrs):
            if not self._measuring_respmat:
                self.run_callbacks(
                    'MeasRespMat-Mon', self._csorb.MeasRespMatMon.Aborted)
                msg = 'Measurement stopped.'
                self._update_log(msg)
                _log.info(msg)
                for _ in range(i, nr_corrs):
                    mat.append(orbzero)
                break

            msg = '{0:d}/{1:d} -> {2:s}'.format(
                i+1, nr_corrs, self.correctors.corrs[i].name)
            self._update_log(msg)
            _log.info(msg)
            if not enbllist[i]:
                mat.append(orbzero)
                continue

            if i < self._csorb.NR_CH:
                delta = self._meas_respmat_kick['ch']
            elif i < self._csorb.NR_CH + self._csorb.NR_CV:
                delta = self._meas_respmat_kick['cv']
            elif i < self._csorb.NR_CORRS:
                delta = self._meas_respmat_kick['rf']

            kicks = [None, ] * nr_corrs
            kicks[i] = orig_kicks[i] + delta/2
            self.correctors.apply_kicks(kicks)
            _time.sleep(self._meas_respmat_wait)
            orbp = self.orbit.get_orbit(True)

            kicks[i] = orig_kicks[i] - delta/2
            self.correctors.apply_kicks(kicks)
            _time.sleep(self._meas_respmat_wait)
            orbn = self.orbit.get_orbit(True)
            mat.append((orbp-orbn)/delta)

            kicks[i] = orig_kicks[i]
            self.correctors.apply_kicks(kicks)

        msg = 'Measurement Completed.'
        self._update_log(msg)
        _log.info(msg)
        mat = _np.array(mat).T
        self.matrix.set_respmat(list(mat.flatten()))
        self.run_callbacks(
            'MeasRespMat-Mon', self._csorb.MeasRespMatMon.Completed)
        self._measuring_respmat = False

    def _do_auto_corr(self):
        self.run_callbacks('ClosedLoop-Sts', 1)
        strn = 'TIMEIT: {0:20s} - {1:7.3f}'
        while self._auto_corr == self._csorb.ClosedLoop.On:
            t0 = _time.time()
            _log.debug('TIMEIT: BEGIN')
            orb = self.orbit.get_orbit()
            t1 = _time.time()
            _log.debug(strn.format('get orbit:', 1000*(t1-t0)))
            dkicks = self.matrix.calc_kicks(orb)
            t2 = _time.time()
            _log.debug(strn.format('calc kicks:', 1000*(t2-t1)))
            kicks = self.correctors.get_strength()
            t3 = _time.time()
            _log.debug(strn.format('get strength:', 1000*(t3-t2)))
            kicks = self._process_kicks(kicks, dkicks)
            if kicks is None:
                self._auto_corr = self._csorb.ClosedLoop.Off
                msg = 'ERR: Opening the Loop'
                self._update_log(msg)
                _log.error(msg[5:])
                self.run_callbacks('ClosedLoop-Sel', 0)
                continue
            t4 = _time.time()
            _log.debug(strn.format('process kicks:', 1000*(t4-t3)))
            self.correctors.apply_kicks(kicks)  # slowest part
            t5 = _time.time()
            _log.debug(strn.format('apply kicks:', 1000*(t5-t4)))
            dt = (_time.time()-t0)
            _log.debug(strn.format('total:', 1000*dt))
            _log.debug('TIMEIT: END')
            interval = 1/self._auto_corr_freq
            if dt > interval:
                msg = 'WARN: Loop took {0:6.2f}ms.'.format(dt*1000)
                self._update_log(msg)
                _log.warning(msg[6:])
            dt = interval - dt
            if dt > 0:
                _time.sleep(dt)
        msg = 'Loop is opened.'
        self._update_log(msg)
        _log.info(msg)
        self.run_callbacks('ClosedLoop-Sts', 0)

    def _calc_correction(self):
        msg = 'Getting the orbit.'
        self._update_log(msg)
        _log.info(msg)
        orb = self.orbit.get_orbit()
        msg = 'Calculating the kicks.'
        self._update_log(msg)
        _log.info(msg)
        self._ref_corr_kicks = self.correctors.get_strength()
        dkicks = self.matrix.calc_kicks(orb)
        if dkicks is not None:
            self._dtheta = dkicks

    def _process_kicks(self, kicks, dkicks):
        if dkicks is None:
            return

        # keep track of which dkicks were originally different from zero:
        newkicks = [None, ] * len(dkicks)
        for i, dkick in enumerate(dkicks):
            if not _compare_kicks(dkick, 0):
                newkicks[i] = 0.0
        idcs_to_process = _np.array(newkicks) != None
        if not idcs_to_process.any():
            return newkicks

        nr_ch = self._csorb.NR_CH
        slcs = {'ch': slice(None, nr_ch), 'cv': slice(nr_ch, None)}
        if self.acc == 'SI':
            slcs = {
                'ch': slice(None, nr_ch),
                'cv': slice(nr_ch, -1),
                'rf': slice(-1, None)}
        for pln in sorted(slcs.keys()):
            slc = slcs[pln]
            idcs_pln = idcs_to_process[slc]
            if not idcs_pln.any():
                continue
            dk_slc = dkicks[slc][idcs_pln]
            k_slc = kicks[slc][idcs_pln]
            dk_slc *= self._corr_factor[pln]

            # Check if any kick is larger than the maximum allowed:
            ind, *_ = _np.where(_np.abs(k_slc) > self._max_kick[pln])
            if ind.size:
                msg = 'ERR: Kicks above MaxKick{0:s}.'.format(pln.upper())
                self._update_log(msg)
                _log.error(msg[5:])
                return

            # Check if any delta kick is larger the maximum allowed
            max_delta_kick = _np.max(_np.abs(dk_slc))
            factor1 = 1.0
            if max_delta_kick > self._max_delta_kick[pln]:
                factor1 = self._max_delta_kick[pln]/max_delta_kick
                dk_slc *= factor1
                percent = self._corr_factor[pln] * factor1 * 100
                msg = 'WARN: reach MaxDeltaKick{0:s}. Using {1:5.2f}%'.format(
                                                        pln.upper(), percent)
                self._update_log(msg)
                _log.warning(msg[6:])

            # Check if any kick + delta kick is larger than the maximum allowed
            max_kick = _np.max(_np.abs(k_slc + dk_slc))
            factor2 = 1.0
            if max_kick > self._max_kick[pln]:
                Q = _np.ones((2, k_slc.size), dtype=float)
                # perform the modulus inequality:
                Q[0, :] = (-self._max_kick[pln] - k_slc) / dk_slc
                Q[1, :] = (self._max_kick[pln] - k_slc) / dk_slc
                # since we know that any initial kick is lesser than max_kick
                # from the previous comparison, at this point each column of Q
                # has a positive and a negative value. We must consider only
                # the positive one and take the minimum value along the columns
                # to be the multiplicative factor:
                Q = _np.max(Q, axis=0)
                factor2 = min(_np.min(Q), 1.0)
                dk_slc *= factor2
                percent = self._corr_factor[pln] * factor1 * factor2 * 100
                msg = 'WARN: reach MaxKick{0:s}. Using {1:5.2f}%'.format(
                                                        pln.upper(), percent)
                self._update_log(msg)
                _log.warning(msg[6:])

            dkicks[slc][idcs_pln] = dk_slc

        for i, dkick in enumerate(dkicks):
            if newkicks[i] is not None:
                newkicks[i] = kicks[i] + dkick
        return newkicks
