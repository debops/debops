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
import subprocess

import pytest


pytestmark = pytest.mark.integration


git_crypt = pytest.mark.skipif(
    shutil.which("git-crypt") is None,
    reason="git-crypt is not installed")


encfs = pytest.mark.skipif(
    shutil.which("encfs") is None or shutil.which("fusermount") is None
    or not os.path.exists("/dev/fuse"),
    reason="encfs with fusermount and the /dev/fuse device are required")


def test_project_unlock_and_lock_a_plain_inventory(run_debops, tmp_path,
                                                   debops_env):
    """A project without encrypted secrets has nothing to unlock or
    lock; both commands report success without changing anything."""
    project_dir = tmp_path / "example-plain"
    run_debops("project", "init", "--no-requirements", str(project_dir),
               env=debops_env, check=True)

    unlock = run_debops("project", "unlock", cwd=str(project_dir),
                        env=debops_env)
    lock = run_debops("project", "lock", cwd=str(project_dir),
                      env=debops_env)

    assert unlock.returncode == 0
    assert lock.returncode == 0
    assert not (project_dir / "ansible" / ".encfs.secret").exists()


def _gpg_fingerprint(env, uid):
    """Return the fingerprint of the first key matching the user id."""
    listing = subprocess.run(
        ["gpg", "--list-keys", "--with-colons", uid],
        env={**os.environ, **env}, check=True, capture_output=True,
        text=True).stdout
    for line in listing.splitlines():
        if line.startswith("fpr:"):
            return line.split(":")[9]
    raise AssertionError("no key found for " + uid)


@git_crypt
def test_init_rejects_a_key_without_encryption_capability(
        run_debops, tmp_path, gpg_env):
    """A GPG key which cannot encrypt -- for example a sign-only Ed25519
    key -- aborts the initialization before the project directory is
    created, instead of leaving a project which reports success and
    cannot be unlocked."""
    subprocess.run(
        ["gpg", "--batch", "--pinentry-mode", "loopback", "--passphrase", "",
         "--quick-gen-key", "DebOps Tests <signonly@example.org>",
         "ed25519", "sign", "never"],
        env={**os.environ, **gpg_env}, check=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    fingerprint = _gpg_fingerprint(gpg_env, "signonly@example.org")
    project_dir = tmp_path / "example-unusable"

    result = run_debops("project", "init", "--encrypt", "git-crypt",
                        "--keys", fingerprint, "--no-requirements",
                        str(project_dir), env=gpg_env)

    assert result.returncode == 1
    assert "cannot be used for encryption" in result.stderr
    assert not project_dir.exists()


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


def _git_crypt_is_locked(project_dir):
    """Report whether git-crypt has locked the repository.

    The check mirrors ``SecretStore._git_crypt_locked()``: git-crypt
    implements the lock state by setting and removing the
    ``filter.git-crypt.smudge`` git configuration, so a missing entry
    means locked.
    """
    result = subprocess.run(
        ["git", "config", "--local", "--get", "filter.git-crypt.smudge"],
        cwd=str(project_dir), capture_output=True, text=True)
    return result.returncode != 0


def _head_commit(project_dir):
    """The current commit of the project repository."""
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(project_dir), check=True,
        capture_output=True, text=True).stdout.strip()


def _commit_all(project_dir, env, message):
    """Commit the current state of the project directory."""
    run_env = {**os.environ, **env}
    subprocess.run(["git", "add", "-A"], cwd=str(project_dir), env=run_env,
                   check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "commit", "-q", "-m", message],
                   cwd=str(project_dir), env=run_env, check=True,
                   stdout=subprocess.DEVNULL)


def make_git_crypt_project(run_debops, tmp_path, gpg_env, name):
    """An initialized modern project with git-crypt encrypted secrets.

    The project carries one plaintext marker in the secrets of its
    default view and a playbook which touches nothing, both committed;
    the secrets end up locked, the way initialization leaves them.

    The secret is written while the repository is unlocked and then
    committed, so that git-crypt encrypts it on the way into the
    commit. A secret committed while the repository is locked is stored
    as plaintext -- the clean filter passes content through when it
    cannot encrypt -- and the next checkout smudges it into an empty
    file with a 'file not encrypted' warning, so the locked-commit
    order would poison the fixture instead of testing it.
    """
    project_dir = tmp_path / name
    run_debops("project", "init", "-t", "modern", "--encrypt", "git-crypt",
               "--keys", "debops-tests@example.org", "--no-requirements",
               str(project_dir), env=gpg_env, check=True)
    run_debops("project", "unlock", cwd=str(project_dir),
               env=gpg_env, check=True)

    secret = (project_dir / "ansible" / "views" / "system" /
              "secret" / "credentials.txt")
    secret.write_text("hunter2\n")
    playbook = (project_dir / "ansible" / "views" / "system" /
                "playbooks" / "site.yml")
    playbook.write_text(
        "- hosts: localhost\n"
        "  connection: local\n"
        "  gather_facts: false\n"
        "  tasks:\n"
        "    - ansible.builtin.debug:\n"
        "        msg: test-ok\n")
    _commit_all(project_dir, gpg_env, "Add secrets and a playbook")
    run_debops("project", "lock", cwd=str(project_dir),
               env=gpg_env, check=True)

    return project_dir


