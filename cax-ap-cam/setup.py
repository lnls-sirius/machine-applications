#!/usr/bin/env python-sirius

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='cax-ap-cam',
    version=__version__,
    author='lnls-sirius',
    description='IOC for Carcará X Beamline image processing.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['cax_ap_cam'],
    package_data={'cax_ap_cam': ['VERSION']},
    include_package_data=True,
    scripts=['scripts/sirius-ioc-cax-ap-cam.py'],
    zip_safe=False
)
