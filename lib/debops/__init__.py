# -*- coding: utf-8 -*-

# This program is free software; you can redistribute
# it and/or modify it under the terms of the
# GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License,
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

from __future__ import print_function

import os
import subprocess
import stat
try:
    # shlex.quote is new in Python 3.3
    from shlex import quote as shquote
except ImportError:
    # implement subset of shlex.quote
    def shquote(s):
        if not s: return "''"
        return "'" + s.replace("'", "'\"'\"'") + "'"


# ---- Global constants ----

DEBOPS_DATA_HOME = os.path.expanduser(os.path.join(
    os.environ.get('XDG_DATA_HOME', '~/.local/share'), "debops"))

DEBOPS_CONFIG = ".debops.cfg"

# Default installation directory
DEBOPS_DEFAULT_INSTALL_PATH = os.path.join(DEBOPS_DATA_HOME, "debops-playbooks")

ANSIBLE_CONFIG_FILE = "ansible.cfg"

#--- Roles

# Default role prefix if no roles with prefixes are specified
ROLE_PREFIX = "debops"

#--- Playbooks

# Default subdirectory where playbooks are stored, relative to the DebOps
# playbooks directory
DEBOPS_PLAYBOOK_DIR = "playbooks"

# Locations where DebOps playbooks might be found
DEBOPS_PLAYBOOKS_PATHS = [
    os.path.join(DEBOPS_DATA_HOME, "debops-playbooks", "playbooks"),
    "/usr/local/share/debops/debops-playbooks/playbooks",
    "/usr/share/debops/debops-playbooks/playbooks",
]

# Default site.yml playbook to look for
DEBOPS_SITE_PLAYBOOK = os.path.join(DEBOPS_PLAYBOOK_DIR, "site.yml")

#--- Inventories

INVENTORY = "inventory"

# List of possible inventory directories, relative to DebOps root
# project directory
ANSIBLE_INVENTORY_PATHS = [
    os.path.join("ansible", INVENTORY),
    INVENTORY]

#--- Encryption

# Name of the script used to unlock/lock the encrypted directory
PADLOCK_CMD = "padlock"

ENCFS_CONFIGFILE = ".encfs6.xml"
ENCFS_PREFIX = ".encfs."
SECRET_NAME = "secret"
# Name of the keyfile stored inside EncFS encrypted directory
ENCFS_KEYFILE = ".encfs6.keyfile"
# Length of the random EncFS password stored in encrypted keyfile
ENCFS_KEYFILE_LENGTH = 256


# ---- Functions ----

def find_up(path, name):
    """
    Find specified file or directory in parent dir
    """
    # :todo: only wlak up to the mount-point llike git does
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
    Searches the debops project, this workdir belongs to, if any.

    `path` defaults to the current working directory.

    Returns None if this path does not belong to a debops project. 
    """
    if path is None:
        path = os.getcwd()
    # Find DebOps configuration file
    debops_config = find_up(path, DEBOPS_CONFIG)
    # Find root of the DebOps project dir
    return os.path.dirname(debops_config) if debops_config else None


def find_playbookpath(debops_root):
    """
    Search for playbooks in various locations.
    """
    if debops_root:
        places = [os.path.join(debops_root, "debops-playbooks", "playbooks")]
        places.extend(DEBOPS_PLAYBOOKS_PATHS)
    else:
        places = DEBOPS_PLAYBOOKS_PATHS
    for playbook_path in places:
        if os.path.exists(os.path.join(playbook_path, "site.yml")):
            return playbook_path


def find_inventorypath(debops_root):
    """
    Search Ansible inventory in local directories.
    """
    for inventory_path in ANSIBLE_INVENTORY_PATHS:
        ansible_inventory = os.path.join(debops_root, inventory_path)
        if os.path.isdir(ansible_inventory):
            return ansible_inventory


# ---- Encryption support ----

def padlock_lock(encrypted_path):
    # Cut the EncFS directory prefix to get the decrypted directory name
    decrypted_path = ''.join(encrypted_path.rsplit(ENCFS_PREFIX, 1))
    subprocess.call(['fusermount', '-u', decrypted_path])


def padlock_unlock(encrypted_path):
    # Cut the EncFS directory prefix to get the decrypted directory name
    decrypted_path = ''.join(encrypted_path.rsplit(ENCFS_PREFIX, 1))

    # Make sure that mount directory exists
    if not os.path.isdir(decrypted_path):
        os.makedirs(decrypted_path)

    # Location of GPG-encrypted keyfile to use
    keyfile = os.path.join(encrypted_path, ENCFS_KEYFILE)

    configfile = os.path.join(encrypted_path, ENCFS_CONFIGFILE)
    if not os.path.exists(configfile):
        os.mkfifo(configfile)
    elif not stat.S_ISFIFO(os.stat(configfile).st_mode):
        raise IOError(17, configfile+' exists but is not a fifo')

    # Start encfs. It will wait for input on the `configfile` named
    # pipe.
    encfs = subprocess.Popen([
        'encfs', encrypted_path, decrypted_path, 
        '--extpass', 'gpg --no-mdc-warning --output - %s' % shquote(keyfile)])
    # now decrypt the config and write it into the named pipe
    with open(configfile, 'w') as fh:
        # NB: gpg must write to stdout to avoid it is asking whether
        # the file should be overwritten
        subprocess.Popen(['gpg', '--no-mdc-warning', '--output', '-',
                          configfile+'.asc'], stdout=fh).wait()
    encfs.wait()
    os.remove(configfile)
