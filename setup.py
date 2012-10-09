#!/usr/bin/env python
from setuptools import setup

dependencies = [
    'django==1.4.1',
]


setup(
    name='bluebell',
    version='0.1',
    description='Sodor API consumer.',
    author='TPG CORE Services Team',
    author_email='tpg-pbs-coreservices@threepillarglobal.com',
    url='https://github.com/pbs/bluebell',
    install_requires=dependencies,
)
