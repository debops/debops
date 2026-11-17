# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import fcntl
import logging
import os
import shutil
import subprocess
import sys
from unittest import mock

import pytest

import debops.core.runner as runner_base_module
import debops.core.tofu.runner as runner_module
from debops.core.tofu.runner import TofuRunner
from debops.core.tofu.view import reconcile_view
from debops.core.secrets import SecretManager


@pytest.fixture(autouse=True)
def stub_project_secrets(monkeypatch):
    """A real SecretManager over a stub store.

    The manager's list-shaped unlock and lock results stay live in
    these tests, so a change of the manager's return shape fails here
    instead of hiding behind a mock configured with the shape of an
    older interface; only the store mechanics are stubbed. The store
    mock is handed to the tests which configure or inspect it.
    """
    store = mock.Mock()
    store.unlock.return_value = False
    store.lock.return_value = False

    class StubStores(SecretManager):
        def _factories(self):
            return {"tofu": lambda project, view: store}

    monkeypatch.setattr(runner_base_module, "SecretManager", StubStores)
    return store


@pytest.fixture
def tofu_project(stub_project):
    """A stub project whose configuration carries the tofu section,
    with the view's tofu directory in place."""
    def _make(**kwargs):
        raw = {"binaries": {"tofu": "tofu"},
               "tofu": {"state_path": "secret/terraform.tfstate",
                        "operations": [], "plan_retention": 3,
                        "default_providers": [],
                        "default_modules": {}}}
        if "raw" in kwargs:
            for key, value in kwargs.pop("raw").items():
                if key in raw and isinstance(raw[key], dict):
                    raw[key].update(value)
                else:
                    raw[key] = value
        project = stub_project(raw=raw, **kwargs)
        if project.project_type == "legacy":
            view_dir = os.path.join(project.path, "tofu")
        else:
            view_dir = os.path.join(project.path, "tofu", "views",
                                    project.view)
        os.makedirs(os.path.join(view_dir, "secret"), exist_ok=True)
        # A view whose template is applied: the runner finds it in
        # place and does not re-create it
        with open(os.path.join(view_dir, "main.tf"), "w") as handle:
            handle.write("terraform { backend \"local\" {} }\n")
        return project
    return _make


@pytest.fixture
def stub_tofu_subprocess(monkeypatch):
    """A stubbed tofu subprocess: 'execute()' runs to completion
    without the tofu binary, the hooks pass."""
    process = mock.Mock()
    process.returncode = 0
    process.communicate.return_value = (b"", b"")
    popen = mock.Mock(return_value=process)
    monkeypatch.setattr(runner_module.subprocess, "Popen", popen)
    monkeypatch.setattr(runner_module, "run_hooks",
                        mock.Mock(return_value=True))
    return popen


def test_command_starts_with_the_tofu_binary(tofu_project):
    runner = TofuRunner(tofu_project(), ["plan"])
    assert runner._tofu_command[0] == "tofu"
    assert runner._tofu_command[1] == "plan"


def test_operation_with_a_value_is_kept_in_order(tofu_project):
    runner = TofuRunner(tofu_project(), ["plan", "-var", "foo=bar"])
    assert runner._tofu_command[1:4] == ["plan", "-var", "foo=bar"]


def test_option_with_inline_value_is_self_contained(tofu_project):
    runner = TofuRunner(tofu_project(), ["plan", "-var=foo=bar"])
    assert runner._tofu_command[1:3] == ["plan", "-var=foo=bar"]


def test_runner_options_come_last_and_win(tofu_project):
    """The '-input=false' of the wrapper is appended after the
    operator's arguments, where a repeated flag wins."""
    runner = TofuRunner(tofu_project(),
                        ["plan", "-input=true", "-var", "a=b"])
    assert runner._tofu_command[-3:] == ["-var", "a=b", "-input=false"]


def test_operations_which_accept_no_input_option_run_without_it(
        tofu_project):
    runner = TofuRunner(tofu_project(), ["state", "list"])
    assert "-input=false" not in runner._tofu_command


