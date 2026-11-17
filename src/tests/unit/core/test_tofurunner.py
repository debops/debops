# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import fcntl
import os
import subprocess
import sys
from unittest import mock

import pytest

import debops.core.runner as runner_base_module
import debops.core.tofu.runner as runner_module
from debops.core.tofu.runner import TofuRunner
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
                        "operations": [], "plan_retention": 3}}
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
        os.makedirs(view_dir, exist_ok=True)
        return project
    return _make


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


def test_missing_state_of_an_initialized_view_is_refused(
        tofu_project, caplog):
    """The one hard refusal: the view was initialized before, its
    state is gone -- the store may be locked, empty or mounted empty;
    OpenTofu would silently re-initialize."""
    project = tofu_project()
    runner = TofuRunner(project, ["apply"])
    with mock.patch.object(runner_module.TofuRunner,
                           "_initialized_before", return_value=True):
        with pytest.raises(ChildProcessError, match="missing"):
            runner._check_state_presence()


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
    with pytest.raises(ChildProcessError, match="workspace"):
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
