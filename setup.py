#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2014-2019 Hartmut Goebel <h.goebel@crazy-compilers.com>
# Copyright (C) 2014-2020 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2016      Robin Schneider <ypid@riseup.net>
# Copyright (C) 2014-2020 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

# Installation in development mode:
#   pip3 install --user --editable .

from setuptools import setup, find_packages
import subprocess
import glob
import os
import re


def find_files(directory, strip):
    """
    Using glob patterns in ``package_data`` that matches a directory can
    result in setuptools trying to install that directory as a file and
    the installation to fail.

    This function walks over the contents of *directory* and returns a list
    of only filenames found. The filenames will be stripped of the *strip*
    directory part to allow for location relative to the package.
    """

    result = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if not filename.endswith('.pyc'):
                filename = os.path.join(root, filename)
                result.append(os.path.relpath(filename, strip))
    return result


try:
    import pypandoc
    README = pypandoc.convert_file('README.md', 'rst')
except (IOError, ImportError):
    print('Warning: The "pandoc" support is required to convert '
          'the README.md to reStructuredText format')
    README = open('README.md').read()

try:
    unicode
except NameError:
    # Required for Python 3.x
    class unicode(object):
        def __new__(cls, s):
            if isinstance(s, str):
                return s
            return s and s.decode('utf-8') or None

# Retrieve the project version from 'git describe' command and store it in the
# __version__.py and VERSION files, needed for correct installation of the
# Python package
try:
    with open(os.devnull, 'w') as devnull:
        RELEASE = subprocess.check_output(
                ['git', 'describe'], stderr=devnull
                ).strip().lstrip(b'v').decode('utf-8')
except subprocess.CalledProcessError:
    try:
        RELEASE = open('VERSION').read().strip()
    except Exception:
        try:
            with open('CHANGELOG.rst', 'r') as changelog:
                for count, line in enumerate(changelog):
                    if re.search('^`debops v', line):
                        RELEASE = line.split()[1].rstrip('`_').lstrip('v')
                        break
        except Exception:
            RELEASE = '0.0.0'

with open('VERSION', 'w') as version_file:
    version_file.write('{}\n'.format(RELEASE))
with open('src/debops/__version__.py', 'w') as version_file:
    version_file.write('__version__ = "{}"\n'
                       .format(RELEASE))

MANPAGES_1 = []
MANPAGES_5 = []
if os.path.exists('docs/_build/man'):
    for manpage in os.listdir('docs/_build/man'):
        if os.path.isfile(os.path.join('docs/_build/man', manpage)):
            if manpage.endswith('.1'):
                MANPAGES_1.append(os.path.join('docs/_build/man', manpage))
            elif manpage.endswith('.5'):
                MANPAGES_5.append(os.path.join('docs/_build/man', manpage))
else:
    print('Warning: manual pages not built')

setup(
    install_requires=['distro', 'future', 'jinja2', 'pyyaml',
                      'pyxdg', 'toml', 'python-dotenv'],
    extras_require={
        'ansible': ['ansible', 'netaddr', 'passlib',
                    'python-ldap', 'dnspython', 'pyopenssl']
    },
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=('tests', 'docs')),
    data_files=[
        ('share/man/man1', MANPAGES_1),
        ('share/man/man5', MANPAGES_5),
    ],
    package_data={
        'debops':
            find_files('src/debops/_data',
                       'src/debops')
    },

    include_package_data=True,
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'debops = debops.__main__:main'
        ]
    },

    # metadata for upload to PyPI
    name='debops',
    version=unicode(RELEASE),
    description='Your Debian-based data center in a box',
    long_description=README,
    author='DebOps Developers',
    author_email='debops-devel@lists.debops.org',
    url='https://debops.org/',
    license="GPL-3.0-or-later",
    license_files=glob.glob("LICENSES/*.txt"),
    keywords="ansible debian sysadmin",
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, '
                    '!=3.3.*, !=3.4.*, <4',
    download_url='https://github.com/debops/debops'
                 '/archive/v' + unicode(RELEASE) + '.tar.gz',
    classifiers=[
                'Development Status :: 5 - Production/Stable',
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
                'Programming Language :: Python :: 3.7',
                'Programming Language :: Python :: 3.8',
                'Programming Language :: Python :: 3.9',
                'Topic :: System :: Installation/Setup',
                'Topic :: System :: Systems Administration',
                'Topic :: Utilities'
    ]
)
