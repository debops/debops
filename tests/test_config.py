# -*- coding: utf-8 -*-

# Copyright (C) 2014 Hartmut Goebel <h.goebel@crazy-compilers.com>
# Part of the DebOps project - http://debops.org/

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
# http://www.gnu.org/copyleft/gpl.html

from unittest2 import TestCase
import os

import debops

__author__ = "Hartmut Goebel <h.goebel@crazy-compilers.com>"
__copyright__ = "Copyright 2014 by Hartmut Goebel <h.goebel@crazy-compilers.com>"
__licence__ = "GNU General Public License version 3 (GPL v3) or later"

def setenv(name, value):
    os.environ[name] = value

def unsetenv(name):
    os.environ[name] = ''

class TestConfig(TestCase):

    def test_get_config_filenames_no_env(self):
        unsetenv('XDG_CONFIG_HOME')
        unsetenv('XDG_CONFIG_DIRS')
        cfn = debops.config.get_config_filenames()
        self.assertListEqual(cfn,
                             ['/etc/debops.cfg',
                              '/etc/xdg/debops.cfg',
                              os.path.expanduser('~/.config/debops.cfg')])

    def test_get_config_filenames_with_XDG_CONFIG_HOME_set(self):
        setenv('XDG_CONFIG_HOME', '/myhome/mindy')
        unsetenv('XDG_CONFIG_DIRS')
        cfn = debops.config.get_config_filenames()
        self.assertListEqual(cfn,
                             ['/etc/debops.cfg',
                              '/etc/xdg/debops.cfg',
                              '/myhome/mindy/debops.cfg'])

    def test_get_config_filenames_with_XDG_CONFIG_DIRS_set(self):
        unsetenv('XDG_CONFIG_HOME')
        setenv('XDG_CONFIG_DIRS', '/tmp/mindy:/tmp/etc:/usr/local/etc')
        cfn = debops.config.get_config_filenames()
        self.assertListEqual(cfn,
                             ['/etc/debops.cfg',
                              '/usr/local/etc/debops.cfg',
                              '/tmp/etc/debops.cfg',
                              '/tmp/mindy/debops.cfg',
                              os.path.expanduser('~/.config/debops.cfg')])
                              

    def test_get_config_filenames_with_XDG_vars_set(self):
        setenv('XDG_CONFIG_HOME', '/myhome/mindy')
        setenv('XDG_CONFIG_DIRS', '/tmp/etc:/usr/local/etc')
        cfn = debops.config.get_config_filenames()
        self.assertListEqual(cfn,
                             ['/etc/debops.cfg',
                              '/usr/local/etc/debops.cfg',
                              '/tmp/etc/debops.cfg',
                              '/myhome/mindy/debops.cfg'])
