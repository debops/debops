# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Hartmut Goebel <h.goebel@crazy-compilers.com>
# Copyright (C) 2014-2015 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

# This program is free software; you can redistribute
# it and/or modify it under the terms of the
# GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License,
# or (at your option) any later version.
#
# This program is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General
# Public License along with this program; if not,
# write to the Free Software Foundation, Inc., 59
# Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# An on-line copy of the GNU General Public License can
# be downloaded from the FSF web page at:
# https://www.gnu.org/copyleft/gpl.html

from __future__ import print_function
from unittest import TestCase
from imp import reload
import os
import sys
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
try:
    from cStringIO import cStringIO
except ImportError:
    from io import StringIO as cStringIO
import tempfile
import shutil

import debops

__author__ = "Hartmut Goebel <h.goebel@crazy-compilers.com>"
__copyright__ = "Copyright 2014-2015 by Hartmut Goebel "
"<h.goebel@crazy-compilers.com>"
__licence__ = "GNU General Public License version 3 (GPL v3) or later"


def setenv(name, value):
    os.environ[name] = value


def unsetenv(name):
    os.environ[name] = ''


class TestConfigFilenames(TestCase):

    def test_get_config_filenames_no_env(self):
        unsetenv('XDG_CONFIG_HOME')
        unsetenv('XDG_CONFIG_DIRS')
        cfn = debops.config._get_config_filenames()
        self.assertListEqual(cfn,
                             ['/etc/debops.cfg',
                              '/etc/xdg/debops.cfg',
                              os.path.expanduser('~/.config/debops.cfg')])

    def test_get_config_filenames_with_XDG_CONFIG_HOME_set(self):
        setenv('XDG_CONFIG_HOME', '/myhome/mindy')
        unsetenv('XDG_CONFIG_DIRS')
        cfn = debops.config._get_config_filenames()
        self.assertListEqual(cfn,
                             ['/etc/debops.cfg',
                              '/etc/xdg/debops.cfg',
                              '/myhome/mindy/debops.cfg'])

    def test_get_config_filenames_with_XDG_CONFIG_DIRS_set(self):
        unsetenv('XDG_CONFIG_HOME')
        setenv('XDG_CONFIG_DIRS', '/tmp/mindy:/tmp/etc:/usr/local/etc')
        cfn = debops.config._get_config_filenames()
        self.assertListEqual(cfn,
                             ['/etc/debops.cfg',
                              '/usr/local/etc/debops.cfg',
                              '/tmp/etc/debops.cfg',
                              '/tmp/mindy/debops.cfg',
                              os.path.expanduser('~/.config/debops.cfg')])

    def test_get_config_filenames_with_XDG_vars_set(self):
        setenv('XDG_CONFIG_HOME', '/myhome/mindy')
        setenv('XDG_CONFIG_DIRS', '/tmp/etc:/usr/local/etc')
        cfn = debops.config._get_config_filenames()
        self.assertListEqual(cfn,
                             ['/etc/debops.cfg',
                              '/usr/local/etc/debops.cfg',
                              '/tmp/etc/debops.cfg',
                              '/myhome/mindy/debops.cfg'])


ANSIBLE_DEFAULTS = {'ansible_managed':
                    'This file is managed remotely, all changes will be lost'}


