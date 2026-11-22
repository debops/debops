# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import fcntl
import hashlib
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
from debops.core.tofu.view import (create_view, rekey_view, reconcile_view)
from debops.core.tofu.providers import resolve_providers
from debops.core.tofu.modules import resolve_modules
from debops.core.secrets import SecretManager


def mkview(project, providers=None, modules=None, encrypt='plain',
           keys=None):
    """Create the view the way 'debops tofu mkview' does; the tests
    create store-less stub projects, so the explicit 'plain' decision
    is the default here."""
    create_view(project, project.view,
                providers=resolve_providers(project, providers),
                modules=resolve_modules(project, modules),
                encrypt=encrypt, keys=keys)


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
def tofu_project(stub_project, tmp_path, monkeypatch):
    """A stub project whose configuration carries the tofu section,
    with the view's tofu directory in place. A stub 'tofu' binary on
    the PATH stands in for the system-wide installation, so that the
    binary resolution does not depend on the test host."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stub_tofu = bin_dir / "tofu"
    stub_tofu.write_text("#!/bin/sh\nexit 0\n")
    stub_tofu.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep +
                       os.environ.get("PATH", ""))

    def _make(**kwargs):
        raw = {"binaries": {"tofu": "tofu"},
               "tofu": {"state_path": "state/terraform.tfstate",
                        "operations": [], "plan_retention": 3,
                        "mkview": {"default_providers": [],
                                   "default_modules": {}},
                        "upstream": {"known_version": "1.13.9"}}}
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
    without_plan = [arg for arg in runner._tofu_command
                    if not arg.startswith("-out=")]
    assert without_plan[-3:] == ["-var", "a=b", "-input=false"]


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
        project.path, "tofu", "views", "prod", "state",
        "terraform.tfstate")


def test_state_file_of_a_named_workspace_is_in_the_workspaces_directory(
        tofu_project):
    project = tofu_project(project_type="modern", view="prod")
    runner = TofuRunner(project, ["plan"], workspace="feature")
    assert runner._state_file() == os.path.join(
        project.path, "tofu", "views", "prod", "state", "workspaces",
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


def test_lost_state_of_an_initialized_view_refuses(tofu_project):
    """The state file with git history but without the file itself
    was lost: OpenTofu would silently re-initialize the state and
    plan a full recreate -- the refusal names the escape option."""
    project = tofu_project()
    runner = TofuRunner(project, ["apply"])
    with mock.patch.object(runner_module.TofuRunner,
                           "_initialized_before", return_value=True), \
            mock.patch.object(runner_module.TofuRunner,
                              "_state_was_lost", return_value=True):
        with pytest.raises(ChildProcessError,
                           match="--allow-missing-state"):
            runner._check_state_presence()


def test_lost_state_passes_with_the_escape_option(tofu_project):
    """The '--allow-missing-state' decision passes the check: the
    deliberate wipe-and-rebuild proceeds."""
    project = tofu_project()
    runner = TofuRunner(project, ["apply"], allow_missing_state=True)
    with mock.patch.object(runner_module.TofuRunner,
                           "_initialized_before", return_value=True), \
            mock.patch.object(runner_module.TofuRunner,
                              "_state_was_lost", return_value=True):
        runner._check_state_presence()


def test_state_without_history_passes_the_check(tofu_project):
    """A state file without git history was never created: the view
    was initialized but not applied yet, and the first operation is
    the legitimate creation."""
    project = tofu_project()
    runner = TofuRunner(project, ["apply"])
    with mock.patch.object(runner_module.TofuRunner,
                           "_initialized_before", return_value=True), \
            mock.patch.object(runner_module.TofuRunner,
                              "_state_was_lost", return_value=False):
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
                return_value={"path": "state/terraform.tfstate"}):
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
    os.makedirs(os.path.join(project.path, "tofu", "state"),
                exist_ok=True)
    state_file = os.path.join(project.path, "tofu", "state",
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


def test_plan_operation_saves_the_plan_file(tofu_project,
                                            stub_tofu_subprocess):
    """A 'plan' without the '-out' option saves the plan file into
    the view's encrypted store: the plan file carries the planned
    state of the view, which the native encryption covers with the
    same key as the state."""
    project = tofu_project(project_type="modern")

    TofuRunner(project, ["plan"]).execute()

    command = stub_tofu_subprocess.call_args[0][0]
    saved = [arg for arg in command if arg.startswith("-out=")]
    assert len(saved) == 1
    plan_path = saved[0].split("=", 1)[1]
    assert plan_path.startswith(os.path.join("plans", "debops-"))
    assert plan_path.endswith(".tfplan")
    assert os.path.isdir(os.path.join(
        project.path, "tofu", "views", project.view,
        "plans"))


def test_plan_retention_prunes_the_expired_plans(tofu_project,
                                                 stub_tofu_subprocess):
    """The retention keeps the newest 'plan_retention' of the plan
    files DebOps saved."""
    project = tofu_project(project_type="modern")
    project.config.merge({'tofu': {'plan_retention': 3}})
    plans_dir = os.path.join(project.path, "tofu", "views",
                             project.view, "plans")
    os.makedirs(plans_dir)
    for stamp in ("20240101T000000", "20240102T000000",
                  "20240103T000000", "20240104T000000",
                  "20240105T000000"):
        with open(os.path.join(
                plans_dir, "debops-{}.tfplan".format(stamp)),
                "w") as handle:
            handle.write("plan")

    TofuRunner(project, ["plan"]).execute()

    assert sorted(os.listdir(plans_dir)) == [
        "debops-20240103T000000.tfplan",
        "debops-20240104T000000.tfplan",
        "debops-20240105T000000.tfplan"]


def test_plan_retention_never_touches_the_operator_plans(
        tofu_project, stub_tofu_subprocess):
    """The plan files the operator saves with the '-out' option are
    never pruned."""
    project = tofu_project(project_type="modern")
    plans_dir = os.path.join(project.path, "tofu", "views",
                             project.view, "plans")
    os.makedirs(plans_dir)
    for stamp in ("20240101T000000", "20240102T000000",
                  "20240103T000000", "20240104T000000"):
        with open(os.path.join(
                plans_dir, "debops-{}.tfplan".format(stamp)),
                "w") as handle:
            handle.write("plan")
    with open(os.path.join(plans_dir, "manual.tfplan"), "w") as handle:
        handle.write("plan")

    TofuRunner(project, ["plan"]).execute()

    assert "manual.tfplan" in os.listdir(plans_dir)


def test_plan_with_out_is_not_saved_by_the_runner(tofu_project,
                                                  stub_tofu_subprocess):
    """A 'plan' with the operator's own '-out' option is not saved
    again by the runner: the operator's path wins."""
    project = tofu_project(project_type="modern")

    TofuRunner(project, ["plan", "-out=manual.tfplan"]).execute()

    command = stub_tofu_subprocess.call_args[0][0]
    assert command.count("-out=manual.tfplan") == 1
    assert not os.path.isdir(os.path.join(
        project.path, "tofu", "views", project.view,
        "plans"))