def dirty_a_tracked_file(project_dir):
    """Make the working tree dirty through a tracked, harmless file."""
    tracked = (project_dir / "ansible" / "views" / "system" /
               "playbooks" / "site.yml")
    with open(str(tracked), "a") as handle:
        handle.write("# uncommitted change\n")


@git_crypt
def test_run_unlocks_and_relocks_git_crypt_secrets(run_debops, tmp_path,
                                                   gpg_env):
    """'debops run' on a project with locked secrets unlocks them for
    the playbook and locks them again afterwards."""
    project_dir = make_git_crypt_project(run_debops, tmp_path, gpg_env,
                                         "example-gitcrypt-cycle")
    assert _git_crypt_is_locked(project_dir)

    result = run_debops("run", "site.yml", cwd=str(project_dir),
                        env=gpg_env)

    assert result.returncode == 0
    assert _git_crypt_is_locked(project_dir)


@git_crypt
@pytest.mark.parametrize("command", [
    ["run", "site.yml"],
    ["env", "/bin/true"],
    ["exec", "localhost", "-m", "ansible.builtin.command",
     "-a", "/bin/true"],
], ids=["run", "env", "exec"])
def test_runner_commands_leave_already_unlocked_secrets_unlocked(
        run_debops, tmp_path, gpg_env, command):
    """Secrets which were unlocked before the command stay unlocked.

    The runners lock only the secrets they unlocked themselves. Every
    command used to relock them unconditionally after the secrets were
    split out of the inventory, because a one-result unlock list is
    truthy even when no store changed state (PR #2819).
    """
    project_dir = make_git_crypt_project(run_debops, tmp_path, gpg_env,
                                         "example-gitcrypt-unlocked")
    run_debops("project", "unlock", cwd=str(project_dir),
               env=gpg_env, check=True)

    result = run_debops(*command, cwd=str(project_dir), env=gpg_env)

    assert result.returncode == 0
    assert not _git_crypt_is_locked(project_dir), \
        "the command locked secrets it did not unlock"


@git_crypt
def test_runner_commands_do_not_relock_secrets_on_a_dirty_tree(
        run_debops, tmp_path, gpg_env):
    """A dirty working tree must not turn into a command failure.

    Locking git-crypt secrets refuses a dirty working tree. A command
    which leaves secrets alone because it did not unlock them cannot
    fail with 'Cannot lock project secrets' after the command itself
    already finished; the auto-commit is disabled so that a lock
    attempt could not clean the tree first.
    """
    project_dir = make_git_crypt_project(run_debops, tmp_path, gpg_env,
                                         "example-gitcrypt-dirty")
    config = project_dir / ".debops" / "conf.d" / "project.yml"
    config.write_text(config.read_text().replace(
        "auto_commit: True", "auto_commit: False"))
    _commit_all(project_dir, gpg_env, "Disable the auto commit")
    run_debops("project", "unlock", cwd=str(project_dir),
               env=gpg_env, check=True)

    dirty_a_tracked_file(project_dir)
    result = run_debops("env", "/bin/true", cwd=str(project_dir),
                        env=gpg_env)

    assert result.returncode == 0
    assert not _git_crypt_is_locked(project_dir)


@git_crypt
def test_runner_commands_do_not_autocommit_a_dirty_tree(
        run_debops, tmp_path, gpg_env):
    """The default auto-commit must not ride along with a re-lock.

    With the generated 'auto_commit: True' configuration, an
    unconditional re-lock would commit the operator's uncommitted work
    before locking the secrets. A command which unlocked nothing
    commits nothing.
    """
    project_dir = make_git_crypt_project(run_debops, tmp_path, gpg_env,
                                         "example-gitcrypt-autocommit")
    run_debops("project", "unlock", cwd=str(project_dir),
               env=gpg_env, check=True)
    head_before = _head_commit(project_dir)

    dirty_a_tracked_file(project_dir)
    result = run_debops("env", "/bin/true", cwd=str(project_dir),
                        env=gpg_env)

    assert result.returncode == 0
    assert not _git_crypt_is_locked(project_dir)
    assert _head_commit(project_dir) == head_before, \
        "the command committed the operator's uncommitted work"


@git_crypt
def test_runner_commands_leave_an_unlocked_multi_view_project_unlocked(
        run_debops, tmp_path, gpg_env):
    """A command run from a non-default view leaves the repository
    unlocked.

    git-crypt locks the whole repository at once, so the unlock state
    is shared between the views: the runner of one view must not lock
    the secrets that were unlocked for all of them.
    """
    project_dir = make_git_crypt_project(run_debops, tmp_path, gpg_env,
                                         "example-gitcrypt-views")
    run_debops("project", "mkview", "other", cwd=str(project_dir),
               env=gpg_env, check=True)
    _commit_all(project_dir, gpg_env, "Add the other view")
    run_debops("project", "unlock", cwd=str(project_dir),
               env=gpg_env, check=True)

    result = run_debops("env", "-V", "other", "/bin/true",
                        cwd=str(project_dir), env=gpg_env)

    assert result.returncode == 0
    assert not _git_crypt_is_locked(project_dir)
    # The repository-wide lock state: the default view's secrets are
    # readable too
    assert (project_dir / "ansible" / "views" / "system" / "secret" /
            "credentials.txt").read_text() == "hunter2\n"


