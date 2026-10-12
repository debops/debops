# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Fixtures for the integration tests.

The tests drive the real ``debops`` command line in temporary directories.
``XDG_CONFIG_HOME`` is pointed at an empty directory so that the
configuration and the hook scripts of the machine running the tests cannot
leak in; ``HOME`` is left alone so that the Python user site packages stay
importable.
"""

import os
import shutil
import subprocess

import pytest


@pytest.fixture
def debops_env(tmp_path):
    """Environment overrides which keep the debops subprocess hermetic.

    The git identity used for the commits made by the project initialization
    is provided through the environment, which keeps the tests independent
    of the git configuration of the machine running them; the global and the
    system git configuration are disabled entirely, so that settings such as
    commit signing cannot break the commits made by git-crypt.
    """
    config_home = tmp_path / "config"
    config_home.mkdir()
    return {
        "XDG_CONFIG_HOME": str(config_home),
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_AUTHOR_NAME": "DebOps Tests",
        "GIT_AUTHOR_EMAIL": "debops-tests@example.org",
        "GIT_COMMITTER_NAME": "DebOps Tests",
        "GIT_COMMITTER_EMAIL": "debops-tests@example.org",
    }


@pytest.fixture
def gpg_env(debops_env, tmp_path):
    """A hermetic GnuPG home directory with a single test key.

    Secret encryption needs a key to encrypt to; generating one for each test
    keeps the machine keyring untouched.
    """
    if shutil.which("gpg") is None:
        pytest.skip("gpg is not installed")

    gnupg = tmp_path / "gnupg"
    gnupg.mkdir(mode=0o700)
    env = dict(debops_env, GNUPGHOME=str(gnupg))
    subprocess.run(
        ["gpg", "--batch", "--pinentry-mode", "loopback", "--passphrase", "",
         "--quick-gen-key", "DebOps Tests <debops-tests@example.org>",
         "default", "default", "never"],
        env={**os.environ, **env}, check=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return env
