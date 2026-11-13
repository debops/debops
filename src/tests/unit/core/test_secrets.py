# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for ``debops.core.ansible.secrets``.

``AnsibleSecretStore`` manages one encrypted secret directory of a
project view: the EncFS and git-crypt detection, the unlock and lock
operations and the initial encryption setup. Operations that would run
real subcommands are isolated with mocks.
"""

import logging
import os
import string
from unittest import mock

import pytest

import debops.core.secrets as secrets_module
from debops.core.ansible.secrets import AnsibleSecretStore
from debops.core.secrets import SecretManager


def make_store(project, view="system", **kwargs):
    return AnsibleSecretStore(project, view=view, **kwargs)


def test_encfs_secrets_are_detected(stub_project):
    project = stub_project()
    os.makedirs(os.path.join(project.path, "ansible", ".encfs.secret"))

    store = make_store(project)

    assert store.encrypted
    assert store.crypt_method == "encfs"
    assert not store.decrypted


def test_git_crypt_secrets_are_detected(stub_project, monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, ".git", "git-crypt", "keys"))
    monkeypatch.setattr(AnsibleSecretStore, "_git_crypt_locked",
                        mock.Mock(return_value=True))

    store = make_store(project)

    assert store.encrypted
    assert store.crypt_method == "git-crypt"
    assert not store.decrypted


def test_unlocked_git_crypt_is_reported_as_mounted(stub_project, monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, ".git", "git-crypt", "keys"))
    monkeypatch.setattr(AnsibleSecretStore, "_git_crypt_locked",
                        mock.Mock(return_value=False))

    store = make_store(project)

    assert store.decrypted


def test_git_crypt_locked_detects_an_unlocked_state(stub_project, monkeypatch):
    store = make_store(stub_project())
    process = mock.Mock()
    process.communicate.return_value = (b"smudge", b"")
    popen = mock.Mock(return_value=process)
    monkeypatch.setattr(secrets_module.subprocess, "Popen", popen)

    assert store._git_crypt_locked() is False
    assert popen.call_args.args[0] == [
        store._commands["git"], "config", "--local", "--get",
        "filter.git-crypt.smudge"]


def test_git_crypt_locked_detects_a_locked_state(stub_project, monkeypatch):
    store = make_store(stub_project())
    process = mock.Mock()
    process.communicate.return_value = (b"", b"")
    popen = mock.Mock(return_value=process)
    monkeypatch.setattr(secrets_module.subprocess, "Popen", popen)

    assert store._git_crypt_locked() is True
    assert popen.call_args.args[0] == [
        store._commands["git"], "config", "--local", "--get",
        "filter.git-crypt.smudge"]


def test_random_string_uses_sixty_four_characters(stub_project):
    allowed = set(string.digits + string.ascii_letters + string.punctuation)
    store = make_store(stub_project())

    value = store._get_random_string()

    assert len(value) == 64
    assert set(value) <= allowed


def test_encrypt_secrets_encfs_completes_the_key_exchange(stub_project,
                                                          monkeypatch):
    """The EncFS encryption state machine: GPG encrypts the keyfile,
    EncFS mounts the volume and writes its configuration, GPG encrypts
    the configuration and the plaintext copy is removed."""
    project = stub_project()
    store = make_store(project, encrypt="encfs",
                       keys="test@example.org")
    keyfile = os.path.join(store.encfs_path, '.encfs6.keyfile')
    configfile = os.path.join(store.encfs_path, '.encfs6.xml')

    def make_process(side_effect):
        process = mock.Mock(returncode=0)
        process.communicate.side_effect = side_effect
        return process

    def create_keyfile(*args, **kwargs):
        open(keyfile, 'w').close()
        return b"", b""

    def create_configfile(*args, **kwargs):
        open(configfile, 'w').close()
        return b"", b""

    ascfile = configfile + '.asc'

    def create_ascfile():
        open(ascfile, 'w').close()
        return b"", b""

    processes = [make_process(create_keyfile), make_process(create_configfile),
                 make_process(create_ascfile)]
    popen = mock.Mock(side_effect=processes)
    monkeypatch.setattr(secrets_module.subprocess, "Popen", popen)
    monkeypatch.setattr(os.path, "ismount", lambda path: True)
    call = mock.Mock(return_value=0)
    monkeypatch.setattr(secrets_module.subprocess, "call", call)

    store.encrypt_encfs()

    assert os.path.isfile(keyfile)
    assert os.path.isfile(ascfile)
    assert not os.path.exists(configfile)
    # The volume was mounted by EncFS and locked afterwards
    call.assert_called_once_with(
        [store._commands["fusermount"], "-u", store.secret_path])
    assert store.decrypted is False
    assert [popen.call_args_list[i].args[0][0]
            for i in range(3)] == [store._commands["gpg"],
                                   store._commands["encfs"],
                                   store._commands["gpg"]]


@pytest.mark.parametrize("step", ["keyfile", "volume"])
def test_encrypt_secrets_encfs_reports_a_failed_step(stub_project,
                                                     monkeypatch, step):
    project = stub_project()
    store = make_store(project, encrypt="encfs",
                       keys="test@example.org")
    keyfile = os.path.join(store.encfs_path, '.encfs6.keyfile')
    configfile = os.path.join(store.encfs_path, '.encfs6.xml')

    def make_process(returncode, side_effect):
        process = mock.Mock(returncode=returncode)
        process.communicate.side_effect = side_effect
        return process

    if step == "keyfile":
        processes = [make_process(1, lambda *a, **kw: (b"", b""))]
        match = "keyfile"
    else:
        def create_keyfile(*args, **kwargs):
            open(keyfile, 'w').close()
            return b"", b""
        processes = [make_process(0, create_keyfile),
                     make_process(1, lambda *a, **kw: (b"", b""))]
        match = "volume configuration"
    monkeypatch.setattr(secrets_module.subprocess, "Popen",
                        mock.Mock(side_effect=processes))

    with pytest.raises(ChildProcessError, match=match):
        store.encrypt_encfs()


def test_encrypt_secrets_encfs_reports_a_failed_config_encryption(
        stub_project, monkeypatch):
    project = stub_project()
    store = make_store(project, encrypt="encfs",
                       keys="test@example.org")
    keyfile = os.path.join(store.encfs_path, '.encfs6.keyfile')
    configfile = os.path.join(store.encfs_path, '.encfs6.xml')
    ascfile = configfile + '.asc'

    def make_process(returncode, side_effect):
        process = mock.Mock(returncode=returncode)
        process.communicate.side_effect = side_effect
        return process

    def create_keyfile(*args, **kwargs):
        open(keyfile, 'w').close()
        return b"", b""

    def create_configfile(*args, **kwargs):
        open(configfile, 'w').close()
        return b"", b""

    processes = [make_process(0, create_keyfile),
                 make_process(0, create_configfile),
                 make_process(1, lambda: (b"", b""))]
    monkeypatch.setattr(secrets_module.subprocess, "Popen",
                        mock.Mock(side_effect=processes))
    monkeypatch.setattr(os.path, "ismount", lambda path: True)
    monkeypatch.setattr(secrets_module.subprocess, "call",
                        mock.Mock(return_value=0))

    with pytest.raises(ChildProcessError,
                       match="encrypt the volume configuration"):
        store.encrypt_encfs()

    # The plaintext configuration stays on disk: it was never replaced
    assert os.path.isfile(configfile)
    assert not os.path.exists(ascfile)


def test_unlock_encfs_reports_a_failed_mount(stub_project, monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, "ansible", ".encfs.secret"))
    store = make_store(project)
    process = mock.Mock(returncode=1)
    process.communicate.return_value = (b"", b"")
    monkeypatch.setattr(secrets_module.subprocess, "Popen",
                        mock.Mock(return_value=process))
    # The configuration fifo is mocked into a regular file: the test
    # subprocesses never open the read end, so a real fifo would block
    # the write end forever
    monkeypatch.setattr(secrets_module.os, "mkfifo",
                        lambda path: open(path, 'w').close())
    configfile = os.path.join(store.encfs_path, store.encfs_configfile)

    with pytest.raises(ChildProcessError, match="could not unlock"):
        store.unlock()

    # The fifo used for the configuration transfer is cleaned up
    assert not os.path.exists(configfile)
    assert store.decrypted is False


def test_encrypt_encfs_requires_gpg_keys(stub_project):
    store = make_store(stub_project(), encrypt="encfs")

    with pytest.raises(ValueError):
        store.encrypt_encfs()


def test_unlock_returns_false_for_a_plain_inventory(stub_project):
    project = stub_project()
    store = make_store(project)
    os.makedirs(os.path.join(project.path, "ansible"))

    assert store.unlock() is False


def test_unlock_fails_when_the_inventory_directory_is_missing(stub_project):
    store = make_store(stub_project())

    with pytest.raises(NotADirectoryError):
        store.unlock()


def test_unlock_encfs_skips_an_already_mounted_volume(stub_project,
                                                      monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, "ansible", ".encfs.secret"))
    store = make_store(project)
    monkeypatch.setattr(os.path, "ismount", lambda path: True)

    assert store.unlock() is False


def test_unlock_encfs_rejects_a_regular_config_file(stub_project):
    project = stub_project()
    encfs_dir = os.path.join(project.path, "ansible", ".encfs.secret")
    os.makedirs(encfs_dir)
    open(os.path.join(encfs_dir, ".encfs6.xml"), "w").write("not a fifo")
    open(os.path.join(encfs_dir, ".encfs6.xml.asc"), "w").write("encrypted")

    store = make_store(project)

    with pytest.raises(IOError):
        store.unlock()


def test_unlock_git_crypt_unlocks_the_secrets(stub_project, monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, ".git", "git-crypt", "keys"))
    monkeypatch.setattr(AnsibleSecretStore, "_git_crypt_locked",
                        mock.Mock(return_value=True))
    process = mock.Mock()
    process.communicate.return_value = (b"", b"")
    process.returncode = 0
    popen = mock.Mock(return_value=process)
    monkeypatch.setattr(secrets_module.subprocess, "Popen", popen)
    store = make_store(project)

    assert store.unlock() is True
    assert store.decrypted
    assert popen.call_args.args[0] == [store._commands["git-crypt"],
                                       "unlock"]


def test_unlock_git_crypt_reports_a_dirty_working_tree(stub_project,
                                                       monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, ".git", "git-crypt", "keys"))
    monkeypatch.setattr(AnsibleSecretStore, "_git_crypt_locked",
                        mock.Mock(return_value=True))
    process = mock.Mock()
    process.communicate.return_value = (b"", b"error")
    process.returncode = 1
    monkeypatch.setattr(secrets_module.subprocess, "Popen",
                        mock.Mock(return_value=process))
    store = make_store(project)

    with pytest.raises(ChildProcessError) as caught:
        store.unlock()

    assert "Cannot unlock" in str(caught.value)


def test_unlock_git_crypt_skips_an_already_unlocked_repository(
        stub_project, monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, ".git", "git-crypt", "keys"))
    monkeypatch.setattr(AnsibleSecretStore, "_git_crypt_locked",
                        mock.Mock(return_value=False))
    store = make_store(project)

    assert store.unlock() is False
    assert store.decrypted


def test_lock_git_crypt_locks_the_secrets(stub_project, monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, ".git", "git-crypt", "keys"))
    monkeypatch.setattr(AnsibleSecretStore, "_git_crypt_locked",
                        mock.Mock(return_value=False))
    process = mock.Mock()
    process.communicate.return_value = (b"", b"")
    process.returncode = 0
    popen = mock.Mock(return_value=process)
    monkeypatch.setattr(secrets_module.subprocess, "Popen", popen)
    store = make_store(project)

    assert store.lock() is True
    assert not store.decrypted
    assert popen.call_args.args[0] == [store._commands["git-crypt"],
                                       "lock"]


def test_lock_git_crypt_is_a_noop_when_already_locked(stub_project,
                                                      monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, ".git", "git-crypt", "keys"))
    monkeypatch.setattr(AnsibleSecretStore, "_git_crypt_locked",
                        mock.Mock(return_value=True))
    popen = mock.Mock()
    monkeypatch.setattr(secrets_module.subprocess, "Popen", popen)
    store = make_store(project)

    assert store.lock() is None
    popen.assert_not_called()


def test_lock_encfs_unmounts_the_volume(stub_project, monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, "ansible", ".encfs.secret"))
    store = make_store(project)
    monkeypatch.setattr(os.path, "ismount", lambda path: True)
    call = mock.Mock(return_value=0)
    monkeypatch.setattr(secrets_module.subprocess, "call", call)

    assert store.lock() is True
    assert not store.decrypted
    call.assert_called_once_with(
        [store._commands["fusermount"], "-u",
         store.secret_path])


def test_lock_returns_false_for_a_plain_inventory(stub_project):
    project = stub_project()
    store = make_store(project)
    os.makedirs(os.path.join(project.path, "ansible"))

    assert store.lock() is False


def test_lock_fails_when_the_inventory_directory_is_missing(stub_project):
    store = make_store(stub_project())

    with pytest.raises(NotADirectoryError):
        store.lock()


def test_encfs_mount_is_detected_at_init(stub_project, monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, "ansible", ".encfs.secret"))
    monkeypatch.setattr(os.path, "ismount", lambda path: True)

    store = make_store(project)

    assert store.decrypted


def test_unlock_encfs_commits_before_mounting(stub_project, monkeypatch):
    project = stub_project()
    project.config.raw["project"] = {"git": {"auto_commit": True}}
    project.commit = mock.Mock()
    os.makedirs(os.path.join(project.path, "ansible", ".encfs.secret"))
    monkeypatch.setattr(secrets_module.os, "mkfifo",
                        lambda path: open(path, "w").close())
    process = mock.Mock()
    process.communicate.return_value = (b"", b"")
    process.returncode = 0
    monkeypatch.setattr(secrets_module.subprocess, "Popen",
                        mock.Mock(return_value=process))
    store = make_store(project)

    assert store.unlock() is True
    project.commit.assert_called_once_with()


def test_unlock_git_crypt_commits_before_unlocking(stub_project, monkeypatch):
    project = stub_project()
    project.config.raw["project"] = {"git": {"auto_commit": True}}
    project.commit = mock.Mock()
    os.makedirs(os.path.join(project.path, ".git", "git-crypt", "keys"))
    monkeypatch.setattr(AnsibleSecretStore, "_git_crypt_locked",
                        mock.Mock(return_value=True))
    process = mock.Mock()
    process.communicate.return_value = (b"", b"")
    process.returncode = 0
    monkeypatch.setattr(secrets_module.subprocess, "Popen",
                        mock.Mock(return_value=process))
    store = make_store(project)

    assert store.unlock() is True
    project.commit.assert_called_once_with()


def test_lock_commits_before_locking(stub_project):
    project = stub_project()
    project.config.raw["project"] = {"git": {"auto_commit": True}}
    project.commit = mock.Mock()
    os.makedirs(os.path.join(project.path, "ansible", ".encfs.secret"))
    store = make_store(project)

    store.lock()

    project.commit.assert_called_once_with()


def test_lock_uses_umount_on_macos(stub_project, monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, "ansible", ".encfs.secret"))
    store = make_store(project)
    monkeypatch.setattr(os.path, "ismount", lambda path: True)
    monkeypatch.setattr(secrets_module.sys, "platform", "darwin")
    call = mock.Mock(return_value=0)
    monkeypatch.setattr(secrets_module.subprocess, "call", call)

    assert store.lock() is True
    call.assert_called_once_with([store._commands["umount"],
                                  store.secret_path])


def test_lock_git_crypt_reports_a_failure(stub_project, monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, ".git", "git-crypt", "keys"))
    monkeypatch.setattr(AnsibleSecretStore, "_git_crypt_locked",
                        mock.Mock(return_value=False))
    process = mock.Mock()
    process.communicate.return_value = (b"", b"error")
    process.returncode = 1
    monkeypatch.setattr(secrets_module.subprocess, "Popen",
                        mock.Mock(return_value=process))
    store = make_store(project)

    with pytest.raises(ChildProcessError, match="Cannot lock"):
        store.lock()


def make_manager(project, stores):
    """A ``SecretManager`` whose registered factories return the given
    store mocks, keyed by store name."""
    manager = SecretManager(project)
    manager._factories = lambda: {
        name: (lambda project, view, store=store: store)
        for name, store in stores.items()}
    return manager


def test_manager_unlock_returns_one_result_per_store(stub_project):
    """The manager unlocks every registered store and reports one
    result per store, in the registration order."""
    ansible = mock.Mock()
    ansible.unlock.return_value = True
    other = mock.Mock()
    other.unlock.return_value = False
    manager = make_manager(stub_project(),
                           {"ansible": ansible, "other": other})

    assert manager.unlock() == [True, False]


def test_manager_unlock_selects_a_named_store(stub_project):
    ansible = mock.Mock()
    ansible.unlock.return_value = True
    other = mock.Mock()
    manager = make_manager(stub_project(),
                           {"ansible": ansible, "other": other})

    assert manager.unlock("ansible") == [True]
    other.unlock.assert_not_called()


def test_manager_lock_returns_one_result_per_store(stub_project):
    ansible = mock.Mock()
    ansible.lock.return_value = True
    other = mock.Mock()
    other.lock.return_value = False
    manager = make_manager(stub_project(),
                           {"ansible": ansible, "other": other})

    assert manager.lock() == [True, False]


def test_manager_rejects_an_unknown_store_name(stub_project):
    manager = make_manager(stub_project(), {"ansible": mock.Mock()})

    with pytest.raises(KeyError):
        manager.store("nope")


def test_unlock_refuses_to_autocommit_encrypted_paths(stub_project,
                                                      monkeypatch, caplog):
    """The automatic commit refuses to run while the repository is
    locked and the working tree changes git-crypt encrypted paths. The
    clean filter of a locked repository passes content through, so the
    commit would store the encrypted files as plaintext."""
    project = stub_project()
    project.config.raw["project"] = {"git": {"auto_commit": True}}
    project.commit = mock.Mock()
    os.makedirs(os.path.join(project.path, ".git", "git-crypt", "keys"))
    monkeypatch.setattr(AnsibleSecretStore, "_git_crypt_locked",
                        mock.Mock(return_value=True))
    monkeypatch.setattr(AnsibleSecretStore, "_git_crypt_encrypted_changes",
                        mock.Mock(return_value=["secret/keys.yml"]))
    store = make_store(project)

    with caplog.at_level(logging.ERROR, logger="debops.core.secrets"):
        with pytest.raises(ChildProcessError,
                           match="would store as plaintext"):
            store.unlock()

    project.commit.assert_not_called()
    assert "plaintext" in caplog.text
    assert "secret/keys.yml" in caplog.text


def test_unlock_autocommits_changes_outside_the_encrypted_paths(
        stub_project, monkeypatch):
    """Changes outside the encrypted paths commit automatically while
    the repository is locked: the tree must be clean for the unlock,
    and non-encrypted content commits as plaintext harmlessly."""
    project = stub_project()
    project.config.raw["project"] = {"git": {"auto_commit": True}}
    project.commit = mock.Mock()
    os.makedirs(os.path.join(project.path, ".git", "git-crypt", "keys"))
    monkeypatch.setattr(AnsibleSecretStore, "_git_crypt_locked",
                        mock.Mock(return_value=True))
    monkeypatch.setattr(AnsibleSecretStore, "_git_crypt_encrypted_changes",
                        mock.Mock(return_value=[]))
    process = mock.Mock(returncode=0)
    process.communicate.return_value = (b"", b"")
    monkeypatch.setattr(secrets_module.subprocess, "Popen",
                        mock.Mock(return_value=process))
    store = make_store(project)

    assert store.unlock() is True
    project.commit.assert_called_once_with()


def test_git_crypt_encrypted_changes_filters_by_the_filter_attribute(
        stub_project, monkeypatch):
    """The helper reports only the changed paths whose filter
    attribute names git-crypt, and runs its lookups in the project
    directory."""
    project = stub_project()
    store = make_store(project)

    status = mock.Mock(returncode=0)
    status.communicate.return_value = (
        b" M ansible/views/system/secret/keys.yml\n"
        b" M README.md\n"
        b"?? secret/new-file.txt\n", b"")
    attrs = mock.Mock(returncode=0)
    attrs.communicate.return_value = (
        b"ansible/views/system/secret/keys.yml: filter: git-crypt\n"
        b"README.md: filter: unspecified\n"
        b"secret/new-file.txt: filter: git-crypt\n", b"")
    popen = mock.Mock(side_effect=[status, attrs])
    monkeypatch.setattr(secrets_module.subprocess, "Popen", popen)

    changes = store._git_crypt_encrypted_changes()

    assert sorted(changes) == ["ansible/views/system/secret/keys.yml",
                               "secret/new-file.txt"]
    assert [call.kwargs["cwd"] for call in popen.call_args_list] == \
        [project.path, project.path]
    stdin = attrs.communicate.call_args.args[0].decode()
    assert "secret/new-file.txt" in stdin
    assert "README.md" in stdin
