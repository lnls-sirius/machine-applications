#!/usr/bin/env python3

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

with open('README.md', 'r') as _f:
    _long_description = _f.read().strip()

with open('requirements.txt', 'r') as _f:
    _requirements = _f.read().strip().split('\n')

setup(
    name='as_ap_injbeamdiag',
    version=__version__,
    author='lnls-sirius',
    description='PROJECT-DESCRIPTION',
    long_description=_long_description,
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license="GPL-3.0",
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['as_ap_injbeamdiag'],
    install_requires=_requirements,
    package_data={'as_ap_injbeamdiag': ['VERSION']},
    include_package_data=True,
    scripts=[
        'scripts/sirius-ioc-as-ap-injbeamdiag.py',
    ],
    zip_safe=False
)
