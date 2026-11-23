# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import fcntl
import hashlib
import io
import json
import logging
import os
import re
import shutil
import stat
import subprocess
import sys
import textwrap
import time
from unittest import mock
import zipfile

import pytest

import debops.core.runner as runner_base_module
import debops.core.tofu.binary as binary_module
import debops.core.tofu.runner as runner_module
from debops.core.tofu import plans as plans_module
from debops.core.tofu.plans import plan_rows, resolve_plan_file
from debops.core.tofu.runner import TofuRunner
from debops.core.tofu.rekey import rekey_view
from debops.core.tofu.runner import TofuOperationFailed
from debops.core.tofu.view import create_view, reconcile_view
from debops.core.tofu.providers import resolve_providers
from debops.core.tofu.modules import resolve_modules
from debops.core.secrets import SecretManager
from tests.unit.core.tofu_helpers import (mkview,
                                          write_drop_in)


def test_mkview_requires_the_encrypt_decision(tofu_project):
    """The project without a secret store refuses the creation: the
    '--encrypt' decision is required, 'plain' being the explicit
    insecure one."""
    project = tofu_project(project_type="modern")
    with pytest.raises(ValueError,
                       match="'--encrypt' option is required"):
        create_view(project, "fresh", encrypt=None)


def test_mkview_follows_the_detected_git_crypt_store(
        tofu_project, monkeypatch):
    """The git-crypt store detected in the repository is the
    default: the view joins it, and the contradictory choices
    refuse."""
    project = tofu_project(project_type="modern")
    os.makedirs(os.path.join(project.path, '.git', 'git-crypt', 'keys'))
    monkeypatch.setattr(
        "debops.core.tofu.secrets.TofuSecretStore.unlock",
        lambda self: True)
    monkeypatch.setattr(
        "debops.core.tofu.secrets.TofuSecretStore.lock",
        lambda self: None)
    create_view(project, "fresh", encrypt=None)

    with pytest.raises(ValueError, match="contradicts"):
        create_view(project, "other", encrypt="encfs")
    with pytest.raises(ValueError, match="'plain' is not a choice"):
        create_view(project, "third", encrypt="plain")


def test_mkview_detected_encfs_requires_the_keys(tofu_project):
    """The EncFS store detected in the project makes the view join
    with a volume of its own: the '--keys' recipients are required,
    the '--encrypt' decision implied by the detection."""
    project = tofu_project(project_type="modern")
    os.makedirs(os.path.join(project.path, "ansible", "views",
                             "system", ".encfs.secret"))
    with pytest.raises(ValueError, match="'--keys'"):
        create_view(project, "fresh", encrypt=None)


def test_missing_view_tree_is_refused(tofu_project):
    """A command in a project without the view refuses with the way
    out: the views are created by 'debops tofu mkview'."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    with pytest.raises(ValueError, match="mkview"):
        TofuRunner(project, ["plan"]).execute()


def test_existing_view_is_left_alone(tofu_project):
    """An existing view is not re-created: its files are the user's."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    marker = os.path.join(view_dir, "main.tf")
    content = open(marker).read()

    TofuRunner(project, ["plan"])

    assert open(marker).read() == content


def test_broken_view_tree_is_completed(tofu_project, stub_tofu_subprocess):
    """A view directory without its configuration gains the template
    files; existing files are never overwritten."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    os.remove(os.path.join(view_dir, "main.tf"))
    custom = os.path.join(view_dir, "my-own.tf")
    with open(custom, "w") as handle:
        handle.write("# The user's own file\n")

    mkview(project)

    assert os.path.isfile(os.path.join(view_dir, "main.tf"))
    assert open(custom).read() == "# The user's own file\n"


def test_providers_come_from_the_configuration(tofu_project,
                                               stub_tofu_subprocess):
    """The 'tofu.default_providers' option is the default provider
    set of new views, recorded in the view's configuration drop-in."""
    project = tofu_project(project_type="modern",
                           raw={"tofu": {"mkview": {"default_providers":
                                         ["lxc/incus"],
                                         "default_modules": {}}}})
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    mkview(project)

    providers_tf = open(os.path.join(view_dir, "providers.tf")).read()
    assert 'source = "lxc/incus"' in providers_tf

    drop_in = os.path.join(project.path, ".debops", "conf.d",
                           "view-" + project.view + "-tofu.toml")
    assert "providers = ['lxc/incus']" in open(drop_in).read()


