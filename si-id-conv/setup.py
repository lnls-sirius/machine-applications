#!/usr/bin/env python-sirius
"""Package installer."""

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

with open('requirements.txt', 'r') as _f:
    _requirements = _f.read().strip().split('\n')


setup(
    name='si-id-conv',
    version=__version__,
    author='lnls-sirius',
    description='IOC Conv for Insertion Devices.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['si_id_conv'],
    package_data={'si_id_conv': ['VERSION']},
    install_requires=_requirements,
    include_package_data=True,
    scripts=['scripts/sirius-ioc-si-id-conv.py'],
    zip_safe=False
)
