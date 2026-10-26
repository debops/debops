# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Shared fixtures for the DebOps test suite.

The suite is split in two:

* ``src/tests/unit`` isolates a single component and replaces the tools it
  would otherwise call. These tests run everywhere.
* ``src/tests/integration`` drives several real components with the real
  tools installed on the machine, skipping when one is missing.
"""

import os
import subprocess
import sys
import tempfile

import pytest


# ``conftest.py`` lives in ``<repo>/src/tests``, so the repository root is
# three directories up. The importable package is ``src/debops``.
REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCE_DIR = os.path.join(REPO_ROOT, "src")

# The per-child coverage configuration, created once per pytest session.
SUBPROCESS_COV_CONFIG = None


def pytest_configure(config):
    """Propagate coverage into the DebOps command line subprocesses.

    pytest-cov 7 stopped exporting the environment which prior versions used
    to activate coverage in child processes. Set the coverage trigger by hand
    whenever the parent pytest process measures coverage, so that the DebOps
    integration tests keep covering the command line itself.
    """
    global SUBPROCESS_COV_CONFIG

    if not config.pluginmanager.hasplugin("_cov"):
        return
    if not config.getoption("cov_source"):
        return

    # Default to the same data file the pytest-cov controller uses, so the
    # pytest calls at the end of the session can combine the subprocess data
    # without extra configuration.
    coverage_file = os.environ.setdefault(
        "COVERAGE_FILE", os.path.join(REPO_ROOT, ".coverage"))

    config_file = tempfile.NamedTemporaryFile(
        mode="w", suffix=".cfg", prefix="debops-cov-", delete=False)
    with config_file as fh:
        fh.write(
            "# A per-child coverage configuration for the DebOps integration\n"
            "# tests, written by 'src/tests/conftest.py' on session start.\n\n"
            "[run]\n"
            "branch = True\n"
            "parallel = True\n"
            "source = debops\n"
            f"data_file = {coverage_file}\n")
    SUBPROCESS_COV_CONFIG = config_file.name

    # The coverage hook in site-packages reads only this variable; the
    # 'COVERAGE_PROCESS_CONFIG' spelling carries pre-serialized coverage
    # config, not a file path.
    os.environ.setdefault("COVERAGE_PROCESS_START", SUBPROCESS_COV_CONFIG)


def pytest_sessionfinish(session, exitstatus):
    global SUBPROCESS_COV_CONFIG
    if SUBPROCESS_COV_CONFIG is None:
        return
    os.environ.pop("COVERAGE_PROCESS_START", None)
    os.unlink(SUBPROCESS_COV_CONFIG)
    SUBPROCESS_COV_CONFIG = None


@pytest.fixture
def debops_source_dir():
    """Path to the ``src`` directory which holds the importable package."""
    return SOURCE_DIR


@pytest.fixture
def run_debops(debops_source_dir):
    """Run the DebOps command line in a subprocess.

    The command is launched as ``python -m debops`` with ``src`` on
    ``PYTHONPATH``, which is how the package behaves before installation and
    keeps the real ``sys.exit`` codes observable.
    """
    def _run(*args, cwd=None, env=None, check=False):
        run_env = os.environ.copy()
        run_env["PYTHONPATH"] = os.pathsep.join(
            [debops_source_dir, run_env.get("PYTHONPATH", "")]).rstrip(os.pathsep)
        if env:
            run_env.update(env)

        return subprocess.run(
            [sys.executable, "-m", "debops", *args],
            cwd=cwd, env=run_env, check=check,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return _run
