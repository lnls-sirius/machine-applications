#!/usr/bin/env python-sirius
"""Setup Module."""

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='as-ap-sofb',
    version=__version__,
    author='lnls-sirius',
    description='Slow Orbit Feedback System for Sirius',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['as_ap_sofb'],
    package_data={'as_ap_sofb': ['VERSION']},
    include_package_data=True,
    scripts=['scripts/sirius-ioc-si-ap-sofb.py',
             'scripts/sirius-ioc-bo-ap-sofb.py',
             'scripts/sirius-ioc-tb-ap-sofb.py',
             'scripts/sirius-ioc-ts-ap-sofb.py',
             ],
    zip_safe=False
)
