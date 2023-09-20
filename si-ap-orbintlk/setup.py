#!/usr/bin/env python-sirius
"""Package installer."""

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='si-ap-orbintlk',
    version=__version__,
    author='lnls-sirius',
    description='IOC for Global Orbit Interlock Control.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['si_ap_orbintlk'],
    package_data={'si_ap_orbintlk': ['VERSION']},
    include_package_data=True,
    scripts=['scripts/sirius-ioc-si-ap-orbintlk.py', ],
    zip_safe=False
)
