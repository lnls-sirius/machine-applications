#!/usr/bin/env python-sirius
"""Package installer."""

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='as-ap-opticscorr',
    version=__version__,
    author='lnls-sirius',
    description='IOCs for High Level Control of Booster Tune and Chromaticity Correction.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['as_ap_opticscorr'],
    package_data={'as_ap_opticscorr': ['VERSION'], },
    scripts=['scripts/sirius-ioc-bo-ap-opticscorr-tune.py',
             'scripts/sirius-ioc-bo-ap-opticscorr-chrom.py',
             ],
    zip_safe=False
)