def test_no_color_is_added_for_the_machine_streams(tofu_project):
    runner = TofuRunner(tofu_project(), ["plan"], no_color=True)
    assert "-no-color" in runner._tofu_command


def test_no_color_is_skipped_for_the_state_operations(tofu_project):
    runner = TofuRunner(tofu_project(), ["state", "list"], no_color=True)
    assert "-no-color" not in runner._tofu_command


def test_workspace_comes_from_the_command_line(tofu_project):
    project = tofu_project()
    runner = TofuRunner(project, ["plan"], workspace="feature")
    assert runner._tofu_env["TF_WORKSPACE"] == "feature"


def test_workspace_comes_from_the_view_configuration(tofu_project):
    project = tofu_project(
        view="prod",
        raw={"binaries": {"tofu": "tofu"},
             "views": {"prod": {"tofu": {"workspace": "staging"}}}})
    runner = TofuRunner(project, ["plan"])
    assert runner._tofu_env["TF_WORKSPACE"] == "staging"


def test_workspace_defaults_to_the_default_workspace(tofu_project):
    runner = TofuRunner(tofu_project(), ["plan"])
    assert runner._tofu_env["TF_WORKSPACE"] == "default"


def test_data_directory_is_relocated_outside_the_project(tofu_project,
                                                         tmp_path):
    runner = TofuRunner(tofu_project(), ["plan"])
    assert runner._tofu_env["TF_DATA_DIR"].startswith(os.path.join(
        os.path.expanduser("~"), ".cache", "debops", "tofu"))
    assert not runner._tofu_env["TF_DATA_DIR"].startswith(str(tmp_path))


def test_plugin_cache_is_shared(tofu_project):
    runner = TofuRunner(tofu_project(), ["plan"])
    assert runner._tofu_env["TF_PLUGIN_CACHE_DIR"] == os.path.join(
        os.path.expanduser("~"), ".cache", "debops", "tofu", "plugins")


def test_project_cli_configuration_is_picked_up(tofu_project, tmp_path):
    project = tofu_project()
    cli_config = os.path.join(project.path, ".debops", "tofu", "cli.tfrc")
    os.makedirs(os.path.dirname(cli_config))
    with open(cli_config, "w") as handle:
        handle.write("{}")

    runner = TofuRunner(project, ["plan"])

    assert runner._tofu_env["TF_CLI_CONFIG_FILE"] == cli_config


def test_state_file_of_the_default_workspace_is_the_state_path(
        tofu_project):
    project = tofu_project(project_type="modern", view="prod")
    runner = TofuRunner(project, ["plan"])
    assert runner._state_file() == os.path.join(
        project.path, "tofu", "views", "prod", "secret",
        "terraform.tfstate")


def test_state_file_of_a_named_workspace_is_in_the_workspaces_directory(
        tofu_project):
    project = tofu_project(project_type="modern", view="prod")
    runner = TofuRunner(project, ["plan"], workspace="feature")
    assert runner._state_file() == os.path.join(
        project.path, "tofu", "views", "prod", "secret", "workspaces",
        "feature", "terraform.tfstate")


def test_legacy_project_runs_at_the_project_root(tofu_project):
    project = tofu_project(project_type="legacy", view="system")
    runner = TofuRunner(project, ["plan"])
    assert runner._view_root == os.path.join(project.path, "tofu")


def test_empty_state_path_disables_the_checks(tofu_project):
    project = tofu_project(
        raw={"binaries": {"tofu": "tofu"},
             "tofu": {"state_path": "", "operations": []}})
    runner = TofuRunner(project, ["plan"])
    assert not runner._state_checks_enabled()
    runner._check_state_presence()
    runner._check_state_lock()


def test_missing_state_of_an_initialized_view_warns(tofu_project, caplog):
    """A fresh view holds no state until its first operation, which
    looks the same as a lost store; the missing state warns instead of
    refusing, and the plan surfaces a full recreate."""
    project = tofu_project()
    runner = TofuRunner(project, ["apply"])
    with mock.patch.object(runner_module.TofuRunner,
                           "_initialized_before", return_value=True):
        with caplog.at_level(logging.WARNING):
            runner._check_state_presence()
    assert "is missing" in caplog.text


