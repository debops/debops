# Copyright (C) 2023-2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2023-2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later


class DebOpsError(Exception):
    """Base class of the errors the DebOps library raises.

    The library reports its own failures through this hierarchy and
    lets the clients translate it into their native error reporting:
    CLI exit codes today, MCP tool errors later. Operating system
    errors -- a missing file, a refused permission -- propagate as
    themselves; only the conditions DebOps defines its own words for
    join this hierarchy."""


class NoDefaultViewException(DebOpsError):
    """Raised when default view is not defined in DebOps configuration"""
    pass


class ViewNotFoundError(DebOpsError):
    """Raised when an explicitly selected view is not defined in the
    DebOps project"""
    pass


class OptionNotFoundError(DebOpsError):
    """Raised when a requested configuration option is not defined"""
    pass


class InventorySpecError(DebOpsError):
    """Raised when an inventory file specification is invalid"""
    pass
