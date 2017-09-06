#!/usr/bin/env python-sirius
"""Package installer."""

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='as-ap-opmode',
    version=__version__,
    author='lnls-sirius',
    description='IOC for Accelerator Operation Mode.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['as_ap_opmode'],
    package_data={'as_ap_opmode': ['VERSION']},
    scripts=['scripts/sirius-ioc-as-ap-opmode.py',
            ],
    zip_safe=False
)
