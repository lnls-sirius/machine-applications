#!/usr/bin/env python-sirius

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='li-di-charge',
    version=__version__,
    author='lnls-sirius',
    description='IOC for Linac charge reading from oscilloscopy.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['li_di_charge'],
    package_data={'li_di_charge': ['VERSION']},
    include_package_data=True,
    scripts=['scripts/sirius-ioc-li-di-charge.py'],
    zip_safe=False
)
