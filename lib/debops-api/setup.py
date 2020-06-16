#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.core import setup

version = None
with open('debops/api.py') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.replace("'", '').split()[2]
            break

setup(
    name='debops-api',
    description='Machine readable metadata about the DebOps Project',
    version=version,
    author='Robin Schneider',
    author_email='ypid@riseup.net',
    url='https://github.com/debops/debops-api',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: DFSG approved'
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Documentation',
    ),
)
