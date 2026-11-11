# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the DebOps exception hierarchy.

The base class is the contract the clients build on: the CLI maps it
to exit codes, the MCP daemon later maps it to tool errors. The
existing exceptions keep their names and their catchability.
"""

import pytest

from debops.core import exceptions


def test_the_existing_exceptions_join_the_hierarchy():
    for exc_type in (exceptions.NoDefaultViewException,
                     exceptions.InventorySpecError):
        assert issubclass(exc_type, exceptions.DebOpsError)


def test_the_base_class_catches_the_library_errors():
    with pytest.raises(exceptions.DebOpsError):
        raise exceptions.InventorySpecError('invalid inventory specification')

    with pytest.raises(exceptions.DebOpsError):
        raise exceptions.NoDefaultViewException('no default view')
