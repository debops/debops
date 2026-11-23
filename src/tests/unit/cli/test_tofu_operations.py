# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The DebOps-level tofu operations against the interpreter dispatch.

The operations orchestrate the core machinery and print through the
shared change-record printer; the tests stub the machinery at the
module boundary and drive the bare interpreter instance, whose real
'_render_tofu_changes' a Mock self would otherwise swallow.
"""

import logging
import os
import time
from types import SimpleNamespace
from unittest import mock

import pytest

import debops.cli.interpreter as cli_module
import debops.core.tofu.binary as binary_module
import debops.core.tofu.inventory as inventory_module
from tests.unit.core.tofu_helpers import write_drop_in


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


def test_the_double_dash_separator_precedes_the_operation():
    """The usage line promises the '[--]' placement between the
    wrapper options and the operation: a leading separator must not
    turn the DebOps-level operations into raw passthrough, where
    OpenTofu would refuse them as unknown commands."""
    parsed = cli_module.Subcommands(['debops', 'tofu', '--', 'plans'])
    assert parsed.args.tofu_args == ['plans']


def test_the_install_operation_eval_reports_the_pinned_binaries(
        tofu_project, tmp_path, monkeypatch, capsys):
    """The '--eval' install reports the binaries it would install
    instead of running the verification chain: the download and the
    keyring stay untouched."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    project = tofu_project(project_type="modern")
    write_drop_in(project, [], binary_version="1.13.9")

    args = SimpleNamespace(force=False, eval=True, no_color=False)
    interpreter = cli_module.Interpreter.__new__(cli_module.Interpreter)
    interpreter._do_tofu_install(args, project)

    out = capsys.readouterr().out
    assert "Would install the pinned OpenTofu binary '1.13.9'" in out


def test_the_install_operation_eval_reports_nothing_to_install(
        tofu_project, tmp_path, monkeypatch, capsys):
    """The '--eval' install on a project whose pinned binaries are
    installed reports the fact and exits clean."""
    monkeypatch.setattr(binary_module, "xdg_data_home", str(tmp_path))
    version = "1.13.9"
    managed = binary_module.managed_binary_path(version)
    os.makedirs(os.path.dirname(managed))
    with open(managed, "w") as handle:
        handle.write("#!/bin/sh\nexit 0\n")

    project = tofu_project(project_type="modern")
    write_drop_in(project, [], binary_version=version)

    args = SimpleNamespace(force=False, eval=True, no_color=False)
    interpreter = cli_module.Interpreter.__new__(cli_module.Interpreter)
    interpreter._do_tofu_install(args, project)

    out = capsys.readouterr().out
    assert "are installed" in out


def tofu_dispatch(monkeypatch, project, **overrides):
    """Drive 'do_tofu' with the project resolution stubbed to the
    fixture's project; returns the bare interpreter and the args."""
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    defaults = dict(
        tofu_args=None, help=False, help_body='THE-HELP-BODY',
        project_dir=project.path, view=None, no_color=False,
        workspace=None, bell=False, allow_missing_state=False,
        eval=False, new_view=None, provider=None, module=None,
        encrypt=None, keys=None, force=False, dry_run=False,
        diff=False, reset=False, clean=False, project=False,
        plugins=False, verb=None, plan_id=None, json=False)
    defaults.update(overrides)
    args = SimpleNamespace(**defaults)
    interpreter = cli_module.Interpreter.__new__(cli_module.Interpreter)
    interpreter.config = mock.Mock()
    interpreter.cwd = project.path
    return interpreter, args


def test_the_tofu_section_requires_an_operand(
        tofu_project, monkeypatch, capsys):
    """The section without an operation and without '--help' refuses
    the invocation: the passthrough would run nothing."""
    project = tofu_project(project_type="modern")
    interpreter, args = tofu_dispatch(monkeypatch, project, tofu_args=[])

    with pytest.raises(SystemExit) as exc:
        interpreter.do_tofu(args)

    assert exc.value.code == 2
    assert 'operand' in capsys.readouterr().err


def test_the_tofu_section_routes_the_debops_operations(
        tofu_project, monkeypatch):
    """The DebOps-level operations route through their handlers with
    the resolved project; the plain operations fall through to the
    wrapped runner."""
    project = tofu_project(project_type="modern")
    for operation in ("mkview", "update", "install", "cache",
                      "inventory", "plans", "rekey"):
        handler = mock.Mock()
        monkeypatch.setattr(cli_module.Interpreter,
                            "_do_tofu_" + operation, handler)
        interpreter, args = tofu_dispatch(
            monkeypatch, project, tofu_args=[operation])
        interpreter.do_tofu(args)
        handler.assert_called_once_with(args, project)

    wrapped = mock.Mock()
    monkeypatch.setattr(cli_module.Interpreter,
                        "_run_wrapped_operation", wrapped)
    interpreter, args = tofu_dispatch(monkeypatch, project,
                                      tofu_args=["plan"])
    interpreter.do_tofu(args)
    wrapped.assert_called_once_with(args, project, ["plan"],
                                    eval_first=False)


