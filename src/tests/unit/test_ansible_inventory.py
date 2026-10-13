# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for ``debops.ansible.inventory``.

``AnsibleInventory`` is constructed from a project object; the stubs from the
shared fixtures provide its ``project_type``, ``path`` and the binary paths.
Secret operations that would run real subcommands are isolated with mocks.
"""

import os
import string
from unittest import mock

import pytest

import debops.ansible.inventory as inventory_module
from debops.ansible.inventory import AnsibleInventory
from debops.exceptions import NoDefaultViewException


def make_inventory(project, name="system", **kwargs):
    return AnsibleInventory(project, name=name, **kwargs)


def test_legacy_project_uses_the_ansible_directory(stub_project):
    project = stub_project(project_type="legacy")
    inventory = make_inventory(project)

    assert inventory.path == os.path.join(project.path, "ansible", "inventory")
    assert inventory.secret_path == os.path.join(project.path, "ansible",
                                                 "secret")
    assert not inventory.encrypted


def test_modern_project_uses_the_view_directory(stub_project):
    project = stub_project(project_type="modern")
    inventory = make_inventory(project, name="webservers")

    assert inventory.path == os.path.join(project.path, "ansible", "views",
                                          "webservers", "inventory")


def test_modern_project_requires_a_view(stub_project):
    project = stub_project(project_type="modern")

    with pytest.raises(NoDefaultViewException):
        make_inventory(project, name="")


def test_encfs_secrets_are_detected(stub_project):
    project = stub_project()
    os.makedirs(os.path.join(project.path, "ansible", ".encfs.secret"))

    inventory = make_inventory(project)

    assert inventory.encrypted
    assert inventory.crypt_method == "encfs"
    assert not inventory.encfs_mounted


def test_git_crypt_secrets_are_detected(stub_project, monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, ".git", "git-crypt", "keys"))
    monkeypatch.setattr(inventory_module.AnsibleInventory, "_git_crypt_locked",
                        mock.Mock(return_value=True))

    inventory = make_inventory(project)

    assert inventory.encrypted
    assert inventory.crypt_method == "git-crypt"
    assert not inventory.encfs_mounted


def test_unlocked_git_crypt_is_reported_as_mounted(stub_project, monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, ".git", "git-crypt", "keys"))
    monkeypatch.setattr(inventory_module.AnsibleInventory, "_git_crypt_locked",
                        mock.Mock(return_value=False))

    inventory = make_inventory(project)

    assert inventory.encfs_mounted


def test_git_crypt_locked_detects_an_unlocked_state(stub_project, monkeypatch):
    inventory = make_inventory(stub_project())
    process = mock.Mock()
    process.communicate.return_value = (b"smudge", b"")
    monkeypatch.setattr(inventory_module.subprocess, "Popen",
                        mock.Mock(return_value=process))

    assert inventory._git_crypt_locked() is False


def test_git_crypt_locked_detects_a_locked_state(stub_project, monkeypatch):
    inventory = make_inventory(stub_project())
    process = mock.Mock()
    process.communicate.return_value = (b"", b"")
    monkeypatch.setattr(inventory_module.subprocess, "Popen",
                        mock.Mock(return_value=process))

    assert inventory._git_crypt_locked() is True


def test_random_string_uses_sixty_four_characters(stub_project):
    allowed = set(string.digits + string.ascii_letters + string.punctuation)
    inventory = make_inventory(stub_project())

    value = inventory._get_random_string()

    assert len(value) == 64
    assert set(value) <= allowed


def test_existing_paths_lists_files_and_directories(stub_project):
    project = stub_project()
    inventory = make_inventory(project)
    os.makedirs(os.path.join(project.path, "ansible", "inventory",
                             "group_vars"))
    open(os.path.join(project.path, "ansible", "inventory", "hosts"),
         "w").close()

    found = inventory.existing_paths()

    assert found == {
        os.path.realpath(
            os.path.join(project.path, "ansible", "inventory", "hosts")),
        os.path.realpath(
            os.path.join(project.path, "ansible", "inventory", "group_vars")),
    }


def test_existing_paths_is_empty_for_a_missing_inventory(stub_project):
    inventory = make_inventory(stub_project())

    assert inventory.existing_paths() == set()


def test_apply_spec_forwards_to_the_spec_engine(stub_project, monkeypatch):
    project = stub_project()
    inventory = make_inventory(project)
    result = mock.Mock()
    monkeypatch.setattr(inventory_module, "apply_spec",
                        mock.Mock(return_value=result))

    applied = inventory.apply_spec({"a": 1}, pre_existing={"x"},
                                   overwrite=True, dry_run=False, keep=("a",))

    assert applied is result
    inventory_module.apply_spec.assert_called_once_with(
        {"a": 1}, inventory.path, pre_existing={"x"}, overwrite=True,
        dry_run=False, keep=("a",))


@pytest.mark.parametrize("directory", [
    "inventory/group_vars/all",
    "inventory/host_vars",
    "playbooks/roles",
    "resources/templates/by-group/all",
    "resources/templates/by-host",
    "secret",
])
def test_createdirs_builds_the_common_skeleton(stub_project, directory):
    project = stub_project()
    make_inventory(project).createdirs()

    assert os.path.isdir(os.path.join(project.path, "ansible", directory))


@pytest.mark.parametrize("directory", [
    "collections/ansible_collections",
    "keyring",
    "overrides/files",
    "overrides/tasks",
    "overrides/templates",
])
def test_createdirs_builds_the_legacy_only_skeleton(stub_project, directory):
    project = stub_project(project_type="legacy")
    make_inventory(project).createdirs()

    assert os.path.isdir(os.path.join(project.path, "ansible", directory))


@pytest.mark.parametrize("directory", [
    "collections/ansible_collections",
    "keyring",
    "overrides/files",
])
def test_createdirs_omits_the_legacy_only_skeleton_in_modern_projects(
        stub_project, directory):
    project = stub_project(project_type="modern")
    make_inventory(project, name="system").createdirs()

    assert not os.path.exists(os.path.join(project.path, "ansible", directory))


def test_create_builds_an_inventory_with_a_hosts_file(stub_project):
    project = stub_project()
    make_inventory(project).create()

    hosts_file = os.path.join(project.path, "ansible", "inventory", "hosts")
    assert os.path.exists(hosts_file)


def test_create_rejects_an_existing_root_directory(stub_project):
    project = stub_project()
    os.makedirs(os.path.join(project.path, "ansible"))

    with pytest.raises(IsADirectoryError):
        make_inventory(project).create()


def test_create_encrypts_secrets_with_encfs(stub_project, monkeypatch):
    project = stub_project()
    inventory = make_inventory(project, encrypt="encfs")
    monkeypatch.setattr(inventory_module.AnsibleInventory,
                        "_encrypt_secrets_encfs", mock.Mock())

    inventory.create()

    inventory._encrypt_secrets_encfs.assert_called_once_with()


def test_create_encrypted_git_crypt_is_handled_at_the_repository_level(
        stub_project):
    project = stub_project()
    make_inventory(project, encrypt="git-crypt").create()

    assert os.path.exists(
        os.path.join(project.path, "ansible", "inventory", "hosts"))


def test_encrypt_encfs_requires_gpg_keys(stub_project):
    inventory = make_inventory(stub_project(), encrypt="encfs")

    with pytest.raises(ValueError):
        inventory._encrypt_secrets_encfs()


def test_unlock_returns_false_for_a_plain_inventory(stub_project):
    project = stub_project()
    inventory = make_inventory(project)
    os.makedirs(os.path.join(project.path, "ansible"))

    assert inventory.unlock() is False


def test_unlock_fails_when_the_inventory_directory_is_missing(stub_project):
    inventory = make_inventory(stub_project())

    with pytest.raises(NotADirectoryError):
        inventory.unlock()


def test_unlock_encfs_skips_an_already_mounted_volume(stub_project,
                                                      monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, "ansible", ".encfs.secret"))
    inventory = make_inventory(project)
    monkeypatch.setattr(os.path, "ismount", lambda path: True)

    assert inventory.unlock() is False


def test_unlock_encfs_rejects_a_regular_config_file(stub_project):
    project = stub_project()
    encfs_dir = os.path.join(project.path, "ansible", ".encfs.secret")
    os.makedirs(encfs_dir)
    open(os.path.join(encfs_dir, ".encfs6.xml"), "w").write("not a fifo")
    open(os.path.join(encfs_dir, ".encfs6.xml.asc"), "w").write("encrypted")

    inventory = make_inventory(project)

    with pytest.raises(IOError):
        inventory.unlock()


def test_unlock_git_crypt_unlocks_the_secrets(stub_project, monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, ".git", "git-crypt", "keys"))
    monkeypatch.setattr(inventory_module.AnsibleInventory, "_git_crypt_locked",
                        mock.Mock(return_value=True))
    process = mock.Mock()
    process.communicate.return_value = (b"", b"")
    process.returncode = 0
    popen = mock.Mock(return_value=process)
    monkeypatch.setattr(inventory_module.subprocess, "Popen", popen)
    inventory = make_inventory(project)

    assert inventory.unlock() is True
    assert inventory.encfs_mounted
    assert popen.call_args.args[0] == [inventory._commands["git-crypt"],
                                       "unlock"]


def test_unlock_git_crypt_reports_a_dirty_working_tree(stub_project,
                                                       monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, ".git", "git-crypt", "keys"))
    monkeypatch.setattr(inventory_module.AnsibleInventory, "_git_crypt_locked",
                        mock.Mock(return_value=True))
    process = mock.Mock()
    process.communicate.return_value = (b"", b"error")
    process.returncode = 1
    monkeypatch.setattr(inventory_module.subprocess, "Popen",
                        mock.Mock(return_value=process))
    inventory = make_inventory(project)

    with pytest.raises(ChildProcessError) as caught:
        inventory.unlock()

    assert "Cannot unlock" in str(caught.value)


def test_unlock_git_crypt_skips_an_already_unlocked_repository(
        stub_project, monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, ".git", "git-crypt", "keys"))
    monkeypatch.setattr(inventory_module.AnsibleInventory, "_git_crypt_locked",
                        mock.Mock(return_value=False))
    inventory = make_inventory(project)

    assert inventory.unlock() is False
    assert inventory.encfs_mounted


def test_lock_git_crypt_locks_the_secrets(stub_project, monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, ".git", "git-crypt", "keys"))
    monkeypatch.setattr(inventory_module.AnsibleInventory, "_git_crypt_locked",
                        mock.Mock(return_value=False))
    process = mock.Mock()
    process.communicate.return_value = (b"", b"")
    process.returncode = 0
    popen = mock.Mock(return_value=process)
    monkeypatch.setattr(inventory_module.subprocess, "Popen", popen)
    inventory = make_inventory(project)

    assert inventory.lock() is True
    assert not inventory.encfs_mounted
    assert popen.call_args.args[0] == [inventory._commands["git-crypt"],
                                       "lock"]


def test_lock_git_crypt_is_a_noop_when_already_locked(stub_project,
                                                      monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, ".git", "git-crypt", "keys"))
    monkeypatch.setattr(inventory_module.AnsibleInventory, "_git_crypt_locked",
                        mock.Mock(return_value=True))
    popen = mock.Mock()
    monkeypatch.setattr(inventory_module.subprocess, "Popen", popen)
    inventory = make_inventory(project)

    assert inventory.lock() is None
    popen.assert_not_called()


def test_lock_encfs_unmounts_the_volume(stub_project, monkeypatch):
    project = stub_project()
    os.makedirs(os.path.join(project.path, "ansible", ".encfs.secret"))
    inventory = make_inventory(project)
    monkeypatch.setattr(os.path, "ismount", lambda path: True)
    call = mock.Mock(return_value=0)
    monkeypatch.setattr(inventory_module.subprocess, "call", call)

    assert inventory.lock() is True
    assert not inventory.encfs_mounted
    call.assert_called_once_with(
        [inventory._commands["fusermount"], "-u",
         inventory.secret_path])


def test_lock_returns_false_for_a_plain_inventory(stub_project):
    project = stub_project()
    inventory = make_inventory(project)
    os.makedirs(os.path.join(project.path, "ansible"))

    assert inventory.lock() is False
