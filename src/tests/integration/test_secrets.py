# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""End-to-end tests for encrypted project secrets.

The tests which need ``git-crypt`` or ``encfs`` are skipped when the tools
are not installed. The GnuPG key used for encryption is generated in a
temporary home directory by the ``gpg_env`` fixture.
"""

import shutil

import pytest


pytestmark = pytest.mark.integration


git_crypt = pytest.mark.skipif(
    shutil.which("git-crypt") is None,
    reason="git-crypt is not installed")

encfs = pytest.mark.skipif(
    shutil.which("encfs") is None or shutil.which("fusermount") is None,
    reason="encfs with fusermount is not installed")


@git_crypt
def test_init_can_encrypt_secrets_with_git_crypt(run_debops, tmp_path,
                                                 gpg_env):
    project_dir = tmp_path / "example-gitcrypt"

    result = run_debops("project", "init", "--encrypt", "git-crypt",
                        "--keys", "debops-tests@example.org",
                        "--no-requirements", str(project_dir), env=gpg_env)

    assert result.returncode == 0
    assert (project_dir / ".git" / "git-crypt" / "keys").is_dir()
    assert "secret" in (project_dir / ".gitattributes").read_text()


@git_crypt
def test_project_unlock_and_lock_a_git_crypt_project(run_debops, tmp_path,
                                                     gpg_env):
    project_dir = tmp_path / "example-gitcrypt"
    run_debops("project", "init", "--encrypt", "git-crypt",
               "--keys", "debops-tests@example.org", "--no-requirements",
               str(project_dir), env=gpg_env, check=True)

    result = run_debops("project", "unlock", cwd=str(project_dir), env=gpg_env)
    assert result.returncode == 0

    result = run_debops("project", "lock", cwd=str(project_dir), env=gpg_env)
    assert result.returncode == 0


@encfs
def test_init_can_encrypt_secrets_with_encfs(run_debops, tmp_path, gpg_env):
    project_dir = tmp_path / "example-encfs"

    result = run_debops("project", "init", "--encrypt", "encfs",
                        "--keys", "debops-tests@example.org",
                        "--no-requirements", str(project_dir), env=gpg_env)

    assert result.returncode == 0
    assert (project_dir / "ansible" / ".encfs.secret").is_dir()
