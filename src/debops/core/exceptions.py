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


class OptionRefused(DebOpsError):
    """Raised when a configuration option operation is refused.

    The refusal is reported through the log before the exception is
    raised; the callers exit without reporting it again.
    """


class InventorySpecError(DebOpsError):
    """Raised when an inventory file specification is invalid"""
    pass


class ChecklistError(DebOpsError):
    """Base class of the errors the checklist machinery raises.

    Invalid names resolve here; the specific lifecycle failures get
    their own subclasses."""
    pass


class ChecklistNotFoundError(ChecklistError):
    """Raised when a checklist name does not resolve in any layer"""
    pass


class ChecklistAlreadyOpenError(ChecklistError):
    """Raised when a copy id is already occupied by an open copy"""
    pass


class ChecklistNotOpenError(ChecklistError):
    """Raised when an edit/commit/close target is not an open copy"""
    pass


class ChecklistAmbiguousError(ChecklistError):
    """Raised when a checklist path matches several open copies"""
    pass


class ChecklistFilteredError(ChecklistError):
    """Raised when a checklist name is hidden by checklist.filters"""
    pass