def test_plan_files_carry_the_sequence_id(tofu_project,
                                          stub_tofu_subprocess):
    """The plan file names carry the monotonic sequence id of the
    view: the ids address the files while the retention prunes the
    oldest ones, and the timestamp sorts the files of one id."""
    project = tofu_project(project_type="modern")

    TofuRunner(project, ["plan"]).execute()

    command = stub_tofu_subprocess.call_args[0][0]
    plan_path = [arg.split("=", 1)[1] for arg in command
                 if arg.startswith("-out=")][0]
    assert re.match(r"debops-1-\d{8}T\d{6}\.tfplan$",
                    os.path.basename(plan_path))


def test_plan_sequence_ids_keep_rising_over_the_retention(
        tofu_project, stub_tofu_subprocess):
    """The retention pruning never collides: the next plan saves
    with the id one above the maximum of the live files, and a wiped
    plans directory resets the counter."""
    project = tofu_project(project_type="modern")
    project.config.merge({'tofu': {'plan_retention': 1}})
    plans_dir = os.path.join(project.path, "tofu", "views",
                             project.view, "plans")
    os.makedirs(plans_dir)
    for name in ("debops-1-20240101T000000.tfplan",
                 "debops-2-20240102T000000.tfplan"):
        with open(os.path.join(plans_dir, name), "w") as handle:
            handle.write("plan")

    TofuRunner(project, ["plan"]).execute()

    command = stub_tofu_subprocess.call_args[0][0]
    plan_path = [arg.split("=", 1)[1] for arg in command
                 if arg.startswith("-out=")][0]
    assert os.path.basename(plan_path).startswith("debops-3-")
    # the retention pruned the oldest sequenced file
    assert sorted(os.listdir(plans_dir)) == [
        "debops-2-20240102T000000.tfplan"]


def test_plan_retention_sorts_by_the_sequence(tofu_project,
                                              stub_tofu_subprocess):
    """The retention sorts the sequenced plan files by the id: the
    lexicographic order of the names would break at ten."""
    project = tofu_project(project_type="modern")
    project.config.merge({'tofu': {'plan_retention': 2}})
    plans_dir = os.path.join(project.path, "tofu", "views",
                             project.view, "plans")
    os.makedirs(plans_dir)
    for name in ("debops-9-20240101T000000.tfplan",
                 "debops-10-20240102T000000.tfplan",
                 "debops-11-20240103T000000.tfplan"):
        with open(os.path.join(plans_dir, name), "w") as handle:
            handle.write("plan")

    TofuRunner(project, ["plan"]).execute()

    assert sorted(os.listdir(plans_dir)) == [
        "debops-10-20240102T000000.tfplan",
        "debops-11-20240103T000000.tfplan"]


def test_plan_drift_exitcode_saves_and_announces(
        tofu_project, stub_tofu_subprocess, caplog):
    """A '-detailed-exitcode' plan exits 2 when the plan carries
    changes: the drift-detection success saves, announces and
    retains the plan file the way the clean success does -- the
    drift plan is not a failure and must not evade the retention."""
    project = tofu_project(project_type="modern")
    stub_tofu_subprocess.return_value.returncode = 2
    with caplog.at_level(logging.INFO):
        TofuRunner(project, ["plan", "-detailed-exitcode"]).execute()

    assert "Saved the plan file" in caplog.text
    assert os.path.isdir(os.path.join(
        project.path, "tofu", "views", project.view, "plans"))


def test_failed_plan_does_not_announce_or_prune(
        tofu_project, stub_tofu_subprocess, caplog):
    """A plan which fails leaves the half-saved plan file alone:
    nothing is announced and the retention does not run -- the
    failure is not a success, and the half-written artifact is not
    presented as a reviewable plan."""
    project = tofu_project(project_type="modern")
    stub_tofu_subprocess.return_value.returncode = 1
    with caplog.at_level(logging.INFO):
        TofuRunner(project, ["plan"]).execute()

    assert "Saved the plan file" not in caplog.text


def test_keyboard_interrupt_skips_the_post_hooks(
        tofu_project, stub_tofu_subprocess):
    """The interrupt releases the store lock and skips the post
    hooks: the operation did not complete, and the post-operation
    automation must not run on a half-finished state. The failure
    paths run the hooks, the interrupt does not."""
    project = tofu_project(project_type="modern")
    stub_tofu_subprocess.return_value.communicate.side_effect = \
        KeyboardInterrupt()

    with pytest.raises(SystemExit):
        TofuRunner(project, ["plan"]).execute()

    post_calls = [call for call in runner_module.run_hooks.call_args_list
                  if call.args[1] == 'post-tofu-plan']
    assert not post_calls


def test_backend_metadata_parses_the_recorded_document(
        tofu_project, monkeypatch):
    """The backend metadata drives the workspace layout: the
    document the initialization records is parsed for the state
    paths, and the non-local backends and the broken documents read
    as 'no backend'."""
    project = tofu_project(project_type="modern")
    data_dir = os.path.join(project.path, '.tofu-data')
    monkeypatch.setattr(runner_module.cache, "data_dir",
                        lambda proj: data_dir)
    metadata = os.path.join(data_dir, 'terraform.tfstate')
    runner = TofuRunner(project, ["plan"])

    os.makedirs(data_dir)
    with open(metadata, "w") as handle:
        json.dump({'backend': {'type': 'local', 'config': {
            'path': 'state/terraform.tfstate',
            'workspace_dir': 'state/workspaces'}}}, handle)
    assert runner._backend_metadata() == {
        'path': 'state/terraform.tfstate',
        'workspace_dir': 'state/workspaces'}

    with open(metadata, "w") as handle:
        json.dump({'backend': {'type': 'http', 'config': {}}}, handle)
    assert runner._backend_metadata() is None

    with open(metadata, "w") as handle:
        handle.write('not-json')
    assert runner._backend_metadata() is None

    os.remove(metadata)
    assert runner._backend_metadata() is None


