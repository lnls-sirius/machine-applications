from epics import caget as _caget
from epics import caput as _caput
import re
import threading
import sys
from os.path import exists as _exists
from os.path import basename as _basename
from os import remove as _remove
from os import rename as _rename
import os
import glob
import shutil
from datetime import datetime as _date
from time import sleep as _sleep

#os.environ['EPICS_CA_ADDR_LIST'] = '127.0.0.1'
#os.environ['EPICS_CA_AUTO_ADDR_LIST'] = 'NO'

_TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"

def restore_after_delay(req_file, pv_prefix='', save_location='', delay=10.0):
    _sleep(delay)
    restore_pvs(req_file, pv_prefix, save_location)

def restore_pvs(req_file, pv_prefix='', save_location=''):
    if not str(req_file).endswith('.req'):
        raise RuntimeError('Save-restore: Error. File must end with .req')
    filename = _basename(req_file.rstrip('.req'))
    if save_location != '':
        save_location = save_location.rstrip('/')
        save_location = save_location.rstrip('\\')
    # find most recent save file
    max_timestamp = _date.min
    save_file = ''
    for f_name in glob.glob(save_location+'/'+filename+'*'+'.sav*'):
        canditate_file = _basename(f_name)
        #search_res = re.search(filename+'__(.*)__*', canditate_file)
        #timestamp_str = search_res.group(1)
        timestamp_str = canditate_file.split('__')[1]
        timestamp = _date.strptime(timestamp_str, _TIMESTAMP_FORMAT)
        if timestamp > max_timestamp:
            save_file = f_name
    if save_file != '':
        with open(save_file, 'r') as f:
            lines = f.readlines()
            for l in lines:
                try:
                    if l == '':
                        continue
                    if l[0] == '#':
                        continue
                    l_str = l.replace('\n','').replace('\r','')
                    l_data = l_str.split(' ')
                    pv_name = l_data[0]
                    pv_val = l_data[1]
                    if bool(re.fullmatch(r'[a-zA-Z0-9:_-]*', pv_name)):
                        _caput(pv_prefix+pv_name, pv_val)
                except Exception:
                    print('Save-restore: Failed to restore PV {}'.format(pv_prefix+pv_name))
    else:
        print('Save-restore: No file found for restoration')

def save_monitor_with_delay(req_file, pv_prefix='', save_location='', period=10.0, num_backup_files=10, delay=10.0):
    _sleep(delay)
    save_monitor(req_file, pv_prefix, save_location, period, num_backup_files)

def save_monitor(req_file, pv_prefix='', save_location='', period=10.0, num_backup_files=10):
    if not str(req_file).endswith('.req'):
        print('Save-restore: Error. File must end with .req')
        sys.exit()
    _now = _date.now().strftime(_TIMESTAMP_FORMAT)
    filename = _basename(req_file.rstrip('.req'))
    if save_location != '':
        save_location = save_location.rstrip('/')
        save_location = save_location.rstrip('\\')
    # remove oldest file if backup count exceeded
    save_list = sorted(glob.glob(save_location+'/'+filename+'*'+'.sav*'))
    if len(save_list) >= num_backup_files:
        _remove(save_list[0])
    # define new save file name
    save_file = (
        req_file.rstrip('.req') + '__' + _now + '__.sav'
        )
    backup_file = save_file.rstrip('.sav')+'_Backup.sav'
    eid = threading.Event()
    pv_list = []
    # read request file
    try:
        with open(req_file, 'r') as f:
            lines = f.readlines()
            for l in lines:
                if l == '':
                    continue
                if l[0] == '#':
                    continue
                pvname = l.replace('\n','').replace('\r','').replace(' ','')
                if bool(re.fullmatch(r'[a-zA-Z0-9:_-]*', pvname)):
                    pv_list.append(pvname)
                else:
                    print('Save-restore: Invalid name for PV {}'.format(pvname))
    except Exception:
        raise RuntimeError('Save-restore: Failed to read save request file')
    # create save file
    try:
        with open(save_file, 'w+') as f:
            for pvname in pv_list:
                try:
                    pv_val = _caget(pv_prefix+pvname, as_string=True)
                    f.write(pvname+' '+pv_val+'\n')
                except Exception:
                    print('Save-restore: Failed to save PV {}'.format(pv_prefix+pvname))
    except Exception:
        raise RuntimeError('Save-restore: Failed to create save file')
    # update save file periodically
    while True:
        eid.wait(period)
        try:
            # if backup file exists, keep it for now
            # otherwise, create backup
            if not _exists(backup_file):
                shutil.copyfile(save_file, backup_file)
            # save PVs from list
            all_pvs_updated = True
            with open(save_file, 'w+') as f:
                for pvname in pv_list:
                    try:
                        pv_val = _caget(pv_prefix+pvname, as_string=True, use_monitor=False)
                    except Exception:
                        all_pvs_updated = False
                        print(
                            'Save-restore: Failed to caget PV {}'.format(pv_prefix+pvname))
                    else:
                        # write pv value to file
                        f.write(pvname+' '+pv_val+'\n')
            # erase backup file if save file
            # is fully up-to-date
            if _exists(backup_file) and all_pvs_updated:
                _remove(backup_file)
        except Exception:
            print('Save-restore: Error while trying to update save file')
