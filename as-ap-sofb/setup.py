#!/usr/bin/env python-sirius
"""Setup Module."""

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='SOFB',
    version=__version__,
    author='lnls-sirius',
    description='Slow Orbit Feedback System for Sirius',
    url='PROJECT-URL',
    download_url='PROJECT-DOWNLOAD-URL',
    license='MIT License',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['as_ap_sofb'],
    package_data={'as_ap_sofb': []},
    scripts=['scripts/sirius-ioc-si-ap-sofb.py',
             'scripts/sirius-ioc-bo-ap-sofb.py',
             'scripts/sirius-ioc-tb-ap-orbit.py',
             'scripts/sirius-ioc-ts-ap-orbit.py',
             ],
    zip_safe=False
)
