#!/usr/bin/env python-sirius

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='li-ap-energy',
    version=__version__,
    author='lnls-sirius',
    description='IOC for Linac Energy measurement for Sirius.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['li_ap_energy'],
    package_data={'li_ap_energy': ['VERSION']},
    include_package_data=True,
    scripts=['scripts/sirius-ioc-li-ap-energy.py'],
    zip_safe=False
)