def test_provider_options_replace_the_configuration(tofu_project,
                                                    stub_tofu_subprocess):
    """The '--provider' options of the command line replace the
    configured default provider set for one invocation."""
    project = tofu_project(project_type="modern",
                           raw={"tofu": {"mkview": {"default_providers":
                                         ["lxc/incus"],
                                         "default_modules": {}}}})
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    mkview(project, providers=["hashicorp/tfcoremock"])

    providers_tf = open(os.path.join(view_dir, "providers.tf")).read()
    assert 'source = "hashicorp/tfcoremock"' in providers_tf
    assert "lxc/incus" not in providers_tf

    drop_in = os.path.join(project.path, ".debops", "conf.d",
                           "view-" + project.view + "-tofu.toml")
    assert "providers = ['hashicorp/tfcoremock']" in open(drop_in).read()


def test_providerless_view_writes_no_providers_file(tofu_project,
                                                    stub_tofu_subprocess):
    """An empty provider set writes no 'providers.tf' file: the view
    is providerless by default."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    mkview(project)

    assert not os.path.exists(os.path.join(view_dir, "providers.tf"))


def test_existing_view_follows_the_recorded_set(tofu_project,
                                                stub_tofu_subprocess):
    """An existing view's generated 'providers.tf' follows the
    'views.<view>.tofu.providers' option of its configuration
    drop-in, reconciled by the 'update' operation."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    drop_in = os.path.join(project.path, ".debops", "conf.d",
                           "view-" + project.view + "-tofu.toml")
    shutil.rmtree(view_dir)

    # A view created without providers has no generated file
    mkview(project)
    assert not os.path.exists(os.path.join(view_dir, "providers.tf"))

    # The user edits the drop-in to record the provider set; the
    # reconcile creates the generated file from it
    with open(drop_in, "w") as handle:
        handle.write('[views."{}"].tofu\nproviders = [\'lxc/incus\']\n'
                     .format(project.view))
    project.config.merge({'views': {project.view: {'tofu': {
        'providers': ['lxc/incus']}}}})
    changes = reconcile_view(project, project.view)
    assert [change['action'] for change in changes] == ['create']

    providers_tf = open(os.path.join(view_dir, "providers.tf")).read()
    assert 'source = "lxc/incus"' in providers_tf

    # The same set keeps the file as it is
    before = os.path.getmtime(os.path.join(view_dir, "providers.tf"))
    changes = reconcile_view(project, project.view)
    assert changes == []
    assert os.path.getmtime(os.path.join(view_dir, "providers.tf")) == before


def test_existing_view_drops_the_file_with_an_empty_set(
        tofu_project, stub_tofu_subprocess):
    """An empty recorded set removes the generated 'providers.tf' of
    an existing view."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    drop_in = os.path.join(project.path, ".debops", "conf.d",
                           "view-" + project.view + "-tofu.toml")
    shutil.rmtree(view_dir)

    mkview(project, providers=["lxc/incus"])
    assert os.path.exists(os.path.join(view_dir, "providers.tf"))

    # The user edits the drop-in to record an empty set; the
    # reconcile removes the generated file
    with open(drop_in, "w") as handle:
        handle.write('[views."{}"].tofu\nproviders = []\n'
                     .format(project.view))
    # A fresh process reads the edited drop-in as the whole recorded
    # set: the live tree clears the old value the same way
    project.config.raw['views'][project.view]['tofu']['providers'] \
        = []
    changes = reconcile_view(project, project.view)
    assert [change['action'] for change in changes] == ['remove']
    assert not os.path.exists(os.path.join(view_dir, "providers.tf"))


def test_hand_made_view_keeps_its_own_providers(tofu_project):
    """A view without a configuration drop-in -- a hand-made one --
    keeps its own provider requirements: the reconcile leaves the view
    alone."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    main_tf = os.path.join(view_dir, "main.tf")
    with open(main_tf) as handle:
        template_view = handle.read()
    with open(main_tf, "w") as handle:
        handle.write(template_view + "\n# The view's own providers\n")

    changes = reconcile_view(project, project.view)

    assert changes == []
    assert not os.path.exists(os.path.join(view_dir, "providers.tf"))
    assert "The view's own providers" in open(main_tf).read()


