#!/usr/bin/env python-sirius
"""Package installer."""

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='si-ap-idff',
    version=__version__,
    author='lnls-sirius',
    description='IOC for ID feedforward.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['si_ap_idff'],
    package_data={'si_ap_idff': ['VERSION']},
    include_package_data=True,
    scripts=['scripts/sirius-ioc-si-ap-idff.py', ],
    zip_safe=False
)
