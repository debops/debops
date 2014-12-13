#!/usr/bin/env python
# -*- coding: utf-8 -*-

# padlock: lock/unlock EncFS-encrypted directory with GPG key/passphrase
# Copyright (C) 2014 Hartmut Goebel <h.goebel@crazy-compilers.com>
# Part of the DebOps project - http://debops.org/

import os
import argparse

from debops import *
from debops.cmds import *

def main(action):
    require_commands('encfs', 'fusermount', 'gpg')

    # Get the absolute path to script's directory
    encfs_encrypted = os.path.dirname(os.path.realpath(__file__))
    encfs_decrypted = os.path.join(os.path.dirname(encfs_encrypted),
                                       SECRET_NAME)

    # Check if encrypted directory is already mounted
    # NB: This only tests if encfs_decrypted as a mount-point at all,
    # no matter if it is fuse.encfs or not.
    is_mounted = os.path.ismount(encfs_decrypted)

    if action == 'lock':
        if is_mounted:
            # Unmount the directory if mounted ...
            padlock_lock(encfs_encrypted)
            print("Locked!")
        else:
            print("Is already locked.")
    elif action == 'unlock':
        if not is_mounted:
            # ... or mount it if unmounted
            padlock_unlock(encfs_encrypted)
            print("Unlocked!")
        else:
            print("Is already unlocked.")

parser = argparse.ArgumentParser()
parser.add_argument('action', choices=['lock', 'unlock'])
args = parser.parse_args()

try:
    main(args.action)
except KeyboardInterrupt:
    raise SystemExit('... aborted')