def test_provider_version_pin_is_written(tofu_project,
                                         stub_tofu_subprocess):
    """A '--provider' argument with a version pin carries the pin
    into the generated provider block."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    mkview(project, providers=["lxc/incus=1.2.1"])

    providers_tf = open(os.path.join(view_dir, "providers.tf")).read()
    assert 'source  = "lxc/incus"' in providers_tf
    assert 'version = "1.2.1"' in providers_tf


def test_state_passphrase_is_generated_into_the_store(
        tofu_project, stub_tofu_subprocess):
    """The store's 'environment' file carries the state passphrase
    which the runner composes into the environment; the passphrase is
    drawn from the URL-safe alphabet and the file documents itself."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    mkview(project)
    env_content = open(os.path.join(view_dir, "secret",
                                    "environment")).read()

    assert "The OpenTofu environment of the 'system' view" in env_content
    passphrase_line = [line for line in env_content.splitlines()
                       if line.startswith("TF_VAR_state_passphrase=")][0]
    passphrase = passphrase_line.split("=", 1)[1]
    assert len(passphrase) == 32
    assert all(char.isalnum() or char in "-_" for char in passphrase)
    # The store's environment composes into the subprocess environment
    # at execution time, after the store is unlocked
    env = TofuRunner(project, ["plan"])._extra_env()
    assert env["TF_VAR_state_passphrase"] == passphrase


def test_broken_tree_keeps_the_recorded_set(tofu_project):
    """A view whose tree is broken keeps its recorded provider set:
    the creation does not get to rewrite the user's decision."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    mkview(project, providers=["lxc/incus"])
    os.remove(os.path.join(view_dir, "main.tf"))

    mkview(project, providers=["hashicorp/tfcoremock"])

    providers_tf = open(os.path.join(view_dir, "providers.tf")).read()
    assert 'source = "lxc/incus"' in providers_tf
    assert 'tfcoremock' not in providers_tf


def test_drop_in_is_written_once(tofu_project, stub_tofu_subprocess):
    """The configuration drop-in is written when the view is created
    and never modified by the commands again: the user owns it."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    drop_in = os.path.join(project.path, ".debops", "conf.d",
                           "view-" + project.view + "-tofu.toml")
    shutil.rmtree(view_dir)

    mkview(project, providers=["lxc/incus"])
    content = open(drop_in).read()
    assert "providers = ['lxc/incus']" in content

    # A second command leaves the drop-in alone
    TofuRunner(project, ["plan"]).execute()
    assert open(drop_in).read() == content


def test_reconcile_refuses_a_user_owned_file(tofu_project):
    """A 'providers.tf' file without the DebOps marker is user-owned:
    the reconcile refuses to touch it unless '--force' is given."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    providers_path = os.path.join(view_dir, "providers.tf")
    with open(providers_path, "w") as handle:
        handle.write("# The user's own providers\n")
    write_drop_in(project, ['lxc/incus'])

    with pytest.raises(ValueError, match='was not generated by DebOps'):
        reconcile_view(project, project.view)
    assert open(providers_path).read() == "# The user's own providers\n"


def test_reconcile_force_replaces_a_user_owned_file(tofu_project):
    """'--force' hands the management of a user-owned 'providers.tf'
    back to DebOps."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    providers_path = os.path.join(view_dir, "providers.tf")
    with open(providers_path, "w") as handle:
        handle.write("# The user's own providers\n")
    write_drop_in(project, ['lxc/incus'])

    changes = reconcile_view(project, project.view, force=True)

    assert [change['action'] for change in changes] == ['update']
    assert 'source = "lxc/incus"' in open(providers_path).read()