def test_fresh_view_without_state_is_allowed(tofu_project, caplog):
    """A view which was never applied has no state file yet; its
    first operation is the legitimate creation."""
    project = tofu_project()
    runner = TofuRunner(project, ["apply"])
    runner._check_state_presence()


def test_missing_workspace_is_refused(tofu_project, caplog):
    """OpenTofu silently auto-creates a workspace on selection and
    plans against empty state; the wrapper refuses and points at the
    explicit creation."""
    project = tofu_project()
    runner = TofuRunner(project, ["plan"], workspace="typo")
    with mock.patch.object(runner_module.TofuRunner,
                           "_initialized_before", return_value=True):
        with pytest.raises(ChildProcessError, match="workspace"):
            runner._check_state_presence()


def test_uninitialized_view_refuses_the_named_workspace(tofu_project):
    """Without an initialization the view has no backend to hold the
    workspace; the operations which touch state need 'tofu init'
    first."""
    project = tofu_project()
    runner = TofuRunner(project, ["plan"], workspace="feature")
    with pytest.raises(ChildProcessError, match="not initialized"):
        runner._check_state_presence()


def test_fresh_named_workspace_is_allowed(tofu_project, monkeypatch):
    """A workspace which was created explicitly holds no state yet;
    its first operation is the legitimate creation."""
    project = tofu_project()
    os.makedirs(os.path.join(project.path, "tofu", "terraform.tfstate.d",
                             "feature"))
    runner = TofuRunner(project, ["plan"], workspace="feature")
    with mock.patch.object(runner_module.TofuRunner,
                           "_initialized_before", return_value=True):
        with mock.patch.object(
                runner_module.TofuRunner, "_backend_metadata",
                return_value={"path": "secret/terraform.tfstate"}):
            runner._check_state_presence()


LOCK_HOLDER_SCRIPT = (
    "import fcntl, sys, time\n"
    "handle = open(sys.argv[1], 'r+')\n"
    "fcntl.lockf(handle, fcntl.LOCK_EX)\n"
    "print('locked', flush=True)\n"
    "time.sleep(30)\n")


def test_held_state_lock_is_refused(tofu_project):
    """A record lock held by another process refuses the operation;
    the pre-check mirrors the semantics of the tofu lock."""
    runner, state_file = make_locked_runner(None, tofu_project)

    holder = subprocess.Popen(
        [sys.executable, "-c", LOCK_HOLDER_SCRIPT, state_file],
        stdout=subprocess.PIPE)
    try:
        holder.stdout.readline()
        with pytest.raises(ChildProcessError, match="locked"):
            runner._check_state_lock()
    finally:
        holder.kill()
        holder.wait()


def test_freed_state_lock_allows_the_operation(tofu_project):
    """Without a lock holder the pre-check passes."""
    runner, state_file = make_locked_runner(None, tofu_project)
    runner._check_state_lock()


def make_locked_runner(tmp_path, tofu_project):
    """A runner whose view holds a state file, with the fcntl lock
    machinery live."""
    project = tofu_project()
    os.makedirs(os.path.join(project.path, "tofu", "secret"),
                exist_ok=True)
    state_file = os.path.join(project.path, "tofu", "secret",
                              "terraform.tfstate")
    with open(state_file, "w") as handle:
        handle.write("{}")
    return TofuRunner(project, ["plan"]), state_file


def test_operations_allow_list_refuses_an_unlisted_operation(
        tofu_project):
    project = tofu_project(
        raw={"binaries": {"tofu": "tofu"},
             "tofu": {"state_path": "secret/terraform.tfstate",
                      "operations": ["plan", "output"]}})
    runner = TofuRunner(project, ["destroy"])
    assert not runner._operation_allowed()

    runner = TofuRunner(project, ["plan"])
    assert runner._operation_allowed()