def test_the_tofu_help_composes_the_screen(
        tofu_project, monkeypatch, capsys):
    """The '--help' option runs the OpenTofu help through the runner
    -- its usage lines name the wrapper -- and appends the options
    of the wrapper."""
    project = tofu_project(project_type="modern")
    runner = mock.Mock()
    monkeypatch.setattr(cli_module, "TofuRunner",
                        mock.Mock(return_value=runner))
    interpreter, args = tofu_dispatch(monkeypatch, project, help=True)

    with pytest.raises(SystemExit) as exc:
        interpreter.do_tofu(args)

    assert exc.value.code == 0
    cli_module.TofuRunner.assert_called_once_with(
        project, ["help"], no_color=False, workspace=None)
    assert 'THE-HELP-BODY' in capsys.readouterr().out


def test_the_tofu_section_refuses_a_missing_project(
        tofu_project, monkeypatch, capsys):
    """The project resolution failure names the problem and exits."""
    project = tofu_project(project_type="modern")
    interpreter, args = tofu_dispatch(monkeypatch, project,
                                      tofu_args=["plan"])
    # The dispatch helper resolved the project; this failure rides in
    # after it, the way a broken project directory fails the real
    # construction
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=NotADirectoryError("gone")))

    with pytest.raises(SystemExit) as exc:
        interpreter.do_tofu(args)

    assert exc.value.code == 1
    assert 'gone' in capsys.readouterr().err


def test_the_mkview_operation_creates_the_view(
        tofu_project, monkeypatch):
    """The mkview operation resolves the dependency sets and creates
    the view with the encryption decision; the failures map to the
    exit code."""
    project = tofu_project(project_type="modern")
    created = mock.Mock()
    monkeypatch.setattr(cli_module, "create_view", created)
    monkeypatch.setattr(cli_module, "resolve_providers",
                        mock.Mock(return_value=["lxc/incus"]))
    monkeypatch.setattr(cli_module, "resolve_modules",
                        mock.Mock(return_value={"vpc": "registry"}))
    args = SimpleNamespace(new_view="tfcoremock",
                           provider=["-p", "lxc/incus"],
                           module=["-m", "registry/vpc"],
                           encrypt="git-crypt", keys=None)
    interpreter = cli_module.Interpreter.__new__(cli_module.Interpreter)
    interpreter._do_tofu_mkview(args, project)

    created.assert_called_once_with(
        project, "tfcoremock", providers=["lxc/incus"],
        modules={"vpc": "registry"}, encrypt="git-crypt", keys=None)

    created.side_effect = ValueError('the view exists')
    with pytest.raises(SystemExit) as exc:
        interpreter._do_tofu_mkview(args, project)
    assert exc.value.code == 1


def test_the_update_operation_reconciles_and_inits(
        tofu_project, monkeypatch, capsys):
    """The update operation reconciles the owned files, renders the
    change records and runs 'tofu init' through the wrapper; the
    dry run stops after the render."""
    project = tofu_project(project_type="modern")
    reconcile = mock.Mock(return_value=[
        {"action": "create", "path": "providers.tf", "diff": None}])
    monkeypatch.setattr(cli_module, "reconcile_view", reconcile)
    runner = mock.Mock()
    runner.execute.return_value = 0
    monkeypatch.setattr(cli_module, "TofuRunner",
                        mock.Mock(return_value=runner))
    args = SimpleNamespace(force=False, dry_run=False, eval=False,
                           diff=False, no_color=False, bell=False,
                           workspace=None, allow_missing_state=False)
    interpreter = cli_module.Interpreter.__new__(cli_module.Interpreter)

    with pytest.raises(SystemExit) as exc:
        interpreter._do_tofu_update(args, project)

    assert exc.value.code == 0
    reconcile.assert_called_once_with(project, project.view,
                                      force=False, dry_run=False)
    cli_module.TofuRunner.assert_called_once_with(
        project, ["init"], bell=False, no_color=False, workspace=None,
        allow_missing_state=False)
    assert 'Create providers.tf' in capsys.readouterr().out

    args = SimpleNamespace(force=False, dry_run=True, eval=False,
                           diff=False, no_color=False, bell=False,
                           workspace=None, allow_missing_state=False)
    cli_module.TofuRunner.reset_mock()
    interpreter._do_tofu_update(args, project)
    cli_module.TofuRunner.assert_not_called()