def test_resolve_plan_file_by_the_sequence(tofu_project):
    """An integer id resolves against the parsed sequences of the
    saved plan files."""
    project = tofu_project(project_type="modern")
    plans_dir = os.path.join(project.path, "tofu", "views",
                             project.view, "plans")
    os.makedirs(plans_dir)
    for name in ("debops-1-20240101T000000.tfplan",
                 "debops-2-20240102T000000.tfplan"):
        with open(os.path.join(plans_dir, name), "w") as handle:
            handle.write("plan")

    assert resolve_plan_file(
        os.path.join(project.path, "tofu", "views", project.view),
        "2") == os.path.join(
        "plans", "debops-2-20240102T000000.tfplan")
    assert [row[0] for row in plan_rows(
        os.path.join(project.path, "tofu", "views",
                     project.view))] == [1, 2]


def test_resolve_plan_file_by_the_prefix(tofu_project):
    """A non-integer id resolves by the unique prefix of the file
    names: the operator's own '-out' plans and the pre-sequence
    DebOps ones carry stamp-only names."""
    project = tofu_project(project_type="modern")
    plans_dir = os.path.join(project.path, "tofu", "views",
                             project.view, "plans")
    os.makedirs(plans_dir)
    for name in ("manual.tfplan", "debops-20240101T000000.tfplan"):
        with open(os.path.join(plans_dir, name), "w") as handle:
            handle.write("plan")
    view_root = os.path.join(project.path, "tofu", "views",
                             project.view)

    assert resolve_plan_file(view_root, "manual") == \
        os.path.join("plans", "manual.tfplan")


def test_resolve_plan_file_refuses_the_collisions(tofu_project):
    """An id which matches several files -- a duplicated sequence,
    an ambiguous prefix -- and an id which matches none refuse with
    the names the view holds."""
    project = tofu_project(project_type="modern")
    plans_dir = os.path.join(project.path, "tofu", "views",
                             project.view, "plans")
    os.makedirs(plans_dir)
    for name in ("debops-3-20240101T000000.tfplan",
                 "debops-3-20240102T000000.tfplan"):
        with open(os.path.join(plans_dir, name), "w") as handle:
            handle.write("plan")
    view_root = os.path.join(project.path, "tofu", "views",
                             project.view)

    with pytest.raises(ValueError, match="not unique"):
        resolve_plan_file(view_root, "3")
    with pytest.raises(ValueError, match="ambiguous"):
        resolve_plan_file(view_root, "debops-3")
    with pytest.raises(ValueError, match="No saved plan"):
        resolve_plan_file(view_root, "7")


# The 'debops tofu plans' operation: the listing without the store
# cycle, the show and the apply through the runner machinery, the
# delete with the id resolved.

def plans_operation(monkeypatch, project, verb=None, plan_id=None,
                    rc=0, json=False):
    """Run the interpreter's plans operation with the runner
    stubbed; returns the stub and the plans directory."""
    from types import SimpleNamespace
    import debops.cli.interpreter as cli_module

    plans_dir = os.path.join(project.path, "tofu", "views",
                             project.view, "plans")
    os.makedirs(plans_dir, exist_ok=True)
    runner = mock.Mock()
    runner.execute.return_value = rc
    runner_stub = mock.Mock(return_value=runner)
    monkeypatch.setattr(cli_module, "TofuRunner", runner_stub)
    args = SimpleNamespace(bell=False, workspace=None, verb=verb,
                           plan_id=plan_id, json=json, no_color=False,
                           allow_missing_state=False)
    interpreter = cli_module.Interpreter.__new__(cli_module.Interpreter)
    interpreter._do_tofu_plans(args, project)
    return runner_stub, plans_dir


def test_the_plans_operation_lists_the_saved_plans(
        tofu_project, monkeypatch, capsys):
    """The bare operation lists the sequenced plan files -- the
    sequence id, the stamp, the size and the age -- without cycling
    the store."""
    project = tofu_project(project_type="modern")
    _, plans_dir = plans_operation(monkeypatch, project)
    for name in ("debops-1-20240101T000000.tfplan",
                 "debops-2-20240102T000000.tfplan"):
        with open(os.path.join(plans_dir, name), "w") as handle:
            handle.write("plan")
    plans_operation(monkeypatch, project)

    out = capsys.readouterr().out
    assert '  1  20240101T000000' in out
    assert '  2  20240102T000000' in out


def test_the_plans_operation_show_applies_through_the_runner(
        tofu_project, monkeypatch, capsys):
    """The 'show' verb renders the plan through the runner -- the
    '--json' flag rides in; the 'apply' verb applies the resolved
    file without the approval machinery."""
    project = tofu_project(project_type="modern")
    plans_dir = os.path.join(project.path, "tofu", "views",
                             project.view, "plans")
    os.makedirs(plans_dir)
    for name in ("debops-1-20240101T000000.tfplan",
                 "debops-2-20240102T000000.tfplan"):
        with open(os.path.join(plans_dir, name), "w") as handle:
            handle.write("plan")

    with pytest.raises(SystemExit) as exc:
        plans_operation(
            monkeypatch, project, verb='show', plan_id='2',
            json=True)
    assert exc.value.code == 0
    import debops.cli.interpreter as cli_module
    runner_stub = cli_module.TofuRunner
    assert runner_stub.call_args.args[1] == [
        'show', '-json', 'plans/debops-2-20240102T000000.tfplan']

    with pytest.raises(SystemExit):
        plans_operation(
            monkeypatch, project, verb='apply', plan_id='2')
    assert cli_module.TofuRunner.call_args.args[1] == [
        'apply', 'plans/debops-2-20240102T000000.tfplan']


def test_the_plans_operation_deletes_the_resolved_plan(
        tofu_project, monkeypatch, capsys):
    """The 'delete' verb removes the resolved plan file and reports
    its view-relative path."""
    project = tofu_project(project_type="modern")
    plans_dir = os.path.join(project.path, "tofu", "views",
                             project.view, "plans")
    os.makedirs(plans_dir)
    for name in ("debops-1-20240101T000000.tfplan",
                 "debops-2-20240102T000000.tfplan"):
        with open(os.path.join(plans_dir, name), "w") as handle:
            handle.write("plan")
    runner_stub, _ = plans_operation(
        monkeypatch, project, verb='delete', plan_id='2')

    assert capsys.readouterr().out == (
        'plans/debops-2-20240102T000000.tfplan\n')
    assert not os.path.exists(os.path.join(
        plans_dir, 'debops-2-20240102T000000.tfplan'))
    runner_stub.assert_not_called()