def test_operations_allow_list_empty_allows_everything(tofu_project):
    runner = TofuRunner(tofu_project(), ["destroy"])
    assert runner._operation_allowed()


def test_one_step_apply_without_approval_is_refused_when_not_a_tty(
        tofu_project, monkeypatch):
    monkeypatch.setattr("sys.stdin", mock.Mock(isatty=lambda: False))
    runner = TofuRunner(tofu_project(), ["apply"])
    with pytest.raises(ChildProcessError, match="approval"):
        runner._check_approval()


def test_plan_file_apply_needs_no_approval(tofu_project, monkeypatch):
    monkeypatch.setattr("sys.stdin", mock.Mock(isatty=lambda: False))
    runner = TofuRunner(tofu_project(),
                        ["apply", "secret/plan.tfplan"])
    runner._check_approval()
    assert "-auto-approve" not in runner._tofu_command


def test_var_value_is_not_taken_for_the_plan_file(tofu_project,
                                                  monkeypatch):
    """A glued flag value is not a positional: the one-step apply
    keeps its approval requirement."""
    monkeypatch.setattr("sys.stdin", mock.Mock(isatty=lambda: False))
    runner = TofuRunner(tofu_project(), ["apply", "-var", "foo=bar"])
    with pytest.raises(ChildProcessError, match="approval"):
        runner._check_approval()


def test_auto_approve_on_the_command_line_is_the_decision(
        tofu_project, monkeypatch):
    monkeypatch.setattr("sys.stdin", mock.Mock(isatty=lambda: False))
    runner = TofuRunner(tofu_project(), ["apply", "-auto-approve"])
    runner._check_approval()
    assert "-auto-approve" in runner._tofu_command


def test_confirmation_on_a_tty_appends_auto_approve(tofu_project,
                                                    monkeypatch):
    monkeypatch.setattr("sys.stdin", mock.Mock(isatty=lambda: True))
    with mock.patch("builtins.input", return_value="yes"):
        runner = TofuRunner(tofu_project(), ["destroy"])
        runner._check_approval()
    assert "-auto-approve" in runner._tofu_command


def test_declined_confirmation_aborts(tofu_project, monkeypatch):
    monkeypatch.setattr("sys.stdin", mock.Mock(isatty=lambda: True))
    with mock.patch("builtins.input", return_value="no"):
        runner = TofuRunner(tofu_project(), ["destroy"])
        with pytest.raises(SystemExit):
            runner._check_approval()
    assert "-auto-approve" not in runner._tofu_command


def test_execute_cycles_the_store_and_runs_the_operation(
        tofu_project, stub_project_secrets, monkeypatch):
    store = stub_project_secrets
    store.unlock.return_value = True
    popen = mock.Mock(returncode=3)
    process = mock.Mock()
    process.returncode = 3
    process.communicate.return_value = (b"", b"")
    popen.return_value = process
    monkeypatch.setattr(runner_module.subprocess, "Popen", popen)
    monkeypatch.setattr(runner_module, "run_hooks",
                        mock.Mock(return_value=True))

    runner = TofuRunner(tofu_project(), ["plan"])
    rc = runner.execute()

    assert rc == 3
    assert store.unlock.called
    assert store.lock.called
    assert popen.call_args.kwargs["cwd"] == runner._view_root
    env = popen.call_args.kwargs["env"]
    assert env["TF_WORKSPACE"] == "default"
    assert env["TF_DATA_DIR"] == runner._tofu_env["TF_DATA_DIR"]


