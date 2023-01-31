#!/usr/bin/env python-sirius
"""Package installer."""

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='si-ap-stabinfo',
    version=__version__,
    author='lnls-sirius',
    description='IOC for beam stability indicators.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['si_ap_stabinfo'],
    package_data={'si_ap_stabinfo': ['VERSION']},
    include_package_data=True,
    scripts=['scripts/sirius-ioc-si-ap-stabinfo.py', ],
    zip_safe=False
)
