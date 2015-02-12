#!/usr/bin/env python

from setuptools import setup, find_packages
import os

SCRIPTS = [os.path.join('bin', n) for n in [
    'debops', 'debops-init', 'debops-task',
    'debops-defaults', 'debops-padlock', 'debops-update']]
           # 'padlock.py'

README = open('README.rst').read()

setup(
    name = "debops",
    version = "0.4.0",
    install_requires = ['netaddr', 'argparse'],

    scripts = ['bin/debops',
               'bin/debops-defaults',
               'bin/debops-init',
               'bin/debops-padlock',
               'bin/debops-task',
               'bin/debops-update'],

    packages = find_packages(exclude=['tests']),
    package_data = {
        'debops': ['padlock-script'],
        },

    # metadata for upload to PyPI
    author = "DebOps Project",
    author_email = "debops@groups.io",
    description = "Your Debian-based data center in a box.",
    long_description = README,
    license = "GPL 3.0",
    keywords = "ansible",
    url          = "http://debops.org/",
    download_url = "https://github.com/debops/debops/archive/v0.4.0.tar.gz",
    classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: System :: Systems Administration',
    ],

    # these are for easy_install (used by bdist_*)
    zip_safe = True,
#    entry_points = {
#        "console_scripts": [
#            "debops = debops.cmds.main:run",
#        ],
#    },
)
