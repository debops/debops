# -*- coding: utf-8 -*-

# Copyright (C) 2022 David Härdeman <david@hardeman.nu>
# Copyright (C) 2022 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from .constants import DEBOPS_USER_HOME_DIR


def unexpanduser(path):
    if path.startswith(DEBOPS_USER_HOME_DIR):
        return path.replace(DEBOPS_USER_HOME_DIR, '~', 1)
    else:
        return path