def test_the_update_operation_refuses_the_reconcile_error(
        tofu_project, monkeypatch, capsys):
    """A user-owned file without '--force' refuses the operation."""
    project = tofu_project(project_type="modern")
    monkeypatch.setattr(cli_module, "reconcile_view",
                        mock.Mock(side_effect=ValueError("user-owned")))
    args = SimpleNamespace(force=False, dry_run=False, eval=False,
                           diff=False, no_color=False, bell=False,
                           workspace=None, allow_missing_state=False)
    interpreter = cli_module.Interpreter.__new__(cli_module.Interpreter)

    with pytest.raises(SystemExit) as exc:
        interpreter._do_tofu_update(args, project)

    assert exc.value.code == 1
    assert 'user-owned' in capsys.readouterr().err


def test_the_install_operation_reports_the_reconciled_binaries(
        tofu_project, monkeypatch, caplog):
    """The non-eval install announces the outcome through the
    journal; the reconcile refusal maps to the exit code."""
    project = tofu_project(project_type="modern")
    reconcile = mock.Mock(return_value=["1.13.9"])
    monkeypatch.setattr(cli_module, "reconcile_binaries", reconcile)
    args = SimpleNamespace(force=False, eval=False)
    interpreter = cli_module.Interpreter.__new__(cli_module.Interpreter)

    interpreter._do_tofu_install(args, project)
    reconcile.assert_called_once_with(project, force=False, dry_run=False)

    reconcile.return_value = []
    with caplog.at_level(logging.INFO):
        interpreter._do_tofu_install(args, project)
    assert 'are installed' in caplog.text

    reconcile.side_effect = ValueError("unknown version")
    with pytest.raises(SystemExit) as exc:
        interpreter._do_tofu_install(args, project)
    assert exc.value.code == 1


def test_the_cache_operation_lists_and_cleans(
        tofu_project, monkeypatch, capsys):
    """The listing renders the entries with their sizes; the '--reset'
    and the '--clean' scopes print the removed paths."""
    project = tofu_project(project_type="modern")
    import debops.core.tofu.cache as cache_module
    cache_stub = mock.Mock()
    cache_stub.human_size = cache_module.human_size
    cache_stub.cache_rows.return_value = [
        ("/home/user/.cache/debops/tofu", 2048, "view system")]
    monkeypatch.setattr(cli_module, "cache", cache_stub)
    args = SimpleNamespace(reset=False, clean=False, project=False,
                           plugins=False)
    interpreter = cli_module.Interpreter.__new__(cli_module.Interpreter)

    interpreter._do_tofu_cache(args, project)
    out = capsys.readouterr().out
    assert '/home/user/.cache/debops/tofu' in out
    assert '2.0K' in out

    cache_stub.reset_cache.return_value = "/reset/path"
    args = SimpleNamespace(reset=True, clean=False, project=False,
                           plugins=False)
    interpreter._do_tofu_cache(args, project)
    assert '/reset/path' in capsys.readouterr().out

    cache_stub.clean_project.return_value = ["/project/path"]
    args = SimpleNamespace(reset=False, clean=True, project=True,
                           plugins=False)
    interpreter._do_tofu_cache(args, project)
    cache_stub.clean_project.assert_called_once_with(project)
    assert '/project/path' in capsys.readouterr().out

    cache_stub.clean_plugins.return_value = "/plugins/path"
    args = SimpleNamespace(reset=False, clean=True, project=False,
                           plugins=True)
    interpreter._do_tofu_cache(args, project)
    assert '/plugins/path' in capsys.readouterr().out

    cache_stub.clean_data_dir.return_value = "/data/path"
    args = SimpleNamespace(reset=False, clean=True, project=False,
                           plugins=False)
    interpreter._do_tofu_cache(args, project)
    cache_stub.clean_data_dir.assert_called_once_with(project)
    assert '/data/path' in capsys.readouterr().out

    cache_stub.cache_rows.return_value = []
    args = SimpleNamespace(reset=False, clean=False, project=False,
                           plugins=False)
    interpreter._do_tofu_cache(args, project)
    assert capsys.readouterr().out == ''