def test_execute_composes_the_store_environment(tofu_project,
                                                stub_project_secrets,
                                                monkeypatch):
    """The variables of the store's environment file reach the tofu
    subprocess, with the rotated store values winning."""
    project = tofu_project()
    os.makedirs(os.path.join(project.path, "tofu", "secret"),
                exist_ok=True)
    with open(os.path.join(project.path, "tofu", "secret", ".env"),
              "w") as handle:
        handle.write("TF_VAR_state_passphrase=from-the-store\n")

    process = mock.Mock()
    process.returncode = 0
    process.communicate.return_value = (b"", b"")
    popen = mock.Mock(return_value=process)
    monkeypatch.setattr(runner_module.subprocess, "Popen", popen)
    monkeypatch.setattr(runner_module, "run_hooks",
                        mock.Mock(return_value=True))

    runner = TofuRunner(project, ["plan"])
    runner.execute()

    env = popen.call_args.kwargs["env"]
    assert env["TF_VAR_state_passphrase"] == "from-the-store"


def test_execute_runs_the_hooks_around_the_operation(
        tofu_project, stub_project_secrets):
    """The hooks of the operation run around the tofu subprocess,
    with the project environment composed for them."""
    project = tofu_project(raw={"binaries": {"tofu": "/bin/true"}})
    script = os.path.join(project.path, ".debops", "hooks", "pre-plan",
                          "00-pre")
    os.makedirs(os.path.dirname(script))
    with open(script, "w") as handle:
        handle.write("#!/bin/sh\ntouch pre-plan-ran\n")
    os.chmod(script, 0o755)
    # The stub project carries the markers the hook runner requires
    os.makedirs(os.path.join(project.path, ".debops", "conf.d"),
                exist_ok=True)

    runner = TofuRunner(project, ["plan"])
    runner.execute()

    assert os.path.exists(os.path.join(project.path, "pre-plan-ran"))


def test_failed_hook_aborts_the_operation(tofu_project,
                                          stub_project_secrets):
    project = tofu_project(raw={"binaries": {"tofu": "/bin/true"}})
    script = os.path.join(project.path, ".debops", "hooks", "pre-plan",
                          "00-pre")
    os.makedirs(os.path.dirname(script))
    with open(script, "w") as handle:
        handle.write("#!/bin/sh\nexit 1\n")
    os.chmod(script, 0o755)
    # The stub project carries the markers the hook runner requires
    os.makedirs(os.path.join(project.path, ".debops", "conf.d"),
                exist_ok=True)

    runner = TofuRunner(project, ["plan"])
    with pytest.raises(ChildProcessError, match="aborted"):
        runner.execute()


def test_missing_view_tree_is_created_lazily(tofu_project,
                                             stub_tofu_subprocess):
    """The first command in a project without the view tree applies
    the template and proceeds."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    runner = TofuRunner(project, ["plan"])
    runner.execute()

    assert os.path.isfile(os.path.join(view_dir, "main.tf"))
    assert os.path.isfile(os.path.join(view_dir, "secret", ".env"))
    # The operation runs against the created view
    assert runner._view_root == view_dir


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

    TofuRunner(project, ["plan"]).execute()

    assert os.path.isfile(os.path.join(view_dir, "main.tf"))
    assert open(custom).read() == "# The user's own file\n"


def test_providers_come_from_the_configuration(tofu_project,
                                               stub_tofu_subprocess):
    """The 'tofu.default_providers' option is the default provider
    set of new views, recorded in the view's configuration drop-in."""
    project = tofu_project(project_type="modern",
                           raw={"tofu": {"default_providers":
                                         ["lxc/incus"]}})
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    TofuRunner(project, ["plan"]).execute()

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
                           raw={"tofu": {"default_providers":
                                         ["lxc/incus"]}})
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    TofuRunner(project, ["plan"], providers=["hashicorp/tfcoremock"]
               ).execute()

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

    TofuRunner(project, ["plan"]).execute()

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
    TofuRunner(project, ["plan"]).execute()
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

    TofuRunner(project, ["plan"], providers=["lxc/incus"]).execute()
    assert os.path.exists(os.path.join(view_dir, "providers.tf"))

    # The user edits the drop-in to record an empty set; the
    # reconcile removes the generated file
    with open(drop_in, "w") as handle:
        handle.write('[views."{}"].tofu\nproviders = []\n'
                     .format(project.view))
    project.config.merge({'views': {project.view: {'tofu': {
        'providers': []}}}})
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

    TofuRunner(project, ["plan"], providers=["lxc/incus=1.2.1"]
               ).execute()

    providers_tf = open(os.path.join(view_dir, "providers.tf")).read()
    assert 'source  = "lxc/incus"' in providers_tf
    assert 'version = "1.2.1"' in providers_tf


