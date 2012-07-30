#!/usr/bin/env python
from setuptools import setup

dependencies = [
    'django==1.3.1',
    'resty',
]

dependency_links = [
    'http://username:password@github.com/pbs/resty/tarball/master#egg=resty',
]

setup(
    name='bluebell',
    version='0.1',
    description='Sodor API consumer.',
    author='TPG CORE Services Team',
    author_email='tpg-pbs-coreservices@threepillarglobal.com',
    url='https://github.com/pbs/bluebell',
    install_requires=dependencies,
    dependency_links = dependency_links,
)