class TestReadConfig(TestCase):

    def setUp(self):
        self.sandbox = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.sandbox)
        self._saved_configfiles = debops.config._configfiles[:]
        # remove '/etc/debobs.cfg' to make results predictable
        debops.config._configfiles.remove('/etc/debops.cfg')

    def tearDown(self):
        debops.config._configfiles = self._saved_configfiles[:]

    def _make_configfile(self, dir, sect, *data):
        dir = os.path.join(self.sandbox, dir)
        os.makedirs(dir)
        fn = os.path.join(dir, 'debops.cfg')
        with open(fn, 'w') as fh:
            print("[{}]".format(sect), file=fh)
            for d in data:
                print(d, file=fh)
        return dir

    def _read_config(self, project_dir):
        # refresh debops._configfiles with set environment
        cfn = debops.config._get_config_filenames()
        cfn.remove('/etc/debops.cfg')
        debops.config._configfiles = cfn
        cfg = debops.config.read_config(project_dir)
        del cfg['paths']
        return cfg

    def test_read_config_files_simple(self):
        dirs = [self._make_configfile(dir, sect, data) for
                dir, sect, data in (
                    ['xdg_home', 'debops', 'home: /var/home'],
                    ['xdg_dir1', 'debops', 'name1: value1'],
                    ['xdg_dir2', 'debops', 'name2: value2'],
                )]
        setenv('XDG_CONFIG_HOME', dirs[0])
        setenv('XDG_CONFIG_DIRS', ':'.join(dirs[1:]))
        cfg = self._read_config('/non/existing/dir')
        self.assertDictEqual(cfg,
                             {'ansible defaults': ANSIBLE_DEFAULTS,
                              'debops': {'home': '/var/home',
                                         'name1': 'value1',
                                         'name2': 'value2'}
                              })

    def test_read_config_files_precedence(self):
        dirs = [self._make_configfile(dir, sect, data) for
                dir, sect, data in (
                    ['xdg_home', 'debops', 'home: /var/home'],
                    # xdg_dir1 has higher priority
                    ['xdg_dir1', 'debops', 'name1: value1'],
                    ['xdg_dir2', 'debops', 'name1: value2'],
                )]
        setenv('XDG_CONFIG_HOME', dirs[0])
        setenv('XDG_CONFIG_DIRS', ':'.join(dirs[1:]))
        cfg = self._read_config('/non/existing/dir')
        self.assertDictEqual(cfg,
                             {'ansible defaults': ANSIBLE_DEFAULTS,
                              'debops': {'home': '/var/home',
                                         'name1': 'value1'}
                              })

    def test_read_config_files_with_project_root(self):
        dirs = [self._make_configfile(dir, sect, data) for
                dir, sect, data in (
                    ['xdg_home', 'debops', 'home: /var/home'],
                    ['xdg_dir1', 'debops', 'name1: value1'],
                    ['proj_root', 'debops', 'name2: value2'],
                )]
        setenv('XDG_CONFIG_HOME', dirs[0])
        setenv('XDG_CONFIG_DIRS', dirs[1])
        os.rename(os.path.join(dirs[2], 'debops.cfg'),
                  os.path.join(dirs[2], '.debops.cfg'))
        cfg = self._read_config(dirs[2])
        self.assertDictEqual(cfg,
                             {'ansible defaults': ANSIBLE_DEFAULTS,
                              'debops': {'home': '/var/home',
                                         'name1': 'value1',
                                         'name2': 'value2'}
                              })

    def test_read_config_files_with_project_root_precedence(self):
        dirs = [self._make_configfile(dir, sect, *data) for
                dir, sect, data in (
                    ['xdg_home', 'debops', ('home: /var/home',)],
                    ['xdg_dir1', 'debops', ('name1: value1',)],
                    ['pro_root', 'debops', ('name1: value2',
                                            'home: /my/home')],
                )]
        setenv('XDG_CONFIG_HOME', dirs[0])
        setenv('XDG_CONFIG_DIRS', dirs[1])
        os.rename(os.path.join(dirs[2], 'debops.cfg'),
                  os.path.join(dirs[2], '.debops.cfg'))
        cfg = self._read_config(dirs[2])
        self.assertDictEqual(cfg,
                             {'ansible defaults': ANSIBLE_DEFAULTS,
                              'debops': {'home': '/my/home',
                                         'name1': 'value2'}
                              })