def test_reconcile_leaves_a_user_owned_file_with_an_empty_set(
        tofu_project):
    """An empty recorded set removes only the generated file: a
    user-owned 'providers.tf' stays."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    providers_path = os.path.join(view_dir, "providers.tf")
    with open(providers_path, "w") as handle:
        handle.write("# The user's own providers\n")
    write_drop_in(project, [])

    changes = reconcile_view(project, project.view)

    assert changes == []
    assert open(providers_path).read() == "# The user's own providers\n"


def test_reconcile_dry_run_writes_nothing(tofu_project):
    """The dry-run reconcile shows the proposed changes without
    writing them."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    providers_path = os.path.join(view_dir, "providers.tf")
    write_drop_in(project, ['lxc/incus'])

    changes = reconcile_view(project, project.view, dry_run=True)

    assert [change['action'] for change in changes] == ['create']
    assert not os.path.exists(providers_path)

    # Without the dry-run flag the same reconcile writes the file
    changes = reconcile_view(project, project.view)
    assert [change['action'] for change in changes] == ['create']
    assert 'source = "lxc/incus"' in open(providers_path).read()


def test_reconcile_diff_carries_the_unified_diff(tofu_project):
    """The proposed changes carry the unified diff of each file."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    providers_path = os.path.join(view_dir, "providers.tf")
    write_drop_in(project, ['lxc/incus'])

    changes = reconcile_view(project, project.view, dry_run=True)

    diff = changes[0]['diff']
    assert diff.startswith('--- a/')
    assert 'tofu/views/' + project.view + '/providers.tf' in diff
    assert '+++ b/' in diff
    # A new file renders as a full-addition diff
    assert all(line.startswith('+') for line in diff.splitlines()
               if line.startswith(('+', '-')) and not line.startswith(
                   ('+++', '---')))


def test_modules_come_from_the_configuration(tofu_project,
                                             stub_tofu_subprocess):
    """The 'tofu.default_modules' option is the default module set of
    new views, recorded in the view's configuration drop-in."""
    project = tofu_project(project_type="modern",
                           raw={"tofu": {"mkview": {
                               "default_providers": [],
                               "default_modules": {
                                   "consul": {
                                       "source": "hashicorp/consul/aws"}}}}})
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    mkview(project)

    modules_tf = open(os.path.join(view_dir, "modules.tf")).read()
    assert 'module "consul" {' in modules_tf
    assert 'source = "hashicorp/consul/aws"' in modules_tf

    drop_in = os.path.join(project.path, ".debops", "conf.d",
                           "view-" + project.view + "-tofu.toml")
    content = open(drop_in).read()
    assert 'tofu.modules."consul"' in content
    assert "source = 'hashicorp/consul/aws'" in content


def test_module_options_replace_the_configuration(tofu_project,
                                                  stub_tofu_subprocess):
    """The '--module' options of the command line replace the
    configured default module set for one invocation."""
    project = tofu_project(project_type="modern",
                           raw={"tofu": {"mkview": {
                               "default_providers": [],
                               "default_modules": {
                                   "consul": {
                                       "source": "hashicorp/consul/aws"}}}}})
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    mkview(project, modules=["terraform-aws-modules/vpc/aws=5.16.0"])

    modules_tf = open(os.path.join(view_dir, "modules.tf")).read()
    assert 'module "vpc" {' in modules_tf
    assert 'source  = "terraform-aws-modules/vpc/aws"' in modules_tf
    assert 'version = "5.16.0"' in modules_tf
    assert 'consul' not in modules_tf

    drop_in = os.path.join(project.path, ".debops", "conf.d",
                           "view-" + project.view + "-tofu.toml")
    content = open(drop_in).read()
    assert 'tofu.modules."vpc"' in content
    assert 'consul' not in content


def test_moduleless_view_writes_no_modules_file(tofu_project,
                                                stub_tofu_subprocess):
    """An empty module set writes no 'modules.tf' file: the view is
    moduleless by default."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    mkview(project)

    assert not os.path.exists(os.path.join(view_dir, "modules.tf"))


def test_module_version_pin_is_written(tofu_project,
                                       stub_tofu_subprocess):
    """A '--module' argument with a version pin carries the pin into
    the generated module block."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    mkview(project, modules=["hashicorp/consul/aws=5.0.0"])

    modules_tf = open(os.path.join(view_dir, "modules.tf")).read()
    assert 'source  = "hashicorp/consul/aws"' in modules_tf
    assert 'version = "5.0.0"' in modules_tf


