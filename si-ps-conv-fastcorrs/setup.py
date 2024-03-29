#!/usr/bin/env python-sirius
"""Package installer."""

from setuptools import setup

with open('VERSION', 'r') as _f:
    __version__ = _f.read().strip()

with open('requirements.txt', 'r') as _f:
    _requirements = _f.read().strip().split('\n')


setup(
    name='si-ps-conv-fastcorrs',
    version=__version__,
    author='lnls-sirius',
    description='Conv IOC for Fast Corrector Power Supplies.',
    url='https://github.com/lnls-sirius/machine-applications',
    download_url='https://github.com/lnls-sirius/machine-applications',
    license='GNU GPLv3',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'
    ],
    packages=['si_ps_conv_fastcorrs'],
    package_data={'si_ps_conv_fastcorrs': ['VERSION']},
    install_requires=_requirements,
    include_package_data=True,
    scripts=['scripts/sirius-ioc-si-ps-conv-fastcorrs.py'],
    zip_safe=False
)