class TestReadConfig2(TestCase):

    def setUp(self):
        self.sandbox = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.sandbox)
        self._saved_configfiles = debops.config._configfiles[:]
        # remove '/etc/debobs.cfg' to make results predictable
        debops.config._configfiles.remove('/etc/debops.cfg')

    def tearDown(self):
        debops.config._configfiles = self._saved_configfiles[:]

    def _make_configfile(self, dir, sect, *data):
        dir = os.path.join(self.sandbox, dir)
        os.makedirs(dir)
        fn = os.path.join(dir, 'debops.cfg')
        with open(fn, 'w') as fh:
            print("[{}]".format(sect), file=fh)
            for d in data:
                print(d, file=fh)
        return dir

    def _read_config(self, project_dir):
        # refresh debops._configfiles with set environment
        cfn = debops.config._get_config_filenames()
        cfn.remove('/etc/debops.cfg')
        debops.config._configfiles = cfn
        return debops.config.read_config(project_dir)

    def test_defaults(self):
        dirs = [self._make_configfile(dir, sect, data) for
                dir, sect, data in (
                    ['xdg_home', 'xpaths', 'data-home: /opt/my/debops'],
                )]
        unsetenv('XDG_CONFIG_HOME')
        cfg = self._read_config('/non/existing/dir')
        self.assertDictEqual(
            cfg['paths'],
            {'data-home': os.path.expanduser('~/.local/share/debops'),
             'monorepo-path': os.path.expanduser(
                 '~/.local/share/debops/debops'),
             'install-path': os.path.expanduser(
                 '~/.local/share/debops/debops'),
             'playbooks-paths': [os.path.expanduser(
                 '~/.local/share/debops/debops/ansible/playbooks')],
             })

    def test_read_config_files_simple(self):
        dirs = [self._make_configfile(dir, sect, data) for
                dir, sect, data in (
                    ['xdg_home', 'paths', 'data-home: /opt/my/debops'],
                )]
        setenv('XDG_CONFIG_HOME', dirs[0])
        cfg = self._read_config('/non/existing/dir')
        self.assertDictEqual(
            cfg['paths'],
            {'data-home': '/opt/my/debops',
             'monorepo-path': '/opt/my/debops/debops',
             'install-path': '/opt/my/debops/debops',
             'playbooks-paths': ['/opt/my/debops/debops/ansible/playbooks'],
             })


class TestReadConfigDefaultsForPlattforms(TestCase):

    def setUp(self):
        self.platform = sys.platform

    def tearDown(self):
        sys.platform = self.platform

    def test_defaults_linux(self):
        sys.platform = 'linux2'
        reload(debops.config)
        cfgparser = configparser.SafeConfigParser()
        cfgparser.readfp(cStringIO(debops.config.DEFAULTS))
        self.assertEqual(cfgparser.get('paths', 'data-home'),
                         '$XDG_DATA_HOME/debops')

    def test_defaults_windows_without_APPDATA(self):
        sys.platform = 'win32'
        unsetenv('APPDATA')
        reload(debops.config)
        cfgparser = configparser.SafeConfigParser()
        cfgparser.readfp(cStringIO(debops.config.DEFAULTS))
        self.assertEqual(cfgparser.get('paths', 'data-home'),
                         os.path.expanduser(
                             '~\\Application Data/debops'))

    def test_defaults_windows_with_APPDATA(self):
        sys.platform = 'win32'
        setenv('APPDATA', 'H:\\my\\own\\data')
        reload(debops.config)
        cfgparser = configparser.SafeConfigParser()
        cfgparser.readfp(cStringIO(debops.config.DEFAULTS))
        self.assertEqual(cfgparser.get('paths', 'data-home'),
                         'H:\\my\\own\\data/debops')

    def test_defaults_os_x(self):
        sys.platform = 'darwin'
        reload(debops.config)
        cfgparser = configparser.SafeConfigParser()
        cfgparser.readfp(cStringIO(debops.config.DEFAULTS))
        self.assertEqual(cfgparser.get('paths', 'data-home'),
                         os.path.expanduser(
                             '~/Library/Application Support/debops'))
