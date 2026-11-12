# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for ``debops.core.ansible.inventory``.

The secret lifecycle tests live in ``test_secrets.py``; this module
covers the inventory paths, content and creation.

``AnsibleInventory`` is constructed from a project object; the stubs from the
shared fixtures provide its ``project_type``, ``path`` and the binary paths.
Secret operations that would run real subcommands are isolated with mocks.
"""

import os
import string
from unittest import mock

import pytest

import debops.core.ansible.inventory as inventory_module
from debops.core.ansible.inventory import AnsibleInventory
from debops.core.exceptions import NoDefaultViewException


def make_inventory(project, name="system"):
    return AnsibleInventory(project, name=name)


def test_legacy_project_uses_the_ansible_directory(stub_project):
    project = stub_project(project_type="legacy")
    inventory = make_inventory(project)

    assert inventory.path == os.path.join(project.path, "ansible", "inventory")


def test_modern_project_uses_the_view_directory(stub_project):
    project = stub_project(project_type="modern")
    inventory = make_inventory(project, name="webservers")

    assert inventory.path == os.path.join(project.path, "ansible", "views",
                                          "webservers", "inventory")


def test_modern_project_requires_a_view(stub_project):
    project = stub_project(project_type="modern")

    with pytest.raises(NoDefaultViewException):
        make_inventory(project, name="")


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
