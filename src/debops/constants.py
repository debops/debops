# -*- coding: utf-8 -*-

# Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2020 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import os

# Path to the directory which contains data files included in the Python
# package
DEBOPS_PACKAGE_DATA = os.path.join(os.path.dirname(__file__), '_data')

# Path to the user's home dir
DEBOPS_USER_HOME_DIR = os.path.expanduser('~')
