#!/usr/bin/env python

from setuptools import setup, find_packages
import os
import re
import subprocess

try:
    import pypandoc
    README = pypandoc.convert_file('README.md', 'rst')
except(IOError, ImportError):
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

SCRIPTS = [os.path.join('bin', n) for n in [
    'debops', 'debops-init', 'debops-task',
    'debops-defaults', 'debops-padlock', 'debops-update']]

# Retrieve the project version from 'git describe' command and store it in the
# VERSION file, needed for correct installation of the Python package
try:
    with open(os.devnull, 'w') as devnull:
        RELEASE = subprocess.check_output(
                ['git', 'describe'], stderr=devnull
                ).strip().lstrip(b'v')
    with open('VERSION', 'w') as version_file:
        version_file.write('{}\n'.format(RELEASE.decode('utf-8')))
except subprocess.CalledProcessError:
    try:
        RELEASE = open('VERSION').read().strip()
    except Exception:
        try:
            with file('CHANGELOG.rst') as changelog:
                for count, line in enumerate(changelog):
                    if re.search('^`debops v', line):
                        RELEASE = line.split()[1].rstrip(b'`_').lstrip(b'v')
                        break
            with open('VERSION', 'w') as version_file:
                version_file.write('{}\n'.format(RELEASE.decode('utf-8')))
        except Exception:
            RELEASE = '0.0.0'

try:
    # Symlink the 'ansible/' directory inside of the 'debops/' Python package
    # directory. The files will be included in the package using the
    # MANIFEST.in file. This requires 'python-setuptools' APT package from
    # 'jessie-backports' repository.
    if not os.path.exists('debops/ansible'):
        os.symlink('../ansible', 'debops/ansible')
    setup(
        name="debops",
        version=unicode(RELEASE),
        install_requires=['argparse', 'distro', 'future'],
        extras_require={
            'ansible': ['ansible', 'netaddr', 'passlib',
                        'python-ldap', 'dnspython', 'pyopenssl']
            },

        scripts=SCRIPTS,
        packages=find_packages(exclude=['tests']),
        include_package_data=True,

        # metadata for upload to PyPI
        author="DebOps Developers",
        author_email="debops-users@lists.debops.org",
        description="Your Debian-based data center in a box",
        long_description=README,
        license="GPL-3.0-only",
        keywords="ansible debian sysadmin",
        url="https://debops.org/",
        python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, '
                        '!=3.3.*, !=3.4.*, <4',
        download_url="https://github.com/debops/debops"
                    "/archive/v" + unicode(RELEASE) + ".tar.gz",
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
finally:
    # Unlink the symlinked 'ansible/' directory
    if os.path.islink('debops/ansible'):
        os.unlink('debops/ansible')