@encfs
def test_runner_commands_leave_already_unlocked_encfs_mounted(
        run_debops, tmp_path, gpg_env):
    """The EncFS volume stays mounted when the command unlocked
    nothing."""
    project_dir = tmp_path / "example-encfs-runner"
    run_debops("project", "init", "-t", "modern", "--encrypt", "encfs",
               "--keys", "debops-tests@example.org", "--no-requirements",
               str(project_dir), env=gpg_env, check=True)
    secrets = project_dir / "ansible" / "views" / "system" / "secret"

    result = run_debops("project", "unlock", cwd=str(project_dir),
                        env=gpg_env)
    assert result.returncode == 0
    assert os.path.ismount(str(secrets))

    result = run_debops("env", "/bin/true", cwd=str(project_dir),
                        env=gpg_env)

    assert result.returncode == 0
    assert os.path.ismount(str(secrets)), \
        "the command unmounted a volume it did not mount"


@git_crypt
def test_mkview_encrypts_git_crypt_view_secrets(run_debops, tmp_path,
                                                gpg_env):
    """A view created with '--encrypt git-crypt' encrypts its secrets.

    The view's '.gitattributes' declares the git-crypt filter, and a
    secret committed after the view creation lands in the repository
    as git-crypt ciphertext. 'mkview' used to drop the encryption
    options, and the secrets of the new view were stored as plaintext.
    """
    project_dir = make_git_crypt_project(run_debops, tmp_path, gpg_env,
                                         "example-gitcrypt-mkview")
    run_debops("project", "unlock", cwd=str(project_dir),
               env=gpg_env, check=True)

    result = run_debops("project", "mkview", "--encrypt", "git-crypt",
                        "--keys", "debops-tests@example.org", "other",
                        cwd=str(project_dir), env=gpg_env)
    assert result.returncode == 0

    attributes = (project_dir / "ansible" / "views" / "other" /
                  ".gitattributes").read_text()
    assert "/secret/** filter=git-crypt" in attributes
    assert "#/secret" not in attributes, \
        "the git-crypt filter declaration is inactive"

    secret = (project_dir / "ansible" / "views" / "other" /
              "secret" / "key.txt")
    secret.write_text("view-secret\n")
    _commit_all(project_dir, gpg_env, "Add a secret to the new view")

    blob = subprocess.run(
        ["git", "cat-file", "blob",
         "HEAD:ansible/views/other/secret/key.txt"],
        cwd=str(project_dir), check=True, capture_output=True).stdout
    assert blob.startswith(b"\x00GITCRYPT\x00"), \
        "the secret of the new view was stored as plaintext"


@git_crypt
def test_env_stops_when_the_auto_commit_is_refused(run_debops, tmp_path,
                                                   gpg_env):
    """A runner command stops before it starts when the automatic
    commit refuses to store encrypted paths as plaintext.

    The generated projects enable the auto-commit. A new secret file
    in the secrets of a locked repository used to be committed as
    plaintext, the repository unlocked, and the command executed. The
    command must stop instead: the state needs the operator's
    decision, not automatic data destruction."""
    project_dir = make_git_crypt_project(run_debops, tmp_path, gpg_env,
                                         "example-gitcrypt-refusal")
    head_before = _head_commit(project_dir)
    secret = (project_dir / "ansible" / "views" / "system" / "secret" /
              "new-key.txt")
    secret.write_text("brand-new\n")

    result = run_debops("env", "touch RAN", cwd=str(project_dir),
                        env=gpg_env)

    assert result.returncode == 1
    assert "plaintext" in result.stderr
    assert not (project_dir / "RAN").exists(), \
        "the command ran despite the refusal"
    assert _git_crypt_is_locked(project_dir)
    assert _head_commit(project_dir) == head_before, \
        "the working tree was committed automatically"


@git_crypt
def test_run_stops_when_the_auto_commit_is_refused(run_debops, tmp_path,
                                                   gpg_env):
    """'debops run' stops before the playbook starts when the
    automatic commit refuses to store encrypted paths as plaintext."""
    project_dir = make_git_crypt_project(run_debops, tmp_path, gpg_env,
                                         "example-gitcrypt-refusal-run")
    head_before = _head_commit(project_dir)
    secret = (project_dir / "ansible" / "views" / "system" / "secret" /
              "new-key.txt")
    secret.write_text("brand-new\n")

    result = run_debops("run", "site.yml", cwd=str(project_dir),
                        env=gpg_env)

    assert result.returncode == 1
    assert "plaintext" in result.stderr
    assert "PLAY RECAP" not in result.stdout, \
        "the playbook ran despite the refusal"
    assert _git_crypt_is_locked(project_dir)
    assert _head_commit(project_dir) == head_before, \
        "the working tree was committed automatically"