def test_module_schemes_are_refused(tofu_project):
    """The scheme-prefixed and local-path module sources carry no
    registry package name: the '--module' options refuse them with
    the way out instead of deriving a broken local name. Such modules
    are instantiated in the view configuration drop-in directly."""
    for source in ('git::https://git.example.com/group/mod/system',
                   'oci://registry.example/group/mod:1.0.0',
                   './modules/vpc', '/abs/path/module', 'mod'):
        with pytest.raises(ValueError, match='registry address'):
            resolve_modules(tofu_project(project_type="modern"),
                            modules=[source])


def test_module_local_name_is_derived_from_the_source(
        tofu_project, stub_tofu_subprocess):
    """The '--module' arguments derive the local module name from the
    source address: the package name of the registry path."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    mkview(project, modules=["hashicorp/consul/aws",
                             "git.example.com/ns/name//subdir"])

    modules_tf = open(os.path.join(view_dir, "modules.tf")).read()
    assert 'module "consul" {' in modules_tf
    assert 'module "name" {' in modules_tf
    assert 'source = "git.example.com/ns/name//subdir"' in modules_tf


def test_module_collision_is_refused(tofu_project):
    """Two '--module' arguments which derive the same local name are a
    mistake: OpenTofu refuses the same collision."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    with pytest.raises(ValueError, match='more than one module source'):
        mkview(project, modules=["hashicorp/consul/aws",
                                 "hashicorp/consul/other"])


def test_module_inputs_render_from_the_recorded_table(
        tofu_project, stub_tofu_subprocess):
    """The inputs of a recorded module render as the HCL attributes of
    the generated module block."""
    project = tofu_project(project_type="modern",
                           raw={"tofu": {"mkview": {
                               "default_providers": [],
                               "default_modules": {
                                   "consul": {
                                       "source": "hashicorp/consul/aws",
                                       "version": "5.0.0",
                                       "inputs": {
                                           "datacenter": "dc1",
                                           "server_count": 3,
                                           "replicas": True,
                                           "cidrs": ["10.0.1.0/24",
                                                     "10.0.2.0/24"],
                                           "net": {"host": "x",
                                                   "port": 8300}}}}}}})
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    mkview(project)

    modules_tf = open(os.path.join(view_dir, "modules.tf")).read()
    assert 'datacenter   = "dc1"' in modules_tf
    assert 'server_count = 3' in modules_tf
    assert 'replicas     = true' in modules_tf
    assert 'cidrs        = ["10.0.1.0/24", "10.0.2.0/24"]' in modules_tf
    assert 'net          = { host = "x", port = 8300 }' in modules_tf


def test_module_inputs_render_raw_hcl_expressions(
        tofu_project, stub_tofu_subprocess):
    """A string input which carries the 'hcl:' prefix carries a raw
    HCL expression which the generated block emits verbatim; the
    prefix is consumed once, and a doubled prefix is an escaped
    literal."""
    project = tofu_project(project_type="modern",
                           raw={"tofu": {"mkview": {
                               "default_providers": [],
                               "default_modules": {
                                   "consul": {
                                       "source": "hashicorp/consul/aws",
                                       "inputs": {
                                           "image": "hcl:var.image_name",
                                           "cidrs": "hcl:module.network.cidrs",
                                           "count": "hcl:var.autoscaling "
                                                    '? var.max_count '
                                                    ": var.min_count",
                                           "nothing": "hcl:null",
                                           "escaped": "hcl:hcl:hello",
                                           "text": "hcl:hello"}}}}}})
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    mkview(project)

    modules_tf = open(os.path.join(view_dir, "modules.tf")).read()
    assert 'image   = var.image_name' in modules_tf
    assert 'cidrs   = module.network.cidrs' in modules_tf
    assert ('count   = var.autoscaling ? var.max_count : '
            'var.min_count' in modules_tf)
    assert 'nothing = null' in modules_tf
    assert 'escaped = "hcl:hello"' in modules_tf
    assert 'text    = hello' in modules_tf


