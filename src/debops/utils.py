# -*- coding: utf-8 -*-

# Copyright (C) 2022 David Härdeman <david@hardeman.nu>
# Copyright (C) 2022 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .constants import DEBOPS_USER_HOME_DIR


def unexpanduser(path):
    """Replace the absolute path of the home directory with '~'

    This function will replace the full path of the home directory with the '~'
    shorthand, but only if it is present at the start of the absolute path.
    This workaround is needed in cases where home directory string can be
    encountered inside of the path, for example if home directory is symlinked
    from a different place in the filesystem."""
    if path.startswith(DEBOPS_USER_HOME_DIR):
        return path.replace(DEBOPS_USER_HOME_DIR, '~', 1)
    else:
        return path
