#!/usr/bin/env python-sirius
"""Package installer."""

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

with open('requirements.txt', 'r') as _f:
    _requirements = _f.read().strip().split('\n')


setup(
    name='si-id-epu50',
    version=__version__,
    author='lnls-sirius',
    description='IOC for EPU50 Insertion Device.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['si_id_epu50'],
    package_data={'si_id_epu50':
        ['VERSION', 'config/config.toml', 'config/drive_messages.yaml']},
    install_requires=_requirements,
    include_package_data=True,
    scripts=['scripts/sirius-ioc-si-id-epu50.py'],
    zip_safe=False
)