def test_state_passphrase_is_generated_into_the_store(
        tofu_project, stub_tofu_subprocess):
    """The store's '.env' carries the state passphrase which the
    runner composes into the environment."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    runner = TofuRunner(project, ["plan"])
    runner.execute()
    dotenv_content = open(os.path.join(view_dir, "secret", ".env")).read()

    assert dotenv_content.startswith("TF_VAR_state_passphrase=")
    passphrase = dotenv_content.split("=", 1)[1].rstrip("\n")
    assert len(passphrase) == 64
    # The store's environment composes into the subprocess environment
    # at execution time, after the store is unlocked
    env = runner._extra_env()
    assert env["TF_VAR_state_passphrase"] == passphrase


def write_drop_in(project, providers):
    """Write the view's configuration drop-in, the way the view
    creation does, and merge the recorded set into the live
    configuration."""
    drop_in = os.path.join(project.path, ".debops", "conf.d",
                           "view-" + project.view + "-tofu.toml")
    os.makedirs(os.path.dirname(drop_in), exist_ok=True)
    with open(drop_in, "w") as handle:
        handle.write('[views."{}".tofu]\nproviders = {}\n'.format(
            project.view, providers))
    project.config.merge({'views': {project.view: {'tofu': {
        'providers': providers}}}})
    return drop_in


def test_provider_options_refused_on_an_existing_view(tofu_project):
    """The '--provider' options apply when a view is created: an
    existing view's provider set is recorded in its configuration
    drop-in, which the user owns."""
    project = tofu_project(project_type="modern")

    with pytest.raises(ValueError,
                       match="The '--provider' options apply when a view "
                             'is created'):
        TofuRunner(project, ["plan"], providers=["lxc/incus"])


def test_provider_options_refused_on_a_view_with_a_drop_in(
        tofu_project, stub_tofu_subprocess):
    """A view whose tree is broken keeps its recorded provider set:
    repair does not get to rewrite the user's decision."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    TofuRunner(project, ["plan"], providers=["lxc/incus"]).execute()
    os.remove(os.path.join(view_dir, "main.tf"))

    with pytest.raises(ValueError,
                       match="The '--provider' options apply when a view "
                             'is created'):
        TofuRunner(project, ["plan"], providers=["lxc/incus"])


def test_drop_in_is_written_once(tofu_project, stub_tofu_subprocess):
    """The configuration drop-in is written when the view is created
    and never modified by the commands again: the user owns it."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    drop_in = os.path.join(project.path, ".debops", "conf.d",
                           "view-" + project.view + "-tofu.toml")
    shutil.rmtree(view_dir)

    TofuRunner(project, ["plan"], providers=["lxc/incus"]).execute()
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


def test_eval_prints_the_command_without_the_store_secrets(tofu_project):
    """'--eval' prints the command the wrapper would run, with the
    runner-owned environment; the store's values are secret and stay
    out of the output."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    with open(os.path.join(view_dir, "secret", ".env"), "w") as handle:
        handle.write("TF_VAR_state_passphrase=from-the-store\n")

    runner = TofuRunner(project, ["plan"])
    command = runner.eval()

    assert 'TF_WORKSPACE=default' in command
    assert 'tofu plan' in command
    assert 'TF_VAR_state_passphrase' not in command
    assert 'from-the-store' not in command


