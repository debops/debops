# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The command line entry point, driven as a subprocess.

These tests exercise the real ``python -m debops`` path, so the exit codes
and the argument handling are the ones a user sees.
"""

import pytest


pytestmark = pytest.mark.integration


def test_version_is_reported(run_debops):
    result = run_debops("--version")

    assert result.returncode == 0
    assert result.stdout.strip()
