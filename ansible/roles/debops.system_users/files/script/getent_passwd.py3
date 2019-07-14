#!/usr/bin/env python3

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
from json import dumps


def getent(user):
    all = pwd.getpwall()
    user = sorted(
        (u for u in all if u.pw_name == user),
        key=operator.attrgetter("pw_name"),
    )[0]
    return ({user.pw_name: ["x", user.pw_uid, user.pw_gid, user.pw_gecos,
                            user.pw_dir, user.pw_shell]})


if __name__ == "__main__":
    try:
        user = sys.argv[1]
        try:
            print(dumps(getent(user), sort_keys=True, indent=4))
        except IndexError:
            sys.exit(2)

    except Exception:
        print("Usage: %s <user>" % os.path.basename(sys.argv[0]))
        sys.exit(1)
