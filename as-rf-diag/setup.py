#!/usr/bin/env python-sirius
"""Setup Module."""

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

with open('requirements.txt', 'r') as _f:
    _requirements = _f.read().strip().split('\n')


setup(
    name='as-rf-diag',
    version=__version__,
    author='lnls-sirius',
    description='RF diagnostics',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['as_rf_diag'],
    package_data={'as_rf_diag': ['VERSION']},
    install_requires=_requirements,
    include_package_data=True,
    scripts=['scripts/sirius-ioc-as-rf-diag.py',
             ],
    zip_safe=False
)
