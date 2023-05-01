#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2019 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-only

# Get the specified user information from the system password database.
# This solution should work on all platforms; Ansible 'getent' module does not
# work correctly on Apple macOS.
# Ref: https://github.com/ansible/ansible/issues/38339
#
# Usage: getent_passwd.py <username>

import sys
import os
import pwd
import operator
import subprocess
from json import dumps


def getent(user):
    all = pwd.getpwall()
    user = sorted(
        (u for u in all if u.pw_name == user),
        key=operator.attrgetter("pw_name"),
    )[0]
    return ({user.pw_name: ["x", user.pw_uid, user.pw_gid, user.pw_gecos,
                            user.pw_dir, user.pw_shell]})


def getent_bin(user):
    binoutput = subprocess.check_output(['getent', 'passwd', user])
    output = binoutput.decode("utf-8")
    parts = output.strip().split(":")

    if len(parts) != 7 or parts[0] != user:
        raise RuntimeError("Unexpected output from getent")

    return ({parts[0]: ["x", parts[2], parts[3], parts[4], parts[5], parts[6]]})


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: %s <user>" % os.path.basename(sys.argv[0]))
        sys.exit(1)

    user = sys.argv[1]
    try:
        print(dumps(getent(user), sort_keys=True, indent=4))
        sys.exit(0)
    except IndexError:
        pass

    # As an alternative, try the "getent" binary which can get
    # entries from databases supported by the NSS libraries
    # (e.g. LDAP users)
    try:
        print(dumps(getent_bin(user), sort_keys=True, indent=4))
        sys.exit(0)
    except Exception as e:
        print("Except: " + repr(e))
        sys.exit(2)