def test_the_plans_operation_refuses_the_unknown_ids(
        tofu_project, monkeypatch, capsys):
    """An id which resolves to nothing refuses the operation with
    the names the view holds."""
    project = tofu_project(project_type="modern")
    _, plans_dir = plans_operation(monkeypatch, project)
    with open(os.path.join(
            plans_dir, 'debops-1-20240101T000000.tfplan'),
            'w') as handle:
        handle.write('plan')
    with pytest.raises(SystemExit) as exc:
        plans_operation(monkeypatch, project, verb='show',
                        plan_id='7')

    assert exc.value.code == 1
    assert 'No saved plan' in capsys.readouterr().err


def test_human_age_reports_the_seconds(monkeypatch):
    """The age is precise to the second: the plans saved seconds
    apart are distinguishable in the listing, and a file born in
    the same second reports '0 seconds ago'."""
    import debops.cli.interpreter as cli_module
    now = time.time()
    monkeypatch.setattr(cli_module.time, 'time', lambda: now)

    assert cli_module.human_age(now) == '0 seconds ago'
    assert cli_module.human_age(now - 8) == '8 seconds ago'
    assert cli_module.human_age(now - 45) == '45 seconds ago'
    assert cli_module.human_age(now - 61) == '1 minute ago'


def test_plan_retention_zero_disables_the_saving(tofu_project,
                                                 stub_tofu_subprocess):
    """'plan_retention = 0' disables the plan saving."""
    project = tofu_project(project_type="modern")
    project.config.merge({'tofu': {'plan_retention': 0}})

    TofuRunner(project, ["plan"]).execute()

    command = stub_tofu_subprocess.call_args[0][0]
    assert not any(arg.startswith("-out=") for arg in command)
    assert not os.path.isdir(os.path.join(
        project.path, "tofu", "views", project.view,
        "plans"))


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


def test_execute_captures_the_operation_output(tofu_project,
                                               stub_project_secrets,
                                               monkeypatch):
    """The capture mode collects the stdout of the operation instead
    of streaming it: the machine-readable output the consumers read
    as data -- 'output -json' of the inventory bridge -- never
    reaches the terminal."""
    process = mock.Mock()
    process.returncode = 0
    process.communicate.return_value = (b'{"inventory_seed": {}}', b"")
    popen = mock.Mock(return_value=process)
    monkeypatch.setattr(runner_module.subprocess, "Popen", popen)
    monkeypatch.setattr(runner_module, "run_hooks",
                        mock.Mock(return_value=True))

    runner = TofuRunner(tofu_project(), ["plan"])
    rc, output = runner.execute(capture=True)

    assert rc == 0
    assert output == '{"inventory_seed": {}}'
    assert popen.call_args.kwargs["stdout"] is subprocess.PIPE


def test_execute_streams_the_output_without_capture(
        tofu_project, stub_project_secrets, monkeypatch):
    """Without the capture mode the operation streams: the stdout of
    the subprocess is not piped, the return stays the exit code."""
    process = mock.Mock()
    process.returncode = 0
    process.communicate.return_value = (b"", b"")
    popen = mock.Mock(return_value=process)
    monkeypatch.setattr(runner_module.subprocess, "Popen", popen)
    monkeypatch.setattr(runner_module, "run_hooks",
                        mock.Mock(return_value=True))

    runner = TofuRunner(tofu_project(), ["plan"])
    rc = runner.execute()

    assert rc == 0
    assert popen.call_args.kwargs["stdout"] is None


