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
