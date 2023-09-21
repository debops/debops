# Copyright (C) 2023 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2023 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

class NoDefaultViewException(Exception):
    """Raised when default view is not defined in DebOps configuration"""
    pass