def test_execute_composes_the_store_environment(tofu_project,
                                                stub_project_secrets,
                                                monkeypatch):
    """The variables of the store's environment file reach the tofu
    subprocess, with the rotated store values winning."""
    project = tofu_project()
    os.makedirs(os.path.join(project.path, "tofu", "secret"),
                exist_ok=True)
    with open(os.path.join(project.path, "tofu", "secret", "environment"),
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
    script = os.path.join(project.path, ".debops", "hooks", "pre-tofu-plan",
                          "00-pre")
    os.makedirs(os.path.dirname(script))
    with open(script, "w") as handle:
        handle.write("#!/bin/sh\ntouch pre-tofu-plan-ran\n")
    os.chmod(script, 0o755)
    # The stub project carries the markers the hook runner requires
    os.makedirs(os.path.join(project.path, ".debops", "conf.d"),
                exist_ok=True)

    runner = TofuRunner(project, ["plan"])
    runner.execute()

    assert os.path.exists(os.path.join(project.path, "pre-tofu-plan-ran"))


def test_failed_hook_aborts_the_operation(tofu_project,
                                          stub_project_secrets):
    project = tofu_project(raw={"binaries": {"tofu": "/bin/true"}})
    script = os.path.join(project.path, ".debops", "hooks", "pre-tofu-plan",
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


def write_drop_in(project, providers, binary_version=None):
    """Write the view's configuration drop-in, the way the view
    creation does, and merge the recorded set into the live
    configuration."""
    drop_in = os.path.join(project.path, ".debops", "conf.d",
                           "view-" + project.view + "-tofu.toml")
    os.makedirs(os.path.dirname(drop_in), exist_ok=True)
    with open(drop_in, "w") as handle:
        handle.write('[views."{}".tofu]\nproviders = {}\n'.format(
            project.view, providers))
        if binary_version is not None:
            handle.write("binary_version = '{}'\n".format(binary_version))
    recorded = {'providers': providers}
    if binary_version is not None:
        recorded['binary_version'] = binary_version
    project.config.merge({'views': {project.view: {'tofu': recorded}}})
    return drop_in


# The fingerprint the install tests pin: the tests carry their own
# trust anchor in the configuration, the way a project does
RELEASE_KEY_FINGERPRINT = 'E3E6E43D84CB852EADB0051D0C0AF313E5FD9F80'


@pytest.fixture
def stub_gpg(tmp_path, monkeypatch):
    """A stub gpg(1) binary for the install tests: it imports the
    requested keys into a fake keyring and reports the pinned
    fingerprint on verification. The environment variables steer the
    canned behavior; the keyring holds the keys the stub imports."""
    bin_dir = tmp_path / "gpg-bin"
    bin_dir.mkdir()
    stub = bin_dir / "gpg"
    stub.write_text(textwrap.dedent('''\
        #!/bin/sh
        case " $* " in
          *" --list-keys "*)
            cat "$GPG_IMPORTED_LOG" 2>/dev/null || true
            exit 0
            ;;
          *" --recv-keys "*)
            if [ -n "$GPG_RECV_FAIL" ]; then
              echo "gpg: keyserver error" >&2
              exit 1
            fi
            fpr="$*"
            if [ -n "$GPG_RECV_KEY" ]; then
              fpr="$GPG_RECV_KEY"
            fi
            echo "fpr:::::::::${fpr##* }:" >> "$GPG_IMPORTED_LOG"
            exit 0
            ;;
          *" --verify "*)
            if [ -n "$GPG_VERIFY_FAIL" ]; then
              echo "gpg: Bad signature" >&2
              exit 1
            fi
            echo "[GNUPG:] VALIDSIG $GPG_SIGNING_KEY 0 0 0 0 0 0 0 0 $GPG_SIGNING_KEY"
            exit 0
            ;;
        esac
        exit 0
        '''))
    stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv('GPG_IMPORTED_LOG',
                       str(tmp_path / 'gpg-imported.log'))
    monkeypatch.setenv('GPG_SIGNING_KEY', RELEASE_KEY_FINGERPRINT)
    return stub


def keyring_config(stub, tmp_path):
    """The configuration fragment which wires the stub gpg, the
    keyring and the upstream options into the project configuration:
    the release base and the release key fingerprint of the install
    verification."""
    return {
        'binaries': {'gpg': str(stub)},
        'gpg': {'debops': {'keyring': {
            'path': str(tmp_path / 'keyring'),
            'gpg_conf': {'keyserver': 'hkps://keyserver.ubuntu.com'},
        }}},
        'tofu': {'upstream': {
            'release_base': ('https://github.com/opentofu/opentofu/'
                             'releases/download/v{version}'),
            'release_key': {
                'fingerprint': RELEASE_KEY_FINGERPRINT}}},
    }


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


def test_eval_prints_the_command_without_the_store_secrets(tofu_project):
    """'--eval' prints the command the wrapper would run, with the
    runner-owned environment; the store's values are secret and stay
    out of the output."""
    project = tofu_project(project_type="modern")
    view_dir = os.path.join(project.path, "tofu", "views", project.view)
    with open(os.path.join(view_dir, "secret", "environment"),
              "w") as handle:
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


@pytest.mark.parametrize("known", ["", "  ", None, 1139])
def test_known_version_refuses_an_invalid_value(tofu_project, known):
    """The known-good version comes from the configuration only: an
    empty or non-string value refuses the view creation."""
    project = tofu_project(project_type="modern")
    project.config.raw['tofu']['upstream']['known_version'] = known

    with pytest.raises(ValueError, match="is not set"):
        binary_module.known_version(project)


def test_known_version_refuses_when_the_option_is_absent(tofu_project):
    """The known-good version option is configuration-only: a
    configuration without it refuses the view creation."""
    project = tofu_project(project_type="modern")
    del project.config.raw['tofu']['upstream']['known_version']

    with pytest.raises(ValueError, match="is not set"):
        binary_module.known_version(project)


def test_managed_binary_path_refuses_traversal_versions():
    """The managed binary paths compose from the version: a
    traversal-shaped value is refused instead of placing the binary
    outside the managed root -- or on the operator's PATH."""
    for version in ('../../../bin', '', None, '.hidden', 'a..b'):
        with pytest.raises(ValueError, match='version'):
            binary_module.managed_binary_path(version)


def test_managed_binary_path_accepts_release_versions():
    """The release version strings resolve inside the managed root."""
    managed = binary_module.managed_binary_path('1.13.9')
    assert managed.startswith(
        binary_module.binary_install_root() + os.sep)


def test_resolve_binary_runs_the_managed_binary(tofu_project, tmp_path,
                                                monkeypatch):
    """A view which pins a version runs the managed binary of that
    version when it is installed."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    version = "1.13.9"
    managed = binary_module.managed_binary_path(version)
    os.makedirs(os.path.dirname(managed))
    with open(managed, "w") as handle:
        handle.write("#!/bin/sh\nexit 0\n")
    os.chmod(managed, 0o755)

    project = tofu_project(project_type="modern")
    project.config.merge({'views': {project.view: {'tofu': {
        'binary_version': version}}}})

    assert binary_module.resolve_binary(project, project.view) == managed


def test_resolve_binary_falls_back_when_the_pin_is_missing(
        tofu_project, tmp_path, monkeypatch):
    """A view which pins a version runs the configured binary when the
    managed binary of the version is not installed."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    project = tofu_project(project_type="modern")
    project.config.merge({'views': {project.view: {'tofu': {
        'binary_version': "1.13.9"}}}})

    assert binary_module.resolve_binary(project, project.view) == "tofu"


def test_resolve_binary_leaves_a_hand_made_view_unmanaged(tofu_project):
    """A view without a recorded version runs the configured binary:
    the system-wide or user-wide installation, unmanaged."""
    project = tofu_project(project_type="modern")
    assert binary_module.resolve_binary(project, project.view) == "tofu"


def test_resolve_binary_refuses_when_no_installation_is_available(
        tofu_project):
    """When the configured binary is not available -- no system-wide
    or user-wide installation carries it -- the resolution fails:
    there is no OpenTofu binary to run."""
    project = tofu_project(project_type="modern")
    project.config.merge({'binaries': {'tofu': 'missing-tofu'}})

    with pytest.raises(ValueError, match="is not available"):
        binary_module.resolve_binary(project, project.view)


def test_resolve_binary_refuses_when_the_pin_is_missing_and_no_fallback(
        tofu_project, tmp_path, monkeypatch):
    """A view whose pinned binary is not installed falls back to the
    configured binary; when that is not available either, the
    resolution fails."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    project = tofu_project(project_type="modern")
    project.config.merge({'binaries': {'tofu': 'missing-tofu'},
                          'views': {project.view: {'tofu': {
                              'binary_version': "1.13.9"}}}})

    with pytest.raises(ValueError, match="is not available"):
        binary_module.resolve_binary(project, project.view)


def test_effective_binary_runs_the_managed_binary(tofu_project, tmp_path,
                                                  monkeypatch):
    """The lenient resolution runs the managed binary of the version
    which the view pins, when it is installed."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    version = "1.13.9"
    managed = binary_module.managed_binary_path(version)
    os.makedirs(os.path.dirname(managed))
    with open(managed, "w") as handle:
        handle.write("#!/bin/sh\nexit 0\n")
    os.chmod(managed, 0o755)

    project = tofu_project(project_type="modern")
    project.config.merge({'views': {project.view: {'tofu': {
        'binary_version': version}}}})

    assert binary_module.effective_binary(project, project.view) \
        == managed


def test_effective_binary_falls_back_without_refusing(tofu_project,
                                                      tmp_path,
                                                      monkeypatch):
    """The lenient resolution falls back to the configured binary
    when the pinned one is not installed, without refusing: the
    runtime configuration reports the effective binary, the runner
    enforces."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    project = tofu_project(project_type="modern")
    project.config.merge({'views': {project.view: {'tofu': {
        'binary_version': "1.13.9"}}}})

    assert binary_module.effective_binary(project, project.view) \
        == "tofu"


def test_effective_binary_leaves_a_hand_made_view_unmanaged(tofu_project):
    """A view without a recorded version resolves to the configured
    binary."""
    project = tofu_project(project_type="modern")
    assert binary_module.effective_binary(project, project.view) \
        == "tofu"


def test_runner_runs_the_pinned_binary(tofu_project, tmp_path, monkeypatch,
                                       stub_tofu_subprocess):
    """The operation runs the managed binary of the version the view
    pins."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    version = "1.13.9"
    managed = binary_module.managed_binary_path(version)
    os.makedirs(os.path.dirname(managed))
    with open(managed, "w") as handle:
        handle.write("#!/bin/sh\nexit 0\n")
    os.chmod(managed, 0o755)

    project = tofu_project(project_type="modern")
    project.config.merge({'views': {project.view: {'tofu': {
        'binary_version': version}}}})

    TofuRunner(project, ["plan"]).execute()

    command = stub_tofu_subprocess.call_args[0][0]
    assert command[0] == managed


def test_runner_falls_back_when_the_pinned_binary_is_missing(
        tofu_project, tmp_path, monkeypatch, stub_tofu_subprocess):
    """The operation runs the configured binary when the pinned
    version is not installed."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    project = tofu_project(project_type="modern")
    project.config.merge({'views': {project.view: {'tofu': {
        'binary_version': "1.13.9"}}}})

    TofuRunner(project, ["plan"]).execute()

    command = stub_tofu_subprocess.call_args[0][0]
    assert command[0] == "tofu"


def test_runner_refuses_when_no_binary_is_available(tofu_project):
    """The operation fails when no OpenTofu binary is available: the
    missing binary is reported instead of a subprocess traceback."""
    project = tofu_project(project_type="modern")
    project.config.merge({'binaries': {'tofu': 'missing-tofu'}})

    runner = TofuRunner(project, ["plan"])
    with pytest.raises(ValueError, match="is not available"):
        runner.execute()


def test_help_operation_runs_without_the_machinery(tofu_project,
                                                   stub_tofu_subprocess,
                                                   monkeypatch):
    """The help surfaces of OpenTofu run without the machinery of the
    wrapper: the store does not cycle, the allow-list and the hooks
    do not gate them."""
    project = tofu_project(project_type="modern")
    project.config.merge({'tofu': {'operations': ['plan']}})
    unlock = mock.Mock(return_value=False)
    monkeypatch.setattr(runner_module.TofuRunner, '_unlock_secrets',
                        unlock)
    hooks = mock.Mock(return_value=True)
    monkeypatch.setattr(runner_module, 'run_hooks', hooks)

    rc = TofuRunner(project, ["help"]).execute()

    assert rc == 0
    unlock.assert_not_called()
    hooks.assert_not_called()


def test_informational_operation_rewrites_the_usage_lines(
        tofu_project, monkeypatch, capsys):
    """The usage lines of the help screens name the wrapper: the help
    does not teach the invocations which bypass it."""
    process = mock.Mock()
    process.returncode = 0
    process.communicate.return_value = (
        b"Usage: tofu [global options] <subcommand> [args]\n"
        b"Usage: tofu plan [options]\n", b"")
    popen = mock.Mock(return_value=process)
    monkeypatch.setattr(runner_module.subprocess, "Popen", popen)

    project = tofu_project(project_type="modern")
    TofuRunner(project, ["help"]).execute()

    out = capsys.readouterr().out
    assert "Usage: debops tofu [global options]" in out
    assert "Usage: debops tofu plan [options]" in out
    assert "Usage: tofu " not in out


def test_regular_operations_stream_without_the_rewrite(
        tofu_project, stub_tofu_subprocess):
    """The regular operations stream directly: their output is not
    captured or rewritten, only the informational ones are."""
    project = tofu_project(project_type="modern")

    TofuRunner(project, ["plan"]).execute()

    popen = stub_tofu_subprocess
    assert popen.call_args.kwargs["stdout"] is None


def test_install_binary_downloads_verifies_and_installs(
        tofu_project, stub_gpg, tmp_path, monkeypatch):
    """The 'debops tofu install' command downloads the release
    archive, verifies it against the release checksums -- whose
    signature the DebOps keyring authenticates -- and installs the
    binary into the managed location."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    monkeypatch.setattr(binary_module, "_release_system", lambda: "linux")
    monkeypatch.setattr(binary_module, "_release_arch", lambda: "amd64")
    version = "1.13.9"
    archive_name = "tofu_1.13.9_linux_amd64.zip"
    sums_name = "tofu_1.13.9_SHA256SUMS"

    releases = tmp_path / "releases"
    releases.mkdir()
    archive = releases / archive_name
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("tofu", "#!/bin/sh\nexit 0\n")
    archive_digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    sums = releases / sums_name
    sums.write_text("{}  {}\n".format(archive_digest, archive_name))
    sig = releases / (sums_name + ".gpgsig")
    sig.write_bytes(b"stub signature")

    def download(url, path):
        name = url.rsplit("/", 1)[-1]
        shutil.copy(str(releases / name), path)

    monkeypatch.setattr(binary_module, "_download", download)

    project = tofu_project(project_type="modern",
                           raw=keyring_config(stub_gpg, tmp_path))
    assert binary_module.install_binary(project, version) is True
    managed = binary_module.managed_binary_path(version)
    assert os.path.isfile(managed)
    assert open(managed).read() == "#!/bin/sh\nexit 0\n"
    assert os.stat(managed).st_mode & 0o111


def test_install_binary_downloads_from_the_configured_base(
        tofu_project, stub_gpg, tmp_path, monkeypatch):
    """The 'tofu.upstream.release_base' option steers the downloads:
    the '{version}' placeholder is substituted with the version to
    install."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    monkeypatch.setattr(binary_module, "_release_system", lambda: "linux")
    monkeypatch.setattr(binary_module, "_release_arch", lambda: "amd64")
    monkeypatch.setattr(binary_module, "_verify_checksums", mock.Mock())
    version = "1.13.9"

    urls = []

    def download(url, path):
        urls.append(url)
        if url.endswith(".zip"):
            with zipfile.ZipFile(path, "w") as zf:
                zf.writestr("tofu", "#!/bin/sh\nexit 0\n")
        else:
            with open(path, "wb") as handle:
                handle.write(b"stub")

    monkeypatch.setattr(binary_module, "_download", download)

    raw = keyring_config(stub_gpg, tmp_path)
    raw['tofu']['upstream']['release_base'] = \
        'https://mirror.example/tofu/v{version}'

    project = tofu_project(project_type="modern", raw=raw)
    assert binary_module.install_binary(project, version) is True

    assert len(urls) == 3
    assert all(url.startswith("https://mirror.example/tofu/v1.13.9/")
               for url in urls)


def test_install_binary_is_idempotent(tofu_project, tmp_path, monkeypatch):
    """The binary which is already installed is not downloaded
    again."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    version = "1.13.9"
    managed = binary_module.managed_binary_path(version)
    os.makedirs(os.path.dirname(managed))
    with open(managed, "w") as handle:
        handle.write("#!/bin/sh\nexit 0\n")
    os.chmod(managed, 0o755)

    download = mock.Mock()
    monkeypatch.setattr(binary_module, "_download", download)

    project = tofu_project(project_type="modern")
    assert binary_module.install_binary(project, version) is False
    download.assert_not_called()


def test_install_binary_refuses_a_mismatched_checksum(
        tofu_project, stub_gpg, tmp_path, monkeypatch):
    """The archive whose checksum does not match the release checksums
    is refused."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    monkeypatch.setattr(binary_module, "_release_system", lambda: "linux")
    monkeypatch.setattr(binary_module, "_release_arch", lambda: "amd64")
    version = "1.13.9"
    archive_name = "tofu_1.13.9_linux_amd64.zip"
    sums_name = "tofu_1.13.9_SHA256SUMS"

    releases = tmp_path / "releases"
    releases.mkdir()
    archive = releases / archive_name
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("tofu", "#!/bin/sh\nexit 0\n")
    sums = releases / sums_name
    sums.write_text("{}  {}\n".format("0" * 64, archive_name))
    sig = releases / (sums_name + ".gpgsig")
    sig.write_bytes(b"stub signature")

    def download(url, path):
        name = url.rsplit("/", 1)[-1]
        shutil.copy(str(releases / name), path)

    monkeypatch.setattr(binary_module, "_download", download)

    project = tofu_project(project_type="modern",
                           raw=keyring_config(stub_gpg, tmp_path))
    with pytest.raises(ValueError, match="does not match"):
        binary_module.install_binary(project, version)
    assert not os.path.isfile(binary_module.managed_binary_path(version))


def test_install_binary_refuses_checksums_without_the_archive(
        tofu_project, stub_gpg, tmp_path, monkeypatch):
    """The checksums file which does not carry the archive's entry
    refuses the install."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    monkeypatch.setattr(binary_module, "_release_system", lambda: "linux")
    monkeypatch.setattr(binary_module, "_release_arch", lambda: "amd64")
    version = "1.13.9"
    archive_name = "tofu_1.13.9_linux_amd64.zip"
    sums_name = "tofu_1.13.9_SHA256SUMS"

    releases = tmp_path / "releases"
    releases.mkdir()
    archive = releases / archive_name
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("tofu", "#!/bin/sh\nexit 0\n")
    sums = releases / sums_name
    sums.write_text("{}  other.zip\n".format("0" * 64))
    sig = releases / (sums_name + ".gpgsig")
    sig.write_bytes(b"stub signature")

    def download(url, path):
        name = url.rsplit("/", 1)[-1]
        shutil.copy(str(releases / name), path)

    monkeypatch.setattr(binary_module, "_download", download)

    project = tofu_project(project_type="modern",
                           raw=keyring_config(stub_gpg, tmp_path))
    with pytest.raises(ValueError, match="do not carry"):
        binary_module.install_binary(project, version)
    assert not os.path.isfile(binary_module.managed_binary_path(version))


def test_install_binary_refuses_a_missing_gpg(tofu_project, tmp_path,
                                              monkeypatch):
    """The install which the keyring cannot run -- a missing gpg --
    refuses: an unverified download is exactly what the pin guards
    against."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    version = "1.13.9"

    project = tofu_project(project_type="modern", raw={
        'binaries': {'gpg': str(tmp_path / 'missing-gpg')},
        'gpg': {'debops': {'keyring': {
            'path': str(tmp_path / 'keyring')}}},
        'tofu': {'upstream': {
            'release_base': ('https://github.com/opentofu/opentofu/'
                             'releases/download/v{version}'),
            'release_key': {
                'fingerprint': RELEASE_KEY_FINGERPRINT}}}})
    with pytest.raises(ValueError, match="is not available"):
        binary_module.install_binary(project, version)
    assert not os.path.isfile(binary_module.managed_binary_path(version))


def test_install_binary_refuses_without_the_fingerprint_option(
        tofu_project, tmp_path, monkeypatch):
    """The install refuses when the release key fingerprint option is
    absent: the trust anchor is configuration-only, there is no
    fallback."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    version = "1.13.9"

    project = tofu_project(project_type="modern")
    with pytest.raises(ValueError, match="is not set"):
        binary_module.install_binary(project, version)
    assert not os.path.isfile(binary_module.managed_binary_path(version))


@pytest.mark.parametrize("fingerprint", ["", "  ", None, 4096, True])
def test_install_binary_refuses_an_invalid_fingerprint(
        tofu_project, stub_gpg, tmp_path, monkeypatch, fingerprint):
    """The install refuses when the release key fingerprint is empty
    or not a string: the option carries the trust anchor or it
    carries nothing."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    version = "1.13.9"

    raw = keyring_config(stub_gpg, tmp_path)
    raw['tofu']['upstream']['release_key']['fingerprint'] = fingerprint

    project = tofu_project(project_type="modern", raw=raw)
    with pytest.raises(ValueError, match="is not set"):
        binary_module.install_binary(project, version)
    assert not os.path.isfile(binary_module.managed_binary_path(version))


@pytest.mark.parametrize("base", ["", "  ", None, 404])
def test_install_binary_refuses_an_invalid_release_base(
        tofu_project, stub_gpg, tmp_path, monkeypatch, base):
    """The install refuses when the release base is empty or not a
    string: the downloads come from the configuration or not at
    all."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    version = "1.13.9"

    raw = keyring_config(stub_gpg, tmp_path)
    raw['tofu']['upstream']['release_base'] = base

    project = tofu_project(project_type="modern", raw=raw)
    with pytest.raises(ValueError, match="is not set"):
        binary_module.install_binary(project, version)
    assert not os.path.isfile(binary_module.managed_binary_path(version))


def test_install_binary_refuses_an_unreachable_keyserver(
        tofu_project, stub_gpg, tmp_path, monkeypatch):
    """The key which the keyserver does not carry refuses the install
    with the way out: the manual import into the DebOps keyring."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    monkeypatch.setenv('GPG_RECV_FAIL', '1')
    version = "1.13.9"

    project = tofu_project(project_type="modern",
                           raw=keyring_config(stub_gpg, tmp_path))
    with pytest.raises(ValueError, match="cannot be imported"):
        binary_module.install_binary(project, version)
    assert not os.path.isfile(binary_module.managed_binary_path(version))


def test_install_binary_refuses_a_fingerprint_mismatch(
        tofu_project, stub_gpg, tmp_path, monkeypatch):
    """The key which the keyserver carries under a different
    fingerprint refuses the install: the imported key must match the
    pin."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    monkeypatch.setenv('GPG_RECV_KEY',
                       'AAAA' + RELEASE_KEY_FINGERPRINT[4:])
    version = "1.13.9"

    project = tofu_project(project_type="modern",
                           raw=keyring_config(stub_gpg, tmp_path))
    with pytest.raises(ValueError, match="does not match"):
        binary_module.install_binary(project, version)
    assert not os.path.isfile(binary_module.managed_binary_path(version))


def test_install_binary_refuses_a_bad_signature(
        tofu_project, stub_gpg, tmp_path, monkeypatch):
    """The release checksums whose signature does not verify refuse
    the install."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    monkeypatch.setattr(binary_module, "_release_system", lambda: "linux")
    monkeypatch.setattr(binary_module, "_release_arch", lambda: "amd64")
    monkeypatch.setenv('GPG_VERIFY_FAIL', '1')
    version = "1.13.9"
    archive_name = "tofu_1.13.9_linux_amd64.zip"
    sums_name = "tofu_1.13.9_SHA256SUMS"

    releases = tmp_path / "releases"
    releases.mkdir()
    archive = releases / archive_name
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("tofu", "#!/bin/sh\nexit 0\n")
    archive_digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    sums = releases / sums_name
    sums.write_text("{}  {}\n".format(archive_digest, archive_name))
    sig = releases / (sums_name + ".gpgsig")
    sig.write_bytes(b"stub signature")

    def download(url, path):
        name = url.rsplit("/", 1)[-1]
        shutil.copy(str(releases / name), path)

    monkeypatch.setattr(binary_module, "_download", download)

    project = tofu_project(project_type="modern",
                           raw=keyring_config(stub_gpg, tmp_path))
    with pytest.raises(ValueError, match="does not verify"):
        binary_module.install_binary(project, version)
    assert not os.path.isfile(binary_module.managed_binary_path(version))


def test_reconcile_binaries_installs_the_missing_versions(
        tofu_project, stub_gpg, tmp_path, monkeypatch):
    """The 'debops tofu install' command installs the binaries which
    the project's views pin."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    monkeypatch.setattr(binary_module, "_release_system", lambda: "linux")
    monkeypatch.setattr(binary_module, "_release_arch", lambda: "amd64")
    version = "1.13.9"
    archive_name = "tofu_1.13.9_linux_amd64.zip"
    sums_name = "tofu_1.13.9_SHA256SUMS"

    releases = tmp_path / "releases"
    releases.mkdir()
    archive = releases / archive_name
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("tofu", "#!/bin/sh\nexit 0\n")
    archive_digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    sums = releases / sums_name
    sums.write_text("{}  {}\n".format(archive_digest, archive_name))
    sig = releases / (sums_name + ".gpgsig")
    sig.write_bytes(b"stub signature")

    def download(url, path):
        name = url.rsplit("/", 1)[-1]
        shutil.copy(str(releases / name), path)

    monkeypatch.setattr(binary_module, "_download", download)

    project = tofu_project(project_type="modern",
                           raw=keyring_config(stub_gpg, tmp_path))
    write_drop_in(project, [], binary_version=version)

    assert binary_module.reconcile_binaries(project) == [version]
    assert os.path.isfile(binary_module.managed_binary_path(version))


def test_reconcile_binaries_skips_the_installed_versions(
        tofu_project, tmp_path, monkeypatch):
    """The binaries which are already installed are not downloaded
    again."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    version = "1.13.9"
    managed = binary_module.managed_binary_path(version)
    os.makedirs(os.path.dirname(managed))
    with open(managed, "w") as handle:
        handle.write("#!/bin/sh\nexit 0\n")
    os.chmod(managed, 0o755)

    download = mock.Mock()
    monkeypatch.setattr(binary_module, "_download", download)

    project = tofu_project(project_type="modern")
    write_drop_in(project, [], binary_version=version)

    assert binary_module.reconcile_binaries(project) == []
    download.assert_not_called()


def test_reconcile_binaries_force_reinstalls_the_versions(
        tofu_project, stub_gpg, tmp_path, monkeypatch):
    """The '--force' option reinstalls the binaries which are
    installed already: the download, the verification and the
    install run again."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    monkeypatch.setattr(binary_module, "_release_system", lambda: "linux")
    monkeypatch.setattr(binary_module, "_release_arch", lambda: "amd64")
    version = "1.13.9"
    archive_name = "tofu_1.13.9_linux_amd64.zip"
    sums_name = "tofu_1.13.9_SHA256SUMS"

    releases = tmp_path / "releases"
    releases.mkdir()
    archive = releases / archive_name
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("tofu", "#!/bin/sh\nexit 0\n")
    archive_digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    sums = releases / sums_name
    sums.write_text("{}  {}\n".format(archive_digest, archive_name))
    sig = releases / (sums_name + ".gpgsig")
    sig.write_bytes(b"stub signature")

    downloads = []

    def download(url, path):
        downloads.append(url)
        name = url.rsplit("/", 1)[-1]
        shutil.copy(str(releases / name), path)

    monkeypatch.setattr(binary_module, "_download", download)

    project = tofu_project(project_type="modern",
                           raw=keyring_config(stub_gpg, tmp_path))
    write_drop_in(project, [], binary_version=version)

    assert binary_module.reconcile_binaries(project) == [version]
    assert len(downloads) == 3

    assert binary_module.reconcile_binaries(project, force=True) \
        == [version]
    assert len(downloads) == 6
    assert open(binary_module.managed_binary_path(version)).read() \
        == "#!/bin/sh\nexit 0\n"


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
    process_ok.communicate.return_value = (b"", b"")
    process_fail = mock.Mock()
    process_fail.returncode = 1
    process_fail.communicate.return_value = (b"", b"")
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
