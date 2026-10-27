# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""End-to-end tests for encrypted project secrets.

The tests which need ``git-crypt`` or ``encfs`` are skipped when the tools
are not installed. The GnuPG key used for encryption is generated in a
temporary home directory by the ``gpg_env`` fixture.

The EncFS tests additionally require the kernel FUSE device: EncFS is a
FUSE filesystem, and without ``/dev/fuse`` no mount can happen. This is an
easy trap — EncFS creates the on-disk volume configuration even when the
mount fails at the end, so a missing FUSE device makes an environment look
like it works while every writable mount silently degrades. Checking the
device node keeps such environments skipped-out instead of false-passing.
"""

import os
import shutil

import pytest


pytestmark = pytest.mark.integration


git_crypt = pytest.mark.skipif(
    shutil.which("git-crypt") is None,
    reason="git-crypt is not installed")


encfs = pytest.mark.skipif(
    shutil.which("encfs") is None or shutil.which("fusermount") is None
    or not os.path.exists("/dev/fuse"),
    reason="encfs with fusermount and the /dev/fuse device are required")


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
    # '.encfs.secret' is the encrypted (cipher) volume, 'secret' is its
    # mount point while unlocked; the volume config is stored encrypted
    # alongside the keyfile.
    assert (project_dir / "ansible" / ".encfs.secret").is_dir()
    assert (project_dir / "ansible" / "secret").is_dir()
    assert (project_dir / "ansible" / ".encfs.secret" /
            ".encfs6.keyfile").is_file()
    assert (project_dir / "ansible" / ".encfs.secret" /
            ".encfs6.xml.asc").is_file()


@encfs
def test_project_unlock_and_lock_an_encfs_project(run_debops, tmp_path,
                                                  gpg_env):
    """The EncFS unlock mounts the secrets volume, the lock unmounts it,
    and the passphrase file survives the round trip encrypted.

    '.encfs.secret' is the encrypted volume, 'secret' is where it is
    mounted while unlocked.
    """
    project_dir = tmp_path / "example-encfs"
    secrets = project_dir / "ansible" / "secret"
    plaintext_file = secrets / "passphrase.txt"
    encfs_dir = project_dir / "ansible" / ".encfs.secret"

    run_debops("project", "init", "--encrypt", "encfs",
               "--keys", "debops-tests@example.org", "--no-requirements",
               str(project_dir), env=gpg_env, check=True)

    result = run_debops("project", "unlock", cwd=str(project_dir), env=gpg_env)
    assert result.returncode == 0
    assert os.path.ismount(str(secrets)), \
        "the secrets directory was not mounted after 'project unlock'"

    plaintext_file.write_text("hunter2\n")
    os.chmod(str(plaintext_file), 0o600)

    result = run_debops("project", "lock", cwd=str(project_dir), env=gpg_env)
    assert result.returncode == 0
    assert not os.path.ismount(str(secrets)), \
        "the secrets directory was still mounted after 'project lock'"

    # The written file is encrypted in place: no plaintext name may leak
    # into the encrypted area while the volume is locked.
    assert "passphrase.txt" not in os.listdir(str(encfs_dir))

    result = run_debops("project", "unlock", cwd=str(project_dir), env=gpg_env)
    assert result.returncode == 0
    assert plaintext_file.read_text() == "hunter2\n"

    result = run_debops("project", "lock", cwd=str(project_dir), env=gpg_env)
    assert result.returncode == 0
    assert not os.path.ismount(str(secrets)), \
        "the secrets directory was still mounted at the end of the test"


@encfs
def test_init_can_encrypt_secrets_with_encfs_in_modern_layout(run_debops,
                                                              tmp_path,
                                                              gpg_env):
    project_dir = tmp_path / "example-encfs-modern"

    result = run_debops("project", "init", "-t", "modern",
                        "--encrypt", "encfs",
                        "--keys", "debops-tests@example.org",
                        "--no-requirements", str(project_dir), env=gpg_env)

    assert result.returncode == 0
    # In a modern project each view keeps its own EncFS volume:
    # '.encfs.secret' inside the view is the encrypted volume, 'secret'
    # is its mount point while unlocked.
    assert (project_dir / "ansible" / "views" / "system" /
            ".encfs.secret").is_dir()
    assert (project_dir / "ansible" / "views" / "system" /
            "secret").is_dir()
    assert (project_dir / "ansible" / "views" / "system" /
            ".encfs.secret" / ".encfs6.keyfile").is_file()
    assert (project_dir / "ansible" / "views" / "system" /
            ".encfs.secret" / ".encfs6.xml.asc").is_file()


@encfs
def test_project_encfs_views_have_separate_volumes(run_debops, tmp_path,
                                                   gpg_env):
    """Each view in a modern project has its own EncFS volume.

    Unlocking one view does not mount the secrets of another, and files
    written into one view's secrets stay invisible in the other.
    """
    project_dir = tmp_path / "example-encfs-modern"
    system_secret = (project_dir / "ansible" / "views" / "system" /
                     "secret")
    other_secret = (project_dir / "ansible" / "views" / "other" /
                    "secret")
    system_encfs = (project_dir / "ansible" / "views" / "system" /
                    ".encfs.secret")
    marker_file = system_secret / "marker.txt"

    run_debops("project", "init", "-t", "modern",
               "--encrypt", "encfs",
               "--keys", "debops-tests@example.org", "--no-requirements",
               str(project_dir), env=gpg_env, check=True)

    result = run_debops("project", "mkview", "--encrypt", "encfs",
                        "--keys", "debops-tests@example.org", "other",
                        cwd=str(project_dir), env=gpg_env)
    assert result.returncode == 0
    assert (project_dir / "ansible" / "views" / "other" /
            ".encfs.secret" / ".encfs6.keyfile").is_file()
    assert (project_dir / "ansible" / "views" / "other" /
            ".encfs.secret" / ".encfs6.xml.asc").is_file()

    result = run_debops("project", "unlock", "-V", "system",
                        cwd=str(project_dir), env=gpg_env)
    assert result.returncode == 0
    assert os.path.ismount(str(system_secret)), \
        "the 'system' view secrets were not mounted after 'project unlock'"
    assert not os.path.ismount(str(other_secret)), \
        "the 'other' view secrets were mounted by 'project unlock -V system'"

    marker_file.write_text("system view\n")
    os.chmod(str(marker_file), 0o600)

    result = run_debops("project", "lock", "-V", "system",
                        cwd=str(project_dir), env=gpg_env)
    assert result.returncode == 0
    assert not os.path.ismount(str(system_secret)), \
        "the 'system' view secrets were still mounted after 'project lock'"

    # The written file is encrypted in place: no plaintext name may leak
    # into the encrypted area while the volume is locked.
    assert "marker.txt" not in os.listdir(str(system_encfs))

    result = run_debops("project", "unlock", "-V", "other",
                        cwd=str(project_dir), env=gpg_env)
    assert result.returncode == 0
    assert os.path.ismount(str(other_secret)), \
        "the 'other' view secrets were not mounted after 'project unlock'"
    assert not (other_secret / "marker.txt").exists(), \
        "the file written in the 'system' view leaked into 'other'"

    result = run_debops("project", "lock", "-V", "other",
                        cwd=str(project_dir), env=gpg_env)
    assert result.returncode == 0
    assert not os.path.ismount(str(other_secret)), \
        "the 'other' view secrets were still mounted at the end of the test"
