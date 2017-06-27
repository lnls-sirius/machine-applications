import time as _time
import os as _os
import numpy as _np
from threading import Thread as _Thread
import logging as _log
import epics as _epics
from siriuspy.search import PSSearch as _PSSearch

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate simingly repeatitive flat code (they may be easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive' (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes, suffixes, etc)

with open('VERSION') as f:
    __version__ = f.read()
_TIMEOUT = 0.05

TINY_INTERVAL = 0.001
NUM_TIMEOUT = 2000

NR_BPMS  = 160
NR_CH    = 120
NR_CV    = 160
NR_CORRS = NR_CH + NR_CV + 1
MTX_SZ   = (2*NR_BPMS) * NR_CORRS
DANG = 2E-1
DFREQ = 200
SECTION = 'SI'
LL_PREF = 'VAF-'

class App:

    def get_database(self):
        db = dict()
        pre = self.prefix
        db.update(self.correctors.get_database())
        db.update(self.matrix.get_database())
        db.update(self.orbit.get_database())
        db[pre + 'Log-Mon'] = {'type':'string','value':''}
        db[pre + 'AutoCorrState-Sel'] = {'type':'enum','enums':('Off','On'),'value':0,
                                         'fun_set_pv':self._toggle_auto_corr}
        db[pre + 'AutoCorrState-Sts'] = {'type':'enum','enums':('Off','On'),'value':0}
        db[pre + 'AutoCorrFreq-SP']   = {'type':'float','value':1,'lolim':1e-3, 'hilim':20,'unit':'Hz',
                                         'prec':3, 'fun_set_pv':self._set_auto_corr_frequency}
        db[pre + 'AutoCorrFreq-RB']    = {'type':'float','value':1,'prec':2, 'unit':'Hz'}
        db[pre + 'StartMeasRSPMtx-Cmd']  = {'type':'int','value':0,'fun_set_pv':self._start_measure_response_matrix}
        db[pre + 'AbortMeasRSPMtx-Cmd']  = {'type':'int','value':0,'fun_set_pv':self._abort_measure_response_matrix}
        db[pre + 'ResetMeasRSPMtx-Cmd']  = {'type':'int','value':0,'fun_set_pv':self._reset_measure_response_matrix}
        db[pre + 'MeasRSPMtxState-Sts']  = {'type':'enum','enums':('Idle','Measuring','Completed','Aborted'),'value':0}
        db[pre + 'CorrectionMode-Sel'] = {'type':'enum','enums':('OffLine','Online'),'value':1,
                                          'unit':'Defines is correction is offline or online',
                                          'fun_set_pv':self._toggle_correction_mode}
        db[pre + 'CorrectionMode-Sts'] = {'type':'enum','enums':('OffLine','Online'),'value':1,
                                          'unit':'Defines is correction is offline or online'}
        db[pre + 'CalcCorr-Cmd']     = {'type':'int','value':0,'unit':'Calculate kicks',
                                        'fun_set_pv':self._calc_correction}
        db[pre + 'ApplyKicks-Cmd']   = {'type':'enum','enums':('CH','CV','RF','All'),'value':0,
                                        'unit':'Apply last calculated kicks.',
                                        'fun_set_pv':self._apply_kicks}
        return db

    def __init__(self,driver=None):
        _log.info('Starting App...')
        self._driver = driver
        self.prefix = SECTION+'-Glob:AP-SOFB:'
        self.orbit = Orbit(prefix = self.prefix, callback = self._update_driver)
        self.correctors = Correctors(prefix = self.prefix, callback = self._update_driver)
        self.matrix = Matrix(prefix = self.prefix, callback = self._update_driver)
        self.auto_corr = 0
        self.measuring_resp_matrix = False
        self.auto_corr_freq = 1
        self.correction_mode = 1
        self.dtheta = None
        self._thread = None
        self._database = self.get_database()

    @property
    def driver(self):
        return self._driver

    @driver.setter
    def driver(self,driver):
        _log.debug("Setting App's driver.")
        self._driver = driver

    def write(self,reason,value):
        _log.debug('App: Writing PV {0:s} with value {1:s}'.format(reason,str(value)))
        if not self._isValid(reason,value):
            return False
        fun_ = self._database[reason].get('fun_set_pv')
        if fun_ is None:
            _log.warning('App: Write unsuccessful. PV {0:s} does not have a set function.'.format(reason))
            return False
        ret_val = fun_(value)
        if ret_val:
            _log.debug('App: Write complete.')
        else:
            _log.warning('App: Unsuccessful write of PV {0:s}; value = {1:s}.'.format(reason,str(value)))
        return ret_val

    def process(self,interval):
        t0 = _time.time()
        # _log.debug('App: Executing check.')
        # self.check()
        tf = _time.time()
        dt = (tf-t0)
        if dt > 0.2: _log.debug('App: check took {0:f}ms.'.format(dt*1000))
        dt = interval - dt
        if dt>0: _time.sleep(dt)

    def connect(self):
        _log.info('Connecting to Orbit PVs:')
        self._call_callback('Log-Mon', 'Connecting to Low Level PVs')
        self.orbit.connect()
        _log.info('All Orbit connection opened.')
        self.matrix.connect()
        _log.info('Connecting to Correctors PVs:')
        self.correctors.connect()
        _log.info('All Correctors connection opened.')

    def _call_callback(self,pv,value):
        self._update_driver(self.prefix + pv, value)

    def _update_driver(self,pvname,value,**kwargs):
        _log.debug('PV {0:s} updated in driver database with value {1:s}'.format(pvname,str(value)))
        self._driver.setParam(pvname,value)
        self._driver.updatePVs()

    def _isValid(self,reason,value):
        if reason.endswith(('-Sts','-RB', '-Mon')):
            _log.debug('App: PV {0:s} is read only.'.format(reason))
            return False
        enums = self._database[reason].get('enums')
        if enums is not None:
            len_ = len(enums)
            if int(value) >= len_:
                _log.warning('App: value {0:d} too large for PV {1:s} of type enum'.format(value,reason))
                return False
        return True

    def _abort_measure_response_matrix(self, value):
        print('here')
        if not self.measuring_resp_matrix:
            self._call_callback('Log-Mon','Err :No Measurement ocurring.')
            return False
        self._call_callback('Log-Mon','Aborting measurement.')
        self.measuring_resp_matrix = False
        self._thread.join()
        self._call_callback('Log-Mon','Measurement aborted.')
        return True

    def _reset_measure_response_matrix(self,value):
        if self.measuring_resp_matrix:
            self._call_callback('Log-Mon','Cannot Reset, Measurement in process.')
            return False
        self._call_callback('Log-Mon','Reseting measurement status.')
        self._call_callback('MeasRSPMtxState-Sts',0)
        return True

    def _start_measure_response_matrix(self,value):
        if self.measuring_resp_matrix:
            self._call_callback('Log-Mon','Err: Measurement already in process.')
            return False
        if self._thread and self._thread.isAlive():
            self._call_callback('Log-Mon','Err: Cannot Measure, AutoCorr is On.')
            return False
        self.measuring_resp_matrix = True
        self._call_callback('Log-Mon', 'Starting RSP Matrix measurement.')
        self._thread = _Thread(target=self._measure_response_matrix,daemon=True)
        self._thread.start()
        return True

    def _measure_response_matrix(self):
        self._call_callback('MeasRSPMtxState-Sts',1)
        mat = _np.zeros([2*NR_BPMS,NR_CORRS])
        for i in range(NR_CORRS):
            if not self.measuring_resp_matrix:
                self._call_callback('MeasRSPMtxState-Sts',3)
                return
            self._call_callback('Log-Mon', 'Varying Corrector {0:d} of {1:d}'.format(i,NR_CORRS))
            delta = DANG if i<NR_CORRS-1 else DFREQ
            kicks = _np.zeros(NR_CORRS)
            kicks[i] = delta/2
            self.correctors.apply_kicks(kicks)
            orbp = self.orbit.get_orbit()
            kicks[i] = -delta
            self.correctors.apply_kicks(kicks)
            orbn = self.orbit.get_orbit()
            kicks[i] = delta/2
            self.correctors.apply_kicks(kicks)
            mat[:,i] = (orbp-orbn)/delta
        self._call_callback('Log-Mon', 'Measurement Completed.')
        self.matrix.set_resp_matrix(list(mat.flatten()))
        self._call_callback('MeasRSPMtxState-Sts',2)
        self.measuring_resp_matrix = False

    def _toggle_auto_corr(self,value):
        if value:
            if self.auto_corr:
                self._call_callback('Log-Mon','Err: AutoCorr is Already On.')
                return False
            self.auto_corr = value
            if self._thread and self._thread.isAlive():
                self._call_callback('Log-Mon','Err: Cannot Correct, Measuring RSPMtx.')
                return False
            self._call_callback('Log-Mon', 'Turning Auto Correction On.')
            self._thread = _Thread(target=self._automatic_correction,daemon=True)
            self._thread.start()
        else:
            self._call_callback('Log-Mon', 'Turning Auto Correction Off.')
            self.auto_corr = value
        return True

    def _automatic_correction(self):
        if not self.correction_mode:
            self._call_callback('Log-Mon','Err: Cannot Auto Correct in Offline Mode')
            self._call_callback('AutoCorrState-Sel',0)
            self._call_callback('AutoCorrState-Sts',0)
            return
        self._call_callback('AutoCorrState-Sts',1)
        while self.auto_corr:
            t0 = _time.time()
            orb = self.orbit.get_orbit()
            self.dtheta = self.matrix.calc_kicks(orb)
            self.correctors.apply_kicks(self.dtheta, limit=True)
            tf = _time.time()
            dt = (tf-t0)
            interval = 1/self.auto_corr_freq
            if dt > interval:
                _log.debug('App: check took {0:f}ms.'.format(dt*1000))
                self._call_callback('Log-Mon', 'Warn: Auto Corr Loop took {0:6.2f}ms.'.format(dt*1000))
            dt = interval - dt
            if dt>0: _time.sleep(dt)
        self._call_callback('Log-Mon', 'Auto Correction is Off.')
        self._call_callback('AutoCorrState-Sts',0)

    def _toggle_correction_mode(self,value):
        self.correction_mode = value
        self.orbit.correction_mode = value
        self._call_callback('Log-Mon', 'Changing to {0:s} mode.'.format('Online' if value else 'Offline'))
        self._call_callback('CorrectionMode-Sts',value)
        self.orbit.get_orbit()
        return True

    def _set_auto_corr_frequency(self,value):
        self.auto_corr_freq = value
        self._call_callback('AutoCorrFreq-RB',value)
        return True

    def _calc_correction(self,value):
        if self._thread and self._thread.isAlive():
            self._call_callback('Log-Mon','Err: AutoCorr or MeasRSPMtx is On.')
            return False
        self._call_callback('Log-Mon', 'Getting the orbit.')
        orb = self.orbit.get_orbit()
        self._call_callback('Log-Mon', 'Calculating the kicks.')
        self.dtheta = self.matrix.calc_kicks(orb)
        return True

    def _apply_kicks(self,code):
        if not self.correction_mode:
            self._call_callback('Log-Mon','Err: Offline, cannot apply kicks.')
            return False
        if self._thread and self._thread.isAlive():
            self._call_callback('Log-Mon','Err: AutoCorr or MeasRSPMtx is On.')
            return False
        kicks = self.dtheta.copy()
        str_ = 'Applying '
        if code == 0:
            str_ += 'CH '
            kicks[NR_CH:] = 0
        elif code == 1:
            str_ += 'CV '
            kicks[:NR_CH] = 0
            kicks[-1] = 0
        elif code == 2:
            str_ += 'RF '
            kicks[:-1] = 0
        elif code == 3:
            str_ += 'All '
        self._call_callback('Log-Mon',str_ + 'kicks.')
        if any(kicks):
            self.correctors.apply_kicks(kicks)
        return True


class Orbit:

    REF_ORBIT_FILENAME = 'data/reference_orbit'
    GOLDEN_ORBIT_FILENAME = 'data/golden_orbit'
    EXT = '.siorb'

    def get_database(self):
        db = dict()
        pre = self.prefix
        db[pre + 'OrbitRefX-SP'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0],
                                    'fun_set_pv':lambda x: self._set_ref_orbit('x',x)}
        db[pre + 'OrbitRefX-RB'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0]}
        db[pre + 'OrbitRefY-SP'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0],
                                    'fun_set_pv':lambda x: self._set_ref_orbit('y',x)}
        db[pre + 'OrbitRefY-RB'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0]}
        db[pre + 'GoldenOrbitX-SP'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0],
                                    'fun_set_pv':lambda x: self._set_golden_orbit('x',x)}
        db[pre + 'GoldenOrbitX-RB'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0]}
        db[pre + 'GoldenOrbitY-SP'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0],
                                    'fun_set_pv':lambda x: self._set_golden_orbit('y',x)}
        db[pre + 'GoldenOrbitY-RB'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0]}
        db[pre + 'setRefwithGolden-Cmd'] = {'type':'int','value':0,
                                            'unit':'Set the reference orbit with the Golden Orbit',
                                            'fun_set_pv':self._set_ref_with_golden}
        db[pre + 'CorrOrbitX-Mon']   = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0]}
        db[pre + 'CorrOrbitY-Mon']   = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0]}
        db[pre + 'OnlineOrbitX-Mon'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0]}
        db[pre + 'OnlineOrbitY-Mon'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0]}

        db[pre + 'OfflineOrbitX-SP'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0],
                                        'fun_set_pv':lambda x: self._set_offline_orbit('x',x)}
        db[pre + 'OfflineOrbitX-RB'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0]}
        db[pre + 'OfflineOrbitY-SP'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0],
                                        'fun_set_pv':lambda x: self._set_offline_orbit('y',x)}
        db[pre + 'OfflineOrbitY-RB'] = {'type':'float','count':NR_BPMS,'value':NR_BPMS*[0]}
        db[pre + 'OrbitPointsNum-SP']   = {'type':'int','value':1,'unit':'number of points for median',
                                        'fun_set_pv':self._set_orbit_points_num,
                                        'lolim':1, 'hilim':200}
        db[pre + 'OrbitPointsNum-RB']   = {'type':'int','value':1,'unit':'number of points for median'}
        return db

    def __init__(self,prefix,callback):
        self.callback = callback
        self.prefix = prefix
        self.orbs = {'x':[],'y':[]}
        self.orb = {'x':None,'y':None}
        self.offline_orbit = {'x':_np.zeros(NR_BPMS),'y':_np.zeros(NR_BPMS)}
        self.orbit_points_num = 1
        self.correction_mode = 1
        self.pv = {'x':None, 'y':None}

    def connect(self):
        self._load_basic_orbits()
        self.pv ={'x':_epics.PV(SECTION + '-Glob:AP-Orbit:OrbitX-Mon',
                                callback=self._update_orbs('x'),
                                connection_callback= self._on_connection ),
                  'y':_epics.PV(SECTION + '-Glob:AP-Orbit:OrbitY-Mon',
                                callback=self._update_orbs('y'),
                                connection_callback= self._on_connection )  }
        if not self.pv['x'].connected or not self.pv['y'].connected:
            self._call_callback('Log-Mon','Orbit PVs not Connected.')
        if self.pv['x'].count != NR_BPMS:
            self._call_callback('Log-Mon','Orbit length not consistent')

    def get_orbit(self):
        if not self.correction_mode:
            orbx = self.offline_orbit['x']
            orby = self.offline_orbit['y']
            self._call_callback('CorrOrbitX-Mon',list(orbx))
            self._call_callback('CorrOrbitY-Mon',list(orby))
        else:
            for i in range(NUM_TIMEOUT):
                if self.orb['x'] is not None and self.orb['y'] is not None:
                    orbx = self.orb['x']
                    orby = self.orb['y']
                    break
                _time.sleep(TINY_INTERVAL)
            else:
                self._call_callback('Log-Mon','Err: get orbit function timeout.')
                orbx =  self.ref_orbit['x']
                orby =  self.ref_orbit['y']
        refx = self.ref_orbit['x']
        refy = self.ref_orbit['y']
        return _np.hstack([orbx-refx, orby-refy])

    def _on_connection(self,pvname,conn,pv):
        if not conn:
            self._call_callback('Log-Mon','PV '+pvname+'disconnected.')

    def _call_callback(self,pv,value):
        self.callback(self.prefix + pv, value)

    def _set_offline_orbit(self,plane,value):
        self._call_callback('Log-Mon','Setting New Offline Orbit.')
        if len(value) != NR_BPMS:
            self._call_callback('Log-Mon','Err: Wrong Size.')
            return False
        self.offline_orbit[plane] = _np.array(value)
        self._call_callback('OfflineOrbit'+plane.upper()+'-RB', _np.array(value))
        return True

    def _load_basic_orbits(self):
        self.ref_orbit = dict()
        self.golden_orbit = dict()
        for plane in ('x','y'):
            filename = self.REF_ORBIT_FILENAME+plane.upper() + self.EXT
            self.ref_orbit[plane] = _np.zeros(NR_BPMS,dtype=float)
            if _os.path.isfile(filename):
                self.ref_orbit[plane] = _np.loadtxt(filename)
            filename = self.GOLDEN_ORBIT_FILENAME+plane.upper() + self.EXT
            self.golden_orbit[plane] = _np.zeros(NR_BPMS,dtype=float)
            if _os.path.isfile(filename):
                self.golden_orbit[plane] = _np.loadtxt(filename)

    def _save_ref_orbit(self,plane, orb):
        _np.savetxt(self.REF_ORBIT_FILENAME+plane.upper() + self.EXT,orb)

    def _save_golden_orbit(self,plane, orb):
        _np.savetxt(self.GOLDEN_ORBIT_FILENAME+plane.upper() + self.EXT,orb)

    def _reset_orbs(self,plane):
        self.orbs[plane] = []
        self.orb[plane] = None

    def _update_orbs(self,plane):
        def update(pvname,value,**kwargs):
            if value is None: return True
            orb = _np.array(value, dtype=float)
            if len(self.orbs[plane]) < self.orbit_points_num:
                self.orbs[plane].append(orb)
            else:
                self.orbs[plane] = self.orbs[plane][1:]
                self.orbs[plane].append(orb)
            if len(self.orbs[plane]) == self.orbit_points_num:
                if self.orbit_points_num > 1:
                    self.orb[plane] = _np.mean(self.orbs[plane], axis=0)
                else:
                    self.orb[plane] = self.orbs[plane][0]
                self._call_callback('OnlineOrbit'+plane.upper()+'-Mon',list(self.orb[plane]))
                if self.correction_mode:
                    self._call_callback('CorrOrbit'+plane.upper()+'-Mon',list(self.orb[plane]))
            return True
        return update

    def _set_orbit_points_num(self,num):
        self._call_callback('Log-Mon','Setting new number of points for median.')
        self.orbit_points_num = num
        self._reset_orbs('x')
        self._reset_orbs('y')
        self._call_callback('OrbitPointsNum-RB', num)
        return True

    # I changed to use median instead of mean:
    # def _set_orbit_neglected_points_num(self,num):
    #     self._call_callback('Log-Mon','Changing Number Neglected points.')
    #     self.orbit_neglect_num = num
    #     self._reset_orbs('x')
    #     self._reset_orbs('y')
    #     self._call_callback('OrbitNeglectNum-RB', num)
    #     return True

    def _set_ref_orbit(self,plane,orb):
        self._call_callback('Log-Mon','Setting New Reference Orbit.')
        if len(orb) != NR_BPMS:
            self._call_callback('Log-Mon','Err: Wrong Size.')
            return False
        self._save_ref_orbit(plane,orb)
        self.ref_orbit[plane] = _np.array(orb,dtype=float)
        self._reset_orbs(plane)
        self._call_callback('OrbitRef'+plane.upper()+'-RB', orb)
        return True

    def _set_golden_orbit(self,plane,orb):
        self._call_callback('Log-Mon','Setting New Golden Orbit.')
        if len(value) != NR_BPMS:
            self._call_callback('Log-Mon','Err: Wrong Size.')
            return False
        self._save_golden_orbit(plane,orb)
        self.golden_orbit[plane] = _np.array(orb,dtype=float)
        self._call_callback('GoldenOrbit'+plane.upper()+'-RB', orb)
        return True

    def _set_ref_with_golden(self,value):
        self._call_callback('Log-Mon','Golden Orbit --> Reference Orbit.')
        for pl,orb in self.golden_orbit.items():
            self._call_callback('OrbitRef'+pl.upper()+'-SP', orb.copy())
            self._set_ref_orbit(pl,orb.copy())
        return True


