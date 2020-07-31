#!/usr/bin/env python-sirius

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='si-ap-manaca',
    version=__version__,
    author='lnls-sirius',
    description='IOC for Manaca Image Processing.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['si_ap_manaca'],
    package_data={'si_ap_manaca': ['VERSION']},
    include_package_data=True,
    scripts=['scripts/sirius-ioc-si-ap-manaca.py'],
    zip_safe=False
)
