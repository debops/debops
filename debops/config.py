# -*- coding: utf-8 -*-

# Copyright (C) 2015 Hartmut Goebel <h.goebel@crazy-compilers.com>
# Copyright (C) 2015 DebOps <https://debops.org/>
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

import os
import sys
from io import StringIO
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

__all__ = ['DEBOPS_CONFIG', 'read_config']

__author__ = "Hartmut Goebel <h.goebel@crazy-compilers.com>"
__copyright__ = "Copyright 2015 by Hartmut Goebel "
"<h.goebel@crazy-compilers.com>"
__licence__ = "GNU General Public License version 3 (GPL v3) or later"


DEBOPS_CONFIG = ".debops.cfg"

DEFAULTS = u"""
[paths]
data-home: $XDG_DATA_HOME/debops

# Default monorepo directory
monorepo-path: %(data-home)s/debops

# Default installation directory
install-path: %(data-home)s/debops

# Locations where DebOps playbooks might be found
# This MUST be a multi-line string to make ConfigParser work
playbooks-paths: %(monorepo-path)s/ansible/playbooks

[ansible defaults]
ansible_managed = This file is managed remotely, all changes will be lost
"""

if sys.platform.startswith('win'):
    DEFAULTS = DEFAULTS.replace('$XDG_DATA_HOME',
                                os.getenv('APPDATA') or os.path.expanduser(
                                    '~\\Application Data'))
elif sys.platform == 'darwin':  # Mac OS X
    DEFAULTS = DEFAULTS.replace('$XDG_DATA_HOME',
                                os.path.expanduser(
                                    '~/Library/Application Support'))


def _set_xdg_defaults():
    """
    Set default values for XDG variables according to XDG specification
    https://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html
    """
    for name, default in (
            ('XDG_CONFIG_HOME', os.path.expanduser('~/.config')),
            ('XDG_CONFIG_DIRS', '/etc/xdg'),
            ('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))):
        if not os.environ.get(name):
            os.environ[name] = default


def _get_config_filenames():
    if sys.platform.startswith('win'):
        configdirs = [os.getenv('APPDATA')
                      or os.path.expanduser('~\\Application Data')]
    elif sys.platform == 'darwin':  # Mac OS X
        configdirs = [os.path.expanduser('~/Library/Application Support'),
                      '/etc']
        configdirs.reverse()
    else:
        _set_xdg_defaults()
        configdirs = ([os.getenv('XDG_CONFIG_HOME')] +
                      os.getenv('XDG_CONFIG_DIRS').split(':') +
                      ['/etc'])
        configdirs = [os.path.expanduser(d) for d in configdirs]
        configdirs.reverse()
    return [os.path.join(d, 'debops.cfg') for d in configdirs]


_configfiles = _get_config_filenames()


def _expandpath(path):
    return os.path.expanduser(os.path.expandvars(path.strip()))


def read_config(project_root):
    if project_root is None:
        configfiles = _configfiles
    else:
        configfiles = _configfiles + [os.path.join(project_root,
                                                   DEBOPS_CONFIG)]
    cfgparser = configparser.SafeConfigParser()
    cfgparser.readfp(StringIO(DEFAULTS))
    try:
        cfgparser.read(configfiles)
    except configparser.Error as e:
        raise SystemExit('Error in %s: %s' % (DEBOPS_CONFIG, str(e)))
    cfg = dict((sect, dict(cfgparser.items(sect)))
               for sect in cfgparser.sections())
    # expand vars and home-directory
    for name in ('data-home', 'monorepo-path', 'install-path'):
        cfg['paths'][name] = _expandpath(cfg['paths'][name])
    cfg['paths']['playbooks-paths'] = [
        _expandpath(p)
        for p in cfg['paths']['playbooks-paths'].splitlines()
        if p.strip()]
    return cfg
