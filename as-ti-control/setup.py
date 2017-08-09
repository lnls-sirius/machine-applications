#!/usr/bin/env python-sirius

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

setup(
    name='as-ti-control',
    version=__version__,
    author='lnls-sirius',
    description='IOC for High Level control of Sirius Timing System.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='MIT License',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['as_ti_control'],
    package_data={'as_ti_control': ['VERSION']},
    scripts=['scripts/sirius-ioc-as-ti-control.py'],
    zip_safe=False
)