class Matrix:
    RF_ENBL_ENUMS = ('No','Yes')
    RSP_MTX_FILENAME = 'data/response_matrix'
    EXT = '.sirspmtx'

    def get_database(self):
        db = dict()
        pre = self.prefix
        db[pre + 'RSPMatrix-SP'] = {'type':'float','count':MTX_SZ,'value':MTX_SZ*[0],
                                    'unit':'(BH,BV)(nm) x (CH,CV,RF)(urad,Hz)',
                                    'fun_set_pv':self.set_resp_matrix}
        db[pre + 'RSPMatrix-RB'] = {'type':'float','count':MTX_SZ,'value':MTX_SZ*[0],
                                    'unit':'(BH,BV)(nm) x (CH,CV,RF)(urad,Hz)'}
        db[pre + 'SingValues-Mon']= {'type':'float','count':NR_CORRS,'value':NR_CORRS*[0],
                                    'unit':'Singular values of the matrix in use'}
        db[pre + 'InvRSPMatrix-Mon']= {'type':'float','count':MTX_SZ,'value':MTX_SZ*[0],
                                    'unit':'(CH,CV,RF)(urad,Hz) x (BH,BV)(nm)'}
        db[pre + 'CHEnblList-SP']= {'type':'int','count':NR_CH,'value':NR_CH*[1],
                                    'unit':'CHs used in correction',
                                    'fun_set_pv':lambda x: self._set_enbl_list('ch',x)}
        db[pre + 'CHEnblList-RB']= {'type':'int','count':NR_CH,'value':NR_CH*[1],
                                    'unit':'CHs used in correction'}
        db[pre + 'CVEnblList-SP']= {'type':'int','count':NR_CV,'value':NR_CV*[1],
                                    'unit':'CVs used in correction',
                                    'fun_set_pv':lambda x: self._set_enbl_list('cv',x)}
        db[pre + 'CVEnblList-RB']= {'type':'int','count':NR_CV,'value':NR_CV*[1],
                                    'unit':'CVs used in correction'}
        db[pre + 'BPMXEnblList-SP']= {'type':'int','count':NR_BPMS,'value':NR_BPMS*[1],
                                    'unit':'BPMX used in correction',
                                    'fun_set_pv':lambda x: self._set_enbl_list('bpmx',x)}
        db[pre + 'BPMXEnblList-RB']= {'type':'int','count':NR_BPMS,'value':NR_BPMS*[1],
                                    'unit':'BPMX used in correction'}
        db[pre + 'BPMYEnblList-SP']= {'type':'int','count':NR_BPMS,'value':NR_BPMS*[1],
                                    'unit':'BPMY used in correction',
                                    'fun_set_pv':lambda x: self._set_enbl_list('bpmy',x)}
        db[pre + 'BPMYEnblList-RB']= {'type':'int','count':NR_BPMS,'value':NR_BPMS*[1],
                                    'unit':'BPMY used in correction'}
        db[pre + 'RFEnbl-Sel'] = {'type':'enum','enums':self.RF_ENBL_ENUMS,'value':0,
                                    'unit':'If RF is used in correction',
                                    'fun_set_pv':lambda x: self._set_enbl_list('rf',x)}
        db[pre + 'RFEnbl-Sts'] = {'type':'enum','enums':self.RF_ENBL_ENUMS,'value':0,
                                    'unit':'If RF is used in correction'}
        db[pre + 'NumSingValues-SP']= {'type':'int','value':NR_CORRS,'lolim':1, 'hilim':NR_CORRS,
                                    'unit':'Maximum number of SV to use',
                                    'fun_set_pv':self._set_num_sing_values}
        db[pre + 'NumSingValues-RB']= {'type':'int','value':NR_CORRS,'lolim':1, 'hilim':NR_CORRS,
                                    'unit':'Maximum number of SV to use'}
        db[pre + 'CHCalcdKicks-Mon']= {'type':'float','count':NR_CH,'value':NR_CH*[0],'unit':'Last CH kicks calculated.'}
        db[pre + 'CVCalcdKicks-Mon']= {'type':'float','count':NR_CV,'value':NR_CV*[0],'unit':'Last CV kicks calculated.'}
        db[pre + 'RFCalcdKicks-Mon']= {'type':'float','value':1,'unit':'Last RF kick calculated.'}
        return db

    def __init__(self,prefix,callback):
        self.callback = callback
        self.prefix = prefix
        self.select_items = {
            'bpmx':_np.ones(NR_BPMS,dtype=bool),
            'bpmy':_np.ones(NR_BPMS,dtype=bool),
              'ch':_np.ones(NR_CH,  dtype=bool),
              'cv':_np.ones(NR_CV,  dtype=bool),
              'rf':_np.zeros(1,dtype=bool),
            }
        self.selection_pv_names = {
              'ch':'CHEnblList-RB',
              'cv':'CVEnblList-RB',
            'bpmx':'BPMXEnblList-RB',
            'bpmy':'BPMYEnblList-RB',
              'rf':'RFEnbl-Sts',
            }
        self.num_sing_values = NR_CORRS
        self.sing_values = _np.zeros(NR_CORRS,dtype=float)
        self.response_matrix = _np.zeros([2*NR_BPMS,NR_CORRS])
        self.inv_response_matrix = _np.zeros([2*NR_BPMS,NR_CORRS]).T

    def connect(self):
        self._load_response_matrix()

    def set_resp_matrix(self,mat):
        self._call_callback('Log-Mon','Setting New RSP Matrix.')
        if len(mat) != MTX_SZ:
            self._call_callback('Log-Mon','Err: Wrong Size.')
            return False
        mat = _np.reshape(mat,[2*NR_BPMS,NR_CORRS])
        old_ = self.response_matrix.copy()
        self.response_matrix = mat
        if not self._calc_matrices():
            self.response_matrix = old_
            return False
        self._save_resp_matrix(mat)
        self._call_callback('RSPMatrix-RB',list(self.response_matrix.flatten()))
        return True

    def calc_kicks(self,orbit):
        kicks = _np.dot(-self.inv_response_matrix,orbit)
        self._call_callback('CHCalcdKicks-Mon',list(kicks[:NR_CH]))
        self._call_callback('CVCalcdKicks-Mon',list(kicks[NR_CH:NR_CH+NR_CV]))
        self._call_callback('RFCalcdKicks-Mon',kicks[-1])
        return kicks

    def _call_callback(self,pv,value):
        self.callback(self.prefix + pv, value)

    def _set_enbl_list(self,key,val):
        self._call_callback('Log-Mon','Setting {0:s} Enable List'.format(key.upper()))
        copy_ = self.select_items[key]
        new_ = _np.array(val,dtype=bool)
        if key == 'rf':
            new_ = val
        elif len(new_) >= len(copy_):
            new_ = new_[:len(copy_)]
        else:
            new2_ = copy_.copy()
            new2_[:len(new_)] = new_
            new_ = new2
        self.select_items[key] = new_
        if not self._calc_matrices():
            self.select_items[key] = copy_
            return False
        self._call_callback(self.selection_pv_names[key],val)
        return True

    def _calc_matrices(self):
        self._call_callback('Log-Mon','Calculating Inverse Matrix.')
        sel_ = self.select_items
        selecbpm = _np.hstack(  [  sel_['bpmx'],  sel_['bpmy']  ]    )
        seleccor = _np.hstack(  [  sel_['ch'],    sel_['cv'],  sel_['rf']  ]   )
        if not any(selecbpm):
            self._call_callback('Log-Mon','Err: No BPM selected in EnblList')
            return False
        if not any(seleccor):
            self._call_callback('Log-Mon','Err: No Corrector selected in EnblList')
            return False
        sel_mat = selecbpm[:,None] * seleccor[None,:]
        mat = self.response_matrix[sel_mat]
        mat = _np.reshape(mat,[sum(selecbpm),sum(seleccor)])
        try:
            U, s, V = _np.linalg.svd(mat, full_matrices = False)
        except _np.linalg.LinAlgError():
            self._call_callback('Log-Mon','Err: Could not calculate SVD')
            return False
        inv_s = 1/s
        inv_s[self.num_sing_values:] = 0
        Inv_S = _np.diag(inv_s)
        inv_mat = _np.dot(  _np.dot( V.T, Inv_S ),  U.T  )
        isNan = _np.any(  _np.isnan(inv_mat)  )
        isInf = _np.any(  _np.isinf(inv_mat)  )
        if isNan or isInf:
            self._call_callback('Log-Mon','Pseudo inverse contains nan or inf.')
            return False

        self.sing_values[:] = 0
        self.sing_values[:len(s)] = s
        self._call_callback('SingValues-Mon',list(self.sing_values))
        self.inv_response_matrix = _np.zeros([2*NR_BPMS,NR_CORRS]).T
        self.inv_response_matrix[sel_mat.T] = inv_mat.flatten()
        self._call_callback('InvRSPMatrix-Mon',list(self.inv_response_matrix.flatten()))
        return True

    def _set_num_sing_values(self,num):
        copy_ = self.num_sing_values
        self.num_sing_values = num
        if not self._calc_matrices():
            self.num_sing_values = copy_
            return False
        self._call_callback('NumSingValues-RB',num)
        return True

    def _load_response_matrix(self):
        filename = self.RSP_MTX_FILENAME+self.EXT
        if _os.path.isfile(filename):
            copy_ = self.response_matrix.copy()
            self.response_matrix = _np.loadtxt(filename)
            if not self._calc_matrices():
                self.response_matrix = copy_
                return
            self._call_callback('Log-Mon','Loading RSP Matrix from file.')
            self._call_callback('RSPMatrix-RB',list(self.response_matrix.flatten()))

    def _save_resp_matrix(self, mat):
        self._call_callback('Log-Mon','Saving RSP Matrix to file')
        _np.savetxt(self.RSP_MTX_FILENAME+self.EXT,mat)


