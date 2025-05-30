#!/usr/bin/env python-sirius
"""Package installer."""

from setuptools import find_packages, setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='si-di-fpmosc',
    version=__version__,
    author='lnls-sirius',
    description='Soft IOC for Electron Beam Filling Pattern Informations.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='MIT License',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=find_packages(),
    package_data={'si_di_fpmosc': ['VERSION']},
    include_package_data=True,
    scripts=[
        'scripts/sirius-ioc-si-di-fpmosc.py',
        ],
    zip_safe=False
)