def test_modules_follow_the_recorded_set(tofu_project,
                                         stub_tofu_subprocess):
    """An existing view's generated 'modules.tf' follows the
    'views.<view>.tofu.modules' option of its configuration drop-in,
    reconciled by the 'update' operation."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    drop_in = os.path.join(project.path, ".debops", "conf.d",
                           "view-" + project.view + "-tofu.toml")
    shutil.rmtree(view_dir)

    # A view created without modules has no generated file
    mkview(project)
    assert not os.path.exists(os.path.join(view_dir, "modules.tf"))

    # The user edits the drop-in to record the module set; the
    # reconcile creates the generated file from it
    with open(drop_in, "w") as handle:
        handle.write('[views."{}"].tofu\nproviders = []\n'
                     '\n[views."{}".tofu.modules."consul"]\n'
                     "source = 'hashicorp/consul/aws'\n"
                     .format(project.view, project.view))
    project.config.merge({'views': {project.view: {'tofu': {
        'providers': [],
        'modules': {'consul': {'source': 'hashicorp/consul/aws'}}}}}})
    changes = reconcile_view(project, project.view)
    assert [change['action'] for change in changes] == ['create']

    modules_tf = open(os.path.join(view_dir, "modules.tf")).read()
    assert 'module "consul" {' in modules_tf

    # The same set keeps the file as it is
    before = os.path.getmtime(os.path.join(view_dir, "modules.tf"))
    changes = reconcile_view(project, project.view)
    assert changes == []
    assert os.path.getmtime(os.path.join(view_dir, "modules.tf")) == before

    # An empty recorded set removes the generated file
    with open(drop_in, "w") as handle:
        handle.write('[views."{}"].tofu\nproviders = []\n'
                     .format(project.view))
    try:
        del project.config.raw['views'][project.view]['tofu']['modules']
    except KeyError:
        pass
    project.config.merge({'views': {project.view: {'tofu': {
        'providers': [],
        'modules': {}}}}})
    changes = reconcile_view(project, project.view)
    assert [change['action'] for change in changes] == ['remove']
    assert not os.path.exists(os.path.join(view_dir, "modules.tf"))


def test_reconcile_refuses_a_user_owned_modules_file(tofu_project):
    """A 'modules.tf' file without the DebOps marker is user-owned:
    the reconcile refuses to touch it unless '--force' is given."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    modules_path = os.path.join(view_dir, "modules.tf")
    with open(modules_path, "w") as handle:
        handle.write("# The user's own modules\n")
    write_drop_in(project, [])
    project.config.merge({'views': {project.view: {'tofu': {
        'modules': {'consul': {'source': 'hashicorp/consul/aws'}}}}}})

    with pytest.raises(ValueError, match='was not generated by DebOps'):
        reconcile_view(project, project.view)
    assert open(modules_path).read() == "# The user's own modules\n"


def test_reconcile_force_replaces_a_user_owned_modules_file(
        tofu_project):
    """'--force' hands the management of a user-owned 'modules.tf'
    back to DebOps."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    modules_path = os.path.join(view_dir, "modules.tf")
    with open(modules_path, "w") as handle:
        handle.write("# The user's own modules\n")
    write_drop_in(project, [])
    project.config.merge({'views': {project.view: {'tofu': {
        'modules': {'consul': {'source': 'hashicorp/consul/aws'}}}}}})

    changes = reconcile_view(project, project.view, force=True)

    assert [change['action'] for change in changes] == ['update']
    assert 'module "consul" {' in open(modules_path).read()


def test_generated_modules_file_is_fmt_clean(tofu_project,
                                             stub_tofu_subprocess):
    """The generated 'modules.tf' is fmt-clean: running 'tofu fmt' in
    the view does not churn the generated file."""
    project = tofu_project(project_type="modern",
                           raw={"tofu": {"mkview": {
                               "default_providers": [],
                               "default_modules": {
                                   "consul": {
                                       "source": "hashicorp/consul/aws",
                                       "version": "5.0.0",
                                       "inputs": {
                                           "datacenter": "dc1",
                                           "server_count": 3,
                                           "image": "hcl:var.image_name"}}}}}})
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    mkview(project)

    modules_tf = open(os.path.join(view_dir, "modules.tf")).read()
    assert 'source  = "hashicorp/consul/aws"' in modules_tf
    assert 'version = "5.0.0"' in modules_tf
    assert 'datacenter   = "dc1"' in modules_tf
    assert 'server_count = 3' in modules_tf
    assert 'image        = var.image_name' in modules_tf


def test_drop_in_records_the_seeded_binary_version(tofu_project,
                                                   stub_tofu_subprocess):
    """A created view's drop-in records the known-good version of the
    'tofu.upstream.known_version' configuration."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    mkview(project)

    drop_in = os.path.join(project.path, ".debops", "conf.d",
                           "view-" + project.view + "-tofu.toml")
    content = open(drop_in).read()
    known = project.config.raw["tofu"]["upstream"]["known_version"]
    assert "binary_version = '{}'".format(known) in content
    assert "modules = {}" in content
    assert known == project.config.raw[
        "views"][project.view]["tofu"]["binary_version"]


