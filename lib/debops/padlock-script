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

    if action == 'lock':
        # Unmount the directory if mounted ...
        if padlock_lock(encfs_encrypted):
            print("Locked!")
        else:
            print("Is already locked.")
    elif action == 'unlock':
        # ... or mount it if unmounted
        if padlock_unlock(encfs_encrypted):
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
