#!/usr/bin/env python-sirius
"""Package installer."""

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='si-ap-fofb',
    version=__version__,
    author='lnls-sirius',
    description='IOC for High Level FOFB Control.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['si_ap_fofb'],
    package_data={'si_ap_fofb': ['VERSION']},
    include_package_data=True,
    scripts=['scripts/sirius-ioc-si-ap-fofb.py', ],
    zip_safe=False
)
