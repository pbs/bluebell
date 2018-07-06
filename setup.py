#!/usr/bin/env python
from setuptools import setup

dependencies = [
    'django==1.4.1',
    'python-dateutil==2.1',
    'requests==0.13.9',
    'resty==0.1',
    'six==1.2.0',
]


setup(
    name='bluebell',
    version='0.2',
    description='Sodor API consumer.',
    author='TPG CORE Services Team',
    author_email='tpg-pbs-coreservices@threepillarglobal.com',
    url='https://github.com/pbs/bluebell',
    install_requires=dependencies,
)
