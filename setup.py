#!/usr/bin/env python

from setuptools import setup, find_packages
import os

try:
    import pypandoc
    README = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    README = open('README.md').read()

SCRIPTS = [os.path.join('bin', n) for n in [
    'debops', 'debops-init', 'debops-task',
    'debops-defaults', 'debops-padlock', 'debops-update']]

README = open('README.md').read()

RELEASE = os.popen('git describe').read().strip().lstrip('v')

setup(
    name="debops",
    version=RELEASE,
    install_requires=['netaddr', 'argparse', 'passlib', 'ansible'],

    scripts=SCRIPTS,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,

    # metadata for upload to PyPI
    author="DebOps Developers",
    author_email="debops-users@lists.debops.org",
    description="Your Debian-based data center in a box",
    long_description=README,
    license="GPL-3.0",
    keywords="ansible",
    url="https://debops.org/",
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4',
    download_url="https://github.com/debops/debops"
                 "/archive/v" + RELEASE + ".tar.gz",
    classifiers=[
                 'Development Status :: 4 - Beta',
                 'Environment :: Console',
                 'Intended Audience :: Information Technology',
                 'Intended Audience :: System Administrators',
                 'License :: OSI Approved :: GNU General Public License v3 '
                 'or later (GPLv3+)',
                 'Natural Language :: English',
                 'Operating System :: POSIX',
                 'Programming Language :: Other Scripting Engines',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Topic :: System :: Installation/Setup',
                 'Topic :: System :: Systems Administration',
                 'Topic :: Utilities'
    ],

    # these are for easy_install (used by bdist_*)
    zip_safe=True
    #    entry_points = {
    #        "console_scripts": [
    #            "debops = debops.cmds.main:run",
    #        ],
    #    },
)
