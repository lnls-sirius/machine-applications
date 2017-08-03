"""Select PVs and create IOC Database.

get_ma_devices
    Function to get magnet devices belonging to the sirius IOC
get_pvs_database
    Function that builds the IOC database
"""
from siriuspy.search import MASearch as _MASearch
from siriuspy.search import PSSearch as _PSSearch
from siriuspy.magnet.model import MagnetFactory
from siriuspy.envars import vaca_prefix as _vaca_prefix


with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

_connection_timeout = None

_PREFIX_VACA = _vaca_prefix
_PREFIX = 'TS-'

_ma_devices = None


def get_ma_devices():
    """Create/Return PowerSupplyMA objects for each magnet."""
    global _ma_devices, _PREFIX
    if _ma_devices is None:
        _ma_devices = {}
        # Create filter, only getting Fam Quads
        filters = [
            dict(
                section="TS"
            )
        ]
        # Get magnets
        magnets = _MASearch.get_manames(filters)
        for magnet in magnets:
            _, device = magnet.split(_PREFIX)

            # Get dipole object
            dipole = MagnetFactory.get_dipole(magnet)
            if dipole:
                _, dipole_name = dipole.split(_PREFIX)
                if dipole_name not in _ma_devices:
                    raise KeyError("Dipole not created yet!")
                dipole = _ma_devices[dipole_name]

            # Get family magnet object
            fam = MagnetFactory.get_fam(magnet)
            if fam:
                _, fam_name = fam.split(_PREFIX)
                if fam_name not in _ma_devices:
                    raise KeyError(
                        "Family magnet {} not created yet!".format(magnet))
                fam = _ma_devices[fam_name]

            # Create proper magnet object with the proper dipole and family
            # references
            _ma_devices[device] = MagnetFactory.factory(maname=magnet,
                                                        dipole=dipole,
                                                        fam=fam,
                                                        use_vaca=True)
    return _ma_devices


def get_pvs_database():
    """Return IOC dagtabase."""
    pv_database = {'IOC:Version-Cte': {'type': 'str', 'value': __version__}}
    ma_devices = get_ma_devices()
    for device_name, ma_device in ma_devices.items():
        # for ps_name in ma_device.ps_names:
        pv_database.update(ma_device._get_database(device_name))
    return pv_database