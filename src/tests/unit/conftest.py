# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Fixtures shared by the unit tests."""

import pytest

from debops.config import Configuration


@pytest.fixture
def configuration():
    """A Configuration with none of its filesystem or environment access.

    The real constructor reads ``/etc``, the user's XDG directories and the
    packaged defaults. The unit tests only need the in-memory state that the
    methods under test operate on, so the object is built without running
    ``__init__``.
    """
    config = Configuration.__new__(Configuration)
    config._config = {}
    config._config_files = []
    config._env_files = []
    config._env_vars = {}
    return config
