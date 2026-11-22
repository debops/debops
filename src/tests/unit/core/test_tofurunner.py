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
from debops.core.tofu.view import create_view, reconcile_view
from debops.core.tofu.providers import resolve_providers
from debops.core.tofu.modules import resolve_modules
from debops.core.secrets import SecretManager
from debops.core.tofu.secrets import TofuSecretStore


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


def test_provider_options_are_refused_outside_mkview(tofu_project):
    """The '--provider' and '--module' options apply when a view is
    created: the runner refuses them on every other operation with
    the placement named, instead of passing them to OpenTofu for a
    cryptic refusal."""
    with pytest.raises(ValueError, match="mkview"):
        TofuRunner(tofu_project(),
                   ["init", "--provider=hashicorp/random"])
    with pytest.raises(ValueError, match="mkview"):
        TofuRunner(tofu_project(),
                   ["plan", "--module", "hashicorp/consul/aws"])


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


def test_one_step_apply_auto_approve_value_is_the_explicit_decision(
        tofu_project, monkeypatch):
    """The '-auto-approve=value' form the CI pipelines write carries
    the explicit decision: an affirmative value satisfies the gate,
    while '-auto-approve=false' declines it and the gate asks for the
    approval instead -- refused without a terminal, like the bare
    one-step apply."""
    monkeypatch.setattr("sys.stdin", mock.Mock(isatty=lambda: False))
    runner = TofuRunner(tofu_project(), ["apply", "-auto-approve=true"])
    runner._check_approval()

    declined = TofuRunner(tofu_project(),
                          ["apply", "-auto-approve=false"])
    with pytest.raises(ChildProcessError, match="approval"):
        declined._check_approval()


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


def test_backend_change_failure_hints_the_reconfigure(
        tofu_project, stub_tofu_subprocess, caplog):
    """A failed operation whose stderr reports the backend change
    names the wrapper's way out: the raw OpenTofu report teaches the
    invocations which bypass the wrapper, the hint restates them as
    the wrapper invocations."""
    project = tofu_project(project_type="modern")
    process = stub_tofu_subprocess.return_value
    process.returncode = 1
    process.stderr = io.BytesIO(
        b"Error: Backend configuration changed\n")
    with caplog.at_level(logging.INFO):
        TofuRunner(project, ["init"]).execute()

    assert "-reconfigure" in caplog.text
    assert "-migrate-state" in caplog.text


def test_stale_data_dir_failure_hints_the_init(
        tofu_project, stub_tofu_subprocess, caplog):
    """The 'Backend initialization required' failure of the stale or
    cleaned data directory hints the wrapper init -- and 'update',
    which runs it and reconciles the view first."""
    project = tofu_project(project_type="modern")
    process = stub_tofu_subprocess.return_value
    process.returncode = 1
    process.stderr = io.BytesIO(
        b'Error: Backend initialization required: '
        b'please run "tofu init"\n')
    with caplog.at_level(logging.INFO):
        TofuRunner(project, ["plan"]).execute()

    assert "debops tofu init" in caplog.text
    assert "debops tofu update" in caplog.text


def test_unrelated_failure_carries_no_backend_hint(
        tofu_project, stub_tofu_subprocess, caplog):
    """A failure which reports nothing about the backend gets no
    hint: the runner does not guess at causes it did not see."""
    project = tofu_project(project_type="modern")
    process = stub_tofu_subprocess.return_value
    process.returncode = 1
    process.stderr = io.BytesIO(b"Error: something else failed\n")
    with caplog.at_level(logging.INFO):
        TofuRunner(project, ["plan"]).execute()

    assert "-reconfigure" not in caplog.text


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
    stub_tofu_subprocess.return_value.wait.side_effect = \
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


def test_the_store_of_a_viewless_project_reports_absence(tofu_project):
    """The project-wide store cycle unlocks every registered store:
    a project which opted out of OpenTofu carries no view and no
    store, and its unlock reports absence instead of the 'not found'
    refusal the generic store raises."""
    project = tofu_project(project_type="modern")
    shutil.rmtree(os.path.join(project.path, "tofu"))
    store = TofuSecretStore(project, project.view)
    assert store.unlock() is False
    assert store.lock() is False


def test_the_store_of_a_tofu_view_delegates_to_the_base(tofu_project):
    """A project with the view has its store: the unlock runs the
    base machinery, which finds nothing to unlock in the bare
    fixture store and reports it."""
    project = tofu_project(project_type="modern")
    store = TofuSecretStore(project, project.view)
    assert store.unlock() is False


def test_execute_cycles_the_store_and_runs_the_operation(
        tofu_project, stub_project_secrets, monkeypatch):
    store = stub_project_secrets
    store.unlock.return_value = True
    popen = mock.Mock(returncode=3)
    process = mock.Mock()
    process.returncode = 3
    process.stdout = io.BytesIO(b"")
    process.stderr = io.BytesIO(b"")
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
    process.stdout = io.BytesIO(b'{"inventory_seed": {}}')
    process.stderr = io.BytesIO(b"")
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
    process.stdout = io.BytesIO(b"")
    process.stderr = io.BytesIO(b"")
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
    process.stdout = io.BytesIO(b"")
    process.stderr = io.BytesIO(b"")
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