class Correctors:
    SLOW_REF = 0
    SLOW_REF_SYNC = 1

    def get_database(self):
        db = dict()
        pre = self.prefix
        db[pre + 'CHStrength-SP'] = {'type':'float','value':0,'unit':'%','lolim':-1000, 'hilim':1000,
                                    'prec':2, 'fun_set_pv':lambda x:self._set_strength('ch',x)}
        db[pre + 'CHStrength-RB'] = {'type':'float','value':0,'prec':2, 'unit':'%'}
        db[pre + 'CVStrength-SP'] = {'type':'float','value':0,'unit':'%','lolim':-1000, 'hilim':1000,
                                    'prec':2, 'fun_set_pv':lambda x:self._set_strength('cv',x)}
        db[pre + 'CVStrength-RB'] = {'type':'float','value':0,'prec':2, 'unit':'%'}
        db[pre + 'RFStrength-SP'] = {'type':'float','value':0,'unit':'%','lolim':-1000, 'hilim':1000,
                                    'prec':2, 'fun_set_pv':lambda x:self._set_strength('rf',x)}
        db[pre + 'RFStrength-RB'] = {'type':'float','value':0,'prec':2, 'unit':'%'}
        db[pre + 'MaxKickStrength-SP'] =  {'type':'float','value':300,'unit':'urad','lolim':0, 'hilim':1000,
                                    'prec':3, 'fun_set_pv':self._set_max_kick}
        db[pre + 'MaxKickStrength-RB'] = {'type':'float','value':300,'prec':2, 'unit':'urad'}
        db[pre + 'SyncKicks-Sel'] = {'type':'enum','enums':('Off','On'),'value':1,
                                     'fun_set_pv':self._set_corr_pvs_mode}
        db[pre + 'SyncKicks-Sts'] = {'type':'enum','enums':('Off','On'),'value':1}
        return db

    def __init__(self,prefix,callback):
        self.callback = callback
        self.prefix = prefix
        self.strengths = {  'ch':0.0, 'cv':0.0, 'rf':0.0  }
        self.sync_kicks = True
        self._max_kick = 300
        self.corr_pvs_opmode_sel = list()
        self.corr_pvs_opmode_sts = list()
        self.corr_pvs_opmode_ready = dict()
        self.corr_pvs_sp = list()
        self.corr_pvs_rb = list()
        self.corr_pvs_ready = dict()

    def connect(self):
        ch_names = _PSSearch.get_psnames({'section':'SI','discipline':'PS','device':'CH'})
        cv_names = _PSSearch.get_psnames({'section':'SI','discipline':'PS','device':'CV'})
        self.corr_names = ch_names + cv_names

        for dev in self.corr_names:
            self.corr_pvs_opmode_sel.append(_epics.PV(LL_PREF+dev+':OpMode-Sel',
                                                      connection_timeout=_TIMEOUT))
            self.corr_pvs_opmode_sts.append(_epics.PV(LL_PREF+dev+':OpMode-Sts',
                                                      connection_timeout=_TIMEOUT,
                                                      callback=self._corrIsOnMode))
            self.corr_pvs_opmode_ready[LL_PREF+dev+':OpMode-Sts'] = False
            self.corr_pvs_sp.append(_epics.PV(LL_PREF+dev+':Current-SP',
                                              connection_timeout=_TIMEOUT,))
            self.corr_pvs_rb.append(_epics.PV(LL_PREF+dev+':Current-RB',
                                              connection_timeout=_TIMEOUT,
                                              callback=self._corrIsReady))
            self.corr_pvs_ready[LL_PREF+dev+':Current-RB'] = False
        self.rf_pv_sp = _epics.PV(LL_PREF+SECTION + '-Glob:RF-P5Cav:Freq-SP')
        self.rf_pv_rb = _epics.PV(LL_PREF+SECTION + '-Glob:RF-P5Cav:Freq-RB')
        self.event_pv_mode_sel = _epics.PV(SECTION + '-Glob:TI-Event:OrbitMode-Sel')
        self.event_pv_sp = _epics.PV(SECTION + '-Glob:TI-Event:OrbitExtTrig-Cmd')

    def apply_kicks(self,values, limit=False):
        streng = self.strengths.copy()
        if limit:
            maxh = _np.argmax(_np.abs(values[:NR_CH]))
            maxv = _np.argmax(_np.abs(values[NR_CH:-1]))
            maxi = self._max_kick
            if maxh*streng['ch'] > maxi:
                streng['ch'] = min(maxi/maxh,1.0)
                self._call_callback('Log-Mon','Warn: CH > max. Using {0:6.2f}%'.format(streng['ch']*100))
            if maxv*streng['cv'] > maxi:
                streng['cv'] = min(maxi/maxv,1.0)
                self._call_callback('Log-Mon','Warn: CV > max. Using {0:6.2f}%'.format(streng['cv']*100))
        #apply the RF kick
        if values[-1]:
            if self.rf_pv_sp.connected:
                self.rf_pv_sp.value = self.rf_pv_sp.value + streng['rf']*values[-1]
            else:
                self._call_callback('Log-Mon','PV '+self.rf_pv_sp.pvname+' Not Connected.')
        #Send correctors setpoint
        for i, pv in enumerate(self.corr_pvs_sp):
            pvname = pv.pvname.replace('-SP','-RB')
            self.corr_pvs_ready[pvname] = True
            if not values[i]: continue
            if not pv.connected:
                self._call_callback('Log-Mon','Err: PV '+pv.pvname+' Not Connected.')
                return
            plane = 'ch' if i>=NR_CH else 'cv'
            self.corr_pvs_ready[pvname] = False
            pv.value += streng[plane] * values[i]
        #Wait for readbacks to be updated
        for i in range(NUM_TIMEOUT):
            if all(self.corr_pvs_ready.values()): break
            _time.sleep(TINY_INTERVAL)
        else:
            self._call_callback('Log-Mon','Err: Timeout waiting Correctors PVs')
            return
        #Send trigger signal for implementation
        if self.sync_kicks:
            if self.event_pv_sp.connected:
                self.event_pv_sp.value = 1
            else:
                self._call_callback('Log-Mon','Kicks not sent, Timing PV Disconnected.')

    def _call_callback(self,pv,value):
        self.callback(self.prefix + pv, value)

    def _set_max_kick(self,value):
        self._max_kick = float(value)
        self._call_callback('MaxKickStrength-RB', float(value))

    def _set_strength(self,plane,value):
        self.strengths[plane] = value/100
        self._call_callback('Log-Mon','Setting {0:s} Strength to {1:6.2f}'.format(plane.upper(),value))
        self._call_callback(plane.upper() + 'Strength-RB', value)
        return True

    def _set_corr_pvs_mode(self,value):
        self.sync_kicks = True if value else False
        val = self.SLOW_REF_SYNC if self.sync_kicks else self.SLOW_REF
        for pv in self.corr_pvs_opmode_sel:
            if pv.connected:
                pv.value = val
        self._call_callback('Log-Mon','Setting Correctors PVs to {0:s} Mode'.format('Sync' if value else 'Async'))
        self._call_callback('SyncKicks-Sts', value)
        return True

    def _corrIsReady(self,pvname,value,**kwargs):
        ind = self.corr_names.index(pvname.strip(LL_PREF).strip(':Current-RB'))
        if abs(self.corr_pvs_sp[ind].value - value) <= 1e-3:
            self.corr_pvs_ready[pvname] = True

    def _corrIsOnMode(self,pvname,value,**kwargs):
        val = self.SLOW_REF_SYNC if self.sync_kicks else self.SLOW_REF
        self.corr_pvs_opmode_ready[pvname] = (value == val)
        if all(self.corr_pvs_opmode_ready.values()):
            self._call_callback('SyncKicks-Sts',val == self.SLOW_REF_SYNC)
