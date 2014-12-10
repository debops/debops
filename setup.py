#!/usr/bin/env python

#import ez_setup
#ez_setup.use_setuptools()

from setuptools import setup, find_packages
import os

SCRIPTS = [os.path.join('bin', n) for n in [
    'debops', 'debops-init', 'debops-task',
    'debops-defaults', 'debops-padlock', 'debops-update']]
           # 'padlock.py'

README = open('README.rst').read()

setup(
    name = "debops",
    version = "0.1dev",
    install_requires = ['netaddr'],

    packages=find_packages('lib', exclude=['ez_setup']),

    package_data = {
        #'debops': ['padlock.sh'],
        },

    # metadata for upload to PyPI
    author = "Hartmut Goebel",
    author_email = "h.goebel@crazy-compilers.com",
    description = "Your Debian-based data center in a box.",
    long_description = README,
    license = "GPL 3.0",
    keywords = "ansible",
    url          = "http://debops.org//",
    download_url = "https://github.io/debos/debops/",
    classifiers = [
    'Development Status :: 1 - Alpha',
    'Environment :: Console',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Utilities',
    ],

    # these are for easy_install (used by bdist_*)
    zip_safe = True,
#    entry_points = {
#        "console_scripts": [
#            "debops = debops.cmds.main:run",
#        ],
#    },
)
