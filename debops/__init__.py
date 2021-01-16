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

import sys
import os
import subprocess
import stat
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
try:
    # shlex.quote is new in Python 3.3
    from shlex import quote as shquote
except ImportError:
    # implement subset of shlex.quote
    def shquote(s):
        if not s:
            return "''"
        return "'" + s.replace("'", "'\"'\"'") + "'"

from .config import *

__author__ = "Hartmut Goebel <h.goebel@crazy-compilers.com>"
__copyright__ = "Copyright 2014-2015 by Hartmut Goebel "
"<h.goebel@crazy-compilers.com>"
__licence__ = "GNU General Public License version 3 (GPL v3) or later"


# ---- Global constants ----

ANSIBLE_CONFIG_FILE = "ansible.cfg"

# Path to the Ansible playbooks and roles distributed inside of the Python
# package
DEBOPS_PY_PACKAGE = os.path.join(os.path.dirname(__file__), 'ansible')

# --- Roles

# Default role prefix if no roles with prefixes are specified
ROLE_PREFIX = "debops"

# --- Playbooks

# Default site.yml playbook to look for
DEBOPS_SITE_PLAYBOOK = os.path.join("playbooks", "site.yml")

# --- Inventories

INVENTORY = "inventory"

# List of possible inventory directories, relative to DebOps root
# project directory
ANSIBLE_INVENTORY_PATHS = [
    os.path.join("ansible", INVENTORY),
    INVENTORY]

# --- Encryption

# Name of the script used to unlock/lock the encrypted directory
PADLOCK_CMD = "padlock"

ENCFS_CONFIGFILE = ".encfs6.xml"
ENCFS_PREFIX = ".encfs."
SECRET_NAME = "secret"
# Name of the keyfile stored inside EncFS encrypted directory
ENCFS_KEYFILE = ".encfs6.keyfile"
# Length of the random EncFS password stored in encrypted keyfile
ENCFS_KEYFILE_LENGTH = 256

# External programms used. List here for easy substitution for
# hard-coded paths.
ENCFS = 'encfs'
FUSERMOUNT = 'fusermount'
UMOUNT = 'umount'
GPG = 'gpg'


# ---- Functions ----

def _find_up(path, name):
    """
    Find specified file or directory in parent dir
    """
    # :todo: only walk up to the mount-point like git does
    path = os.path.abspath(path)
    last = None
    while path != last:
        last = path
        path = os.path.join(path, name)
        if os.path.exists(path):
            return path
        path = os.path.dirname(last)
    return None


def find_debops_project(path=None):
    """
    Searches DebOps, this workdir belongs to, if any.

    `path` defaults to the current working directory.

    Returns None if this path does not belong to a DebOps project.
    """
    if path is None:
        path = os.getcwd()
    # Find DebOps configuration file
    debops_config = _find_up(path, DEBOPS_CONFIG)
    # Find root of the DebOps project dir
    return os.path.dirname(debops_config) if debops_config else None


def find_monorepopath(config, project_root):
    """
    Search for monorepo in various locations.
    """
    if project_root:
        places = [os.path.join(project_root, "monorepo")]
    else:
        places = []
    places.append(config['paths']['monorepo-path'])
    for monorepo_path in places:
        if os.path.exists(os.path.join(monorepo_path, "setup.py")):
            return monorepo_path


def find_playbookpath(config, project_root):
    """
    Search for playbooks in various locations.
    """
    if project_root:
        places = [os.path.join(project_root, "ansible", "playbooks")]
    else:
        places = []
    places.extend(config['paths']['playbooks-paths'])
    for playbook_path in places:
        if os.path.exists(os.path.join(playbook_path, "site.yml")):
            return playbook_path


def find_inventorypath(config, project_root):
    """
    Search Ansible inventory in local directories.
    """
    user_defined_inventorypath = config.get('ansible defaults', {}) \
                                       .get('inventory')
    if user_defined_inventorypath:
        if os.path.isabs(user_defined_inventorypath):
            return user_defined_inventorypath
        else:
            return os.path.join(project_root, user_defined_inventorypath)
    for inventory_path in ANSIBLE_INVENTORY_PATHS:
        ansible_inventory = os.path.join(project_root, inventory_path)
        if os.path.isdir(ansible_inventory):
            return ansible_inventory


# ---- Encryption support ----

def padlock_lock(encrypted_path):
    """
    Lock the padlock (this is: unmount the directory).

    Returns True if the padlock originally was unlocked, otherwise False.
    """
    # Cut the EncFS directory prefix to get the decrypted directory name
    decrypted_path = ''.join(encrypted_path.rsplit(ENCFS_PREFIX, 1))
    if not os.path.ismount(decrypted_path):
        return False
    # OS X compatibility
    if sys.platform == 'darwin':
        subprocess.call([UMOUNT, decrypted_path])
    else:
        subprocess.call([FUSERMOUNT, '-u', decrypted_path])
    return True


def padlock_unlock(encrypted_path):
    """
    Unlock the padlock (this is: mount the directory).

    Returns True if the padlock originally was locked, otherwise False.
    """
    # Location of GPG-encrypted keyfile to use
    keyfile = os.path.join(encrypted_path, ENCFS_KEYFILE)
    configfile = os.path.join(encrypted_path, ENCFS_CONFIGFILE)
    crypted_configfile = configfile+'.asc'

    # Location of an alternative executable that will mount the decrypted dir
    unlock_cmd = os.path.join(encrypted_path, PADLOCK_CMD)

    # Cut the EncFS directory prefix to get the decrypted directory name
    decrypted_path = ''.join(encrypted_path.rsplit(ENCFS_PREFIX, 1))

    if os.path.exists(keyfile) and os.path.exists(crypted_configfile):
        print("Mounting '{}' using encfs..".format(encrypted_path))
        unlock_cmd = None
    elif os.access(unlock_cmd, os.X_OK):
        print(
            "Mounting '{}' using '{}'..".format(encrypted_path, unlock_cmd))
    else:
        return False

    # Check if encrypted directory is already mounted
    # NB: This only tests if encfs_decrypted as a mount-point at all,
    # no matter if it is fuse.encfs or not.
    if os.path.ismount(decrypted_path):
        # if it is already mounted, do nothing
        return False

    # Make sure the mount directory exists
    if not os.path.isdir(decrypted_path):
        os.makedirs(decrypted_path)

    if unlock_cmd is not None:
        subprocess.check_output([unlock_cmd, encrypted_path, decrypted_path],
                                stderr=subprocess.STDOUT)
        return True

    # Make sure the named pipe for the configfile exists
    if not os.path.exists(configfile):
        os.mkfifo(configfile)
    elif not stat.S_ISFIFO(os.stat(configfile).st_mode):
        raise IOError(17, configfile+' exists but is not a fifo')

    # Start encfs. It will wait for input on the `configfile` named
    # pipe.
    encfs = subprocess.Popen([
        ENCFS, encrypted_path, decrypted_path,
        '--extpass',
        GPG + ' --decrypt --no-mdc-warning --output - %s' % shquote(keyfile)])
    # now decrypt the config and write it into the named pipe
    with open(configfile, 'w') as fh:
        # NB: gpg must write to stdout to avoid it is asking whether
        # the file should be overwritten
        subprocess.Popen([GPG,
                          '--decrypt', '--no-mdc-warning', '--output', '-',
                          crypted_configfile], stdout=fh).wait()
    encfs.wait()
    os.remove(configfile)
    return True
