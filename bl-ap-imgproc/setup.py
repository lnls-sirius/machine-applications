#!/usr/bin/env python-sirius

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='bl-ap-imgproc',
    version=__version__,
    author='lnls-sirius',
    description='IOC for DVF Beamline image processing.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['bl_ap_imgproc'],
    package_data={'bl_ap_imgproc': ['VERSION']},
    include_package_data=True,
    scripts=['scripts/sirius-ioc-bl-ap-imgproc.py'],
    zip_safe=False
)