def test_rekey_rotates_the_passphrase(tofu_project,
                                      stub_tofu_subprocess):
    """The rekey inserts the fallback into the mkview-shaped
    stanza, re-encrypts through the refresh, verifies with a plan
    and removes the fallback: the environment carries only the new
    passphrase afterwards, the user's own keys survive, the
    old-key plan files are gone."""
    project = tofu_project(project_type="modern")
    os.remove(os.path.join(project.path, "tofu", "views",
                           project.view, "main.tf"))
    mkview(project)
    env_path = os.path.join(project.path, "tofu", "views",
                            project.view, "secret", "environment")
    with open(env_path) as handle:
        original = handle.read()
    with open(env_path, "a") as handle:
        handle.write("TF_VAR_probe_token=probe\n")
    state_dir = os.path.join(project.path, "tofu", "views",
                             project.view, "state")
    os.makedirs(state_dir)
    with open(os.path.join(state_dir, "terraform.tfstate"),
              "w") as handle:
        handle.write("{}")

    rekey_view(project, project.view)

    with open(env_path) as handle:
        env = handle.read()
    assert "TF_VAR_old_state_passphrase" not in env
    assert "TF_VAR_probe_token=probe" in env
    new_passphrase = [line.split("=", 1)[1] for line in
                      env.splitlines()
                      if line.startswith("TF_VAR_state_passphrase=")][0]
    old_passphrase = [line.split("=", 1)[1] for line in
                      original.splitlines()
                      if line.startswith("TF_VAR_state_passphrase=")][0]
    assert new_passphrase != old_passphrase
    with open(os.path.join(project.path, "tofu", "views",
                           project.view, "main.tf")) as handle:
        main_tf = handle.read()
    assert "old_state_passphrase" not in main_tf
    # the new primary carries the next generation label
    assert 'key_provider "pbkdf2" "state-2"' in main_tf
    plans_dir = os.path.join(project.path, "tofu", "views",
                             project.view, "plans")
    assert not os.path.isdir(plans_dir) or not os.listdir(plans_dir)


def test_rekey_resumes_by_the_markers(tofu_project,
                                      stub_tofu_subprocess):
    """An interrupted rotation resumes: the re-run reads the old
    passphrase from the environment marker and does not regenerate
    the new one -- the re-encrypted state stays readable."""
    project = tofu_project(project_type="modern")
    os.remove(os.path.join(project.path, "tofu", "views",
                           project.view, "main.tf"))
    mkview(project)
    env_path = os.path.join(project.path, "tofu", "views",
                            project.view, "secret", "environment")
    with open(env_path) as handle:
        original = handle.read()
    interrupted_passphrase = "interrupted-new-passphrase"
    old_passphrase = [line.split("=", 1)[1] for line in
                      original.splitlines()
                      if line.startswith("TF_VAR_state_passphrase=")][0]

    rekey_view(project, project.view)
    # Simulate the interruption of a second rotation: the markers of
    # the interrupted rotation are in place -- the new passphrase in
    # the environment, the old one beside it as the fallback's
    # variable
    with open(env_path, "w") as handle:
        handle.write("TF_VAR_state_passphrase="
                     + interrupted_passphrase + "\n"
                     + "TF_VAR_old_state_passphrase="
                     + old_passphrase + "\n")

    rekey_view(project, project.view)

    with open(env_path) as handle:
        env = handle.read()
    # The passphrase was NOT regenerated: the interrupted rotation's
    # value is the one the state carries
    assert ("TF_VAR_state_passphrase="
            + interrupted_passphrase) in env
    assert "TF_VAR_old_state_passphrase" not in env