def test_the_rekey_operation_renders_the_changes(
        tofu_project, monkeypatch, capsys):
    """The rekey operation prints the rotation records; the
    failures map to the exit code."""
    project = tofu_project(project_type="modern")
    rekey = mock.Mock(return_value=[
        {"action": "rotate", "path": "secret/environment",
         "diff": None}])
    monkeypatch.setattr(cli_module, "rekey_view", rekey)
    args = SimpleNamespace(workspace=None)
    interpreter = cli_module.Interpreter.__new__(cli_module.Interpreter)

    interpreter._do_tofu_rekey(args, project)
    rekey.assert_called_once_with(project, project.view, workspace=None)
    assert 'Rotate secret/environment' in capsys.readouterr().out

    rekey.side_effect = ValueError("named workspace")
    with pytest.raises(SystemExit) as exc:
        interpreter._do_tofu_rekey(args, project)
    assert exc.value.code == 1


def test_the_wrapped_operation_maps_the_failures(
        tofu_project, monkeypatch, capsys):
    """The shared runner boilerplate exits with the operation's
    return code, refuses the construction failures and prints the
    '--eval' command instead of running it."""
    project = tofu_project(project_type="modern")
    args = SimpleNamespace(bell=False, no_color=False, workspace=None,
                           allow_missing_state=False, eval=False)
    interpreter = cli_module.Interpreter.__new__(cli_module.Interpreter)

    monkeypatch.setattr(cli_module, "TofuRunner",
                        mock.Mock(side_effect=ValueError("no view")))
    with pytest.raises(SystemExit) as exc:
        interpreter._run_wrapped_operation(args, project, ["plan"])
    assert exc.value.code == 1
    assert 'no view' in capsys.readouterr().err

    runner = mock.Mock()
    runner.execute.return_value = 0
    monkeypatch.setattr(cli_module, "TofuRunner",
                        mock.Mock(return_value=runner))
    with pytest.raises(SystemExit) as exc:
        interpreter._run_wrapped_operation(args, project, ["plan"])
    assert exc.value.code == 0

    runner.execute.side_effect = ChildProcessError("state lost")
    with pytest.raises(SystemExit) as exc:
        interpreter._run_wrapped_operation(args, project, ["apply"])
    assert exc.value.code == 1
    assert 'state lost' in capsys.readouterr().err

    runner.eval.return_value = "tofu init -input=false"
    runner.execute.side_effect = None
    with pytest.raises(SystemExit) as exc:
        interpreter._run_wrapped_operation(args, project, ["init"],
                                           eval_first=True)
    assert exc.value.code == 0
    assert 'tofu init -input=false' in capsys.readouterr().out


def test_the_pending_view_creation_is_noted(
        tofu_project, monkeypatch, caplog):
    """The '--eval' print notes the missing view tree: the printed
    command runs after the template application."""
    project = tofu_project(project_type="modern")
    interpreter = cli_module.Interpreter.__new__(cli_module.Interpreter)

    interpreter._note_pending_view_creation(project)
    assert caplog.text == ''

    os.remove(os.path.join(project.path, "tofu", "views",
                           project.view, "main.tf"))
    with caplog.at_level(logging.WARNING):
        interpreter._note_pending_view_creation(project)
    assert 'does not exist yet' in caplog.text


def test_the_change_render_prints_the_actions_and_diffs(caplog):
    """The change records print as capitalized actions, as 'Would'
    on the dry run and as unified diffs with '--diff'; a change
    without a diff prints its action line in both modes -- the
    sensitive values must not reach the terminal."""
    interpreter = cli_module.Interpreter.__new__(cli_module.Interpreter)
    changes = [
        {"action": "create", "path": "providers.tf", "diff": None},
        {"action": "remove", "path": "modules.tf",
         "diff": "--- a/modules.tf\n+++ b/modules.tf\n@@ -1 +0 @@\n"
                 "-module \"vpc\" {}\n"},
    ]

    with mock.patch("sys.stdout", new=capsys_stdout()) as captured:
        interpreter._render_tofu_changes(changes, diff=True,
                                         dry_run=False, color=False)
    assert 'Remove modules.tf' not in captured.text
    assert '-module "vpc" {}' in captured.text

    with mock.patch("sys.stdout", new=capsys_stdout()) as captured:
        interpreter._render_tofu_changes(changes, diff=True,
                                         dry_run=False, color=True)
    assert '\033[31m-module' in captured.text
    assert '\033[32m' not in captured.text

    with mock.patch("sys.stdout", new=capsys_stdout()) as captured:
        interpreter._render_tofu_changes(changes, diff=True,
                                         dry_run=True, color=False)
    assert 'Would create providers.tf' in captured.text


class capsys_stdout:
    """A tiny stdout capture the diff printer writes into."""

    def __init__(self):
        self.text = ''

    def write(self, text):
        self.text += text

    def flush(self):
        pass
