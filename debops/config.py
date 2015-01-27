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

import os
import sys
import ConfigParser

__all__ = ['DEBOPS_CONFIG', 'read_config']

__author__ = "Hartmut Goebel <h.goebel@crazy-compilers.com>"
__copyright__ = "Copyright 2015 by Hartmut Goebel <h.goebel@crazy-compilers.com>"
__licence__ = "GNU General Public License version 3 (GPL v3) or later"


DEBOPS_CONFIG = ".debops.cfg"

def get_config_filenames():
    if sys.platform.startswith('win'):
        configdirs = [os.getenv('APPDATA')
                      or os.path.expanduser('~\\Application Data')]
    elif sys.platform == 'darwin':  # Mac OS X
        configdirs = [os.path.expanduser('~/Library/Application Support')]
    else:
        # According to XDG specification
        # http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html

        configdirs = ([os.getenv('XDG_CONFIG_HOME') or '~/.config'] +
                      (os.getenv('XDG_CONFIG_DIRS') or '/etc/xdg').split(':') +
                      ['/etc'])
        configdirs = [os.path.expanduser(d) for d in configdirs]
        configdirs.reverse()
    return [os.path.join(d, 'debops.cfg') for d in configdirs]

_configfiles = get_config_filenames()

def read_config(debops_root):
    configfiles = _configfiles + [os.path.join(debops_root, DEBOPS_CONFIG)]
    cfgparser = ConfigParser.SafeConfigParser()
    try:
        cfgparser.read(configfiles)
    except ConfigParser.Error, e:
        raise SystemExit('Error in %s: %s' % (DEBOPS_CONFIG, str(e)))
    cfg = dict((sect, dict(cfgparser.items(sect)))
               for sect in cfgparser.sections())
    return cfg