def test_rekey_reinserts_the_fallback_when_the_verification_fails(
        tofu_project, stub_tofu_subprocess):
    """The verification plan which fails re-inserts the fallback:
    the state stays readable through the old passphrase while the
    operator investigates."""
    project = tofu_project(project_type="modern")
    os.remove(os.path.join(project.path, "tofu", "views",
                           project.view, "main.tf"))
    mkview(project)
    state_dir = os.path.join(project.path, "tofu", "views",
                             project.view, "state")
    os.makedirs(state_dir)
    with open(os.path.join(state_dir, "terraform.tfstate"),
              "w") as handle:
        handle.write("{}")
    process_ok = mock.Mock()
    process_ok.returncode = 0
    process_ok.stdout = io.BytesIO(b"")
    process_ok.stderr = io.BytesIO(b"")
    process_fail = mock.Mock()
    process_fail.returncode = 1
    process_fail.stdout = io.BytesIO(b"")
    process_fail.stderr = io.BytesIO(b"")
    stub_tofu_subprocess.side_effect = [process_ok, process_fail]

    with pytest.raises(ChildProcessError, match="verification"):
        rekey_view(project, project.view)

    with open(os.path.join(project.path, "tofu", "views",
                           project.view, "main.tf")) as handle:
        main_tf = handle.read()
    assert "fallback" in main_tf
    assert "old_state_passphrase" in main_tf


def test_rekey_refuses_the_missing_encryption_block(tofu_project):
    """The view configuration without the encryption block refuses:
    the rekey rotates what the template renders, and the encryption
    block is rewritten per phase."""
    project = tofu_project(project_type="modern")
    os.remove(os.path.join(project.path, "tofu", "views",
                           project.view, "main.tf"))
    mkview(project)
    main_tf_path = os.path.join(project.path, "tofu", "views",
                                project.view, "main.tf")
    with open(main_tf_path) as handle:
        main_tf = handle.read()
    main_tf = main_tf.replace("  encryption {", "  rekey_removed {")
    with open(main_tf_path, "w") as handle:
        handle.write(main_tf)

    with pytest.raises(ValueError, match="no encryption block"):
        rekey_view(project, project.view)


def test_rekey_refuses_views_with_named_workspaces(tofu_project):
    """A view with named workspaces refuses the rotation: the
    workspaces share one encryption block, and the cleanup would
    leave the other workspaces' states keyless."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    os.remove(os.path.join(view_dir, "main.tf"))
    mkview(project)
    workspaces_dir = os.path.join(view_dir, "state", "terraform.tfstate.d",
                                  "deploy")
    os.makedirs(workspaces_dir)

    with pytest.raises(ValueError, match="named workspaces.*deploy"):
        rekey_view(project, project.view)


def test_rekey_resume_keeps_the_rotation_labels(tofu_project,
                                                stub_tofu_subprocess):
    """A rotation interrupted by a failed refresh resumes with the
    labels the interrupted rotation already wrote: the re-run's
    refresh re-encrypts under the same primary, and the cleanup does
    not derive a new generation -- deriving one would leave the
    state envelope referencing a label the configuration no longer
    carries."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    os.remove(os.path.join(view_dir, "main.tf"))
    mkview(project)
    state_dir = os.path.join(view_dir, "state")
    os.makedirs(state_dir)
    with open(os.path.join(state_dir, "terraform.tfstate"),
              "w") as handle:
        handle.write("{}")
    process_fail = mock.Mock()
    process_fail.returncode = 1
    process_fail.stdout = io.BytesIO(b"")
    process_fail.stderr = io.BytesIO(b"")
    stub_tofu_subprocess.side_effect = [process_fail]

    with pytest.raises(TofuOperationFailed):
        rekey_view(project, project.view)

    main_tf = open(os.path.join(view_dir, "main.tf")).read()
    assert "state-2" in main_tf

    process_ok = mock.Mock()
    process_ok.returncode = 0
    process_ok.stdout = io.BytesIO(b"")
    process_ok.stderr = io.BytesIO(b"")
    stub_tofu_subprocess.side_effect = None
    stub_tofu_subprocess.return_value = process_ok

    rekey_view(project, project.view)

    main_tf = open(os.path.join(view_dir, "main.tf")).read()
    assert "state-3" not in main_tf
    assert "fallback" not in main_tf
    assert "state-2" in main_tf
