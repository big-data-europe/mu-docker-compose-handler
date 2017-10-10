#!/usr/bin/env python3
# This file is necessary to allow tox to execute

import os

from setuptools import setup, find_packages

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

version = None
exec(open('mudrchandler/__init__.py').read())

with open('./requirements.txt') as reqs_txt:
    requirements = list(iter(reqs_txt))


with open('./test-requirements.txt') as test_reqs_txt:
    test_requirements = list(iter(test_reqs_txt))


setup(
    name="mudrchandler",
    version=version,
    description="A microservice that downloads a docker-compose.yml file from a git repo and stores it in a database",
    url='https://github.com/big-data-europe/mu-docker-compose-handler',
    packages=find_packages(exclude=["tests.*", "tests"]),
    install_requires=requirements,
    tests_require=test_requirements,
    zip_safe=False,
    test_suite='tests',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
    ],
    maintainer='Esteban Sastre',
    maintainer_email='esteban.s.f0@gmail.com',
)