def test_eval_never_creates_the_view(tofu_project):
    """'--eval' inspects the command without running it: the view tree
    of a project without one is not created."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    runner = TofuRunner(project, ["plan"])
    command = runner.eval()

    assert 'tofu plan' in command
    assert not os.path.exists(view_dir)


def test_modules_come_from_the_configuration(tofu_project,
                                             stub_tofu_subprocess):
    """The 'tofu.default_modules' option is the default module set of
    new views, recorded in the view's configuration drop-in."""
    project = tofu_project(project_type="modern",
                           raw={"tofu": {"default_modules": {
                               "consul": {
                                   "source": "hashicorp/consul/aws"}}}})
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    TofuRunner(project, ["plan"]).execute()

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
                           raw={"tofu": {"default_modules": {
                               "consul": {
                                   "source": "hashicorp/consul/aws"}}}})
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    TofuRunner(project, ["plan"], modules=["terraform-aws-modules/"
                                           "vpc/aws=5.16.0"]
               ).execute()

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

    TofuRunner(project, ["plan"]).execute()

    assert not os.path.exists(os.path.join(view_dir, "modules.tf"))


def test_module_version_pin_is_written(tofu_project,
                                       stub_tofu_subprocess):
    """A '--module' argument with a version pin carries the pin into
    the generated module block."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    TofuRunner(project, ["plan"], modules=["hashicorp/consul/aws=5.0.0"]
               ).execute()

    modules_tf = open(os.path.join(view_dir, "modules.tf")).read()
    assert 'source  = "hashicorp/consul/aws"' in modules_tf
    assert 'version = "5.0.0"' in modules_tf


def test_module_local_name_is_derived_from_the_source(
        tofu_project, stub_tofu_subprocess):
    """The '--module' arguments derive the local module name from the
    source address: the package name of the registry path."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    TofuRunner(project, ["plan"],
               modules=["hashicorp/consul/aws",
                        "git.example.com/ns/name//subdir"]).execute()

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
        TofuRunner(project, ["plan"],
                   modules=["hashicorp/consul/aws",
                            "hashicorp/consul/other"]).execute()


def test_module_inputs_render_from_the_recorded_table(
        tofu_project, stub_tofu_subprocess):
    """The inputs of a recorded module render as the HCL attributes of
    the generated module block."""
    project = tofu_project(project_type="modern",
                           raw={"tofu": {"default_modules": {
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
                                               "port": 8300}}}}}})
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    TofuRunner(project, ["plan"]).execute()

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
                           raw={"tofu": {"default_modules": {
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
                                       "text": "hcl:hello"}}}}})
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    TofuRunner(project, ["plan"]).execute()

    modules_tf = open(os.path.join(view_dir, "modules.tf")).read()
    assert 'image   = var.image_name' in modules_tf
    assert 'cidrs   = module.network.cidrs' in modules_tf
    assert ('count   = var.autoscaling ? var.max_count : '
            'var.min_count' in modules_tf)
    assert 'nothing = null' in modules_tf
    assert 'escaped = "hcl:hello"' in modules_tf
    assert 'text    = hello' in modules_tf


def test_module_options_refused_on_an_existing_view(tofu_project):
    """The '--module' options apply when a view is created: an
    existing view's module set is recorded in its configuration
    drop-in, which the user owns."""
    project = tofu_project(project_type="modern")

    with pytest.raises(ValueError,
                       match="The '--module' options apply when a view "
                             'is created'):
        TofuRunner(project, ["plan"], modules=["hashicorp/consul/aws"])


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
    TofuRunner(project, ["plan"]).execute()
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
                           raw={"tofu": {"default_modules": {
                               "consul": {
                                   "source": "hashicorp/consul/aws",
                                   "version": "5.0.0",
                                   "inputs": {
                                       "datacenter": "dc1",
                                       "server_count": 3,
                                       "image": "hcl:var.image_name"}}}}})
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    shutil.rmtree(view_dir)

    TofuRunner(project, ["plan"]).execute()

    modules_tf = open(os.path.join(view_dir, "modules.tf")).read()
    assert 'source  = "hashicorp/consul/aws"' in modules_tf
    assert 'version = "5.0.0"' in modules_tf
    assert 'datacenter   = "dc1"' in modules_tf
    assert 'server_count = 3' in modules_tf
    assert 'image        = var.image_name' in modules_tf
