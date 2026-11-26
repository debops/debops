# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the command dispatch in ``debops.cli``.

The ``Interpreter`` constructor builds a real configuration and a parsed
command line; the tests replace both with stubs and either check that the
right command method runs, or call the command methods directly with the
project directory and the runners stubbed out.
"""

from types import SimpleNamespace
from unittest import mock

import json
import locale
import logging
import shlex
from datetime import datetime
import pytest

import debops.cli.interpreter as cli_module
from debops.cli.interpreter import Interpreter
from debops.core import checklists
from debops.core.exceptions import InventorySpecError, NoDefaultViewException
from git import GitCommandError


def make_args(**kwargs):
    # The 'open' parser always provides --dry-run; the default rides
    # along for every simulated argument namespace
    arguments = {'dry_run': False}
    arguments.update(kwargs)
    return SimpleNamespace(**arguments)


def make_interpreter(config=None):
    interpreter = Interpreter.__new__(Interpreter)
    interpreter.args = None
    interpreter.config = (config if config is not None
                          else mock.Mock())
    if config is None:
        # The contract shape of Configuration.get: a list of segments;
        # an unknown key resolves to the {} missing-sentinel
        interpreter.config.get.side_effect = lambda items: (
            'vault/checklists'
            if items == ['checklist', 'commit_path'] else {})
    interpreter.parsed_args = None
    interpreter.cwd = "/shell/cwd"
    return interpreter


def make_parsed(section, command, args):
    return SimpleNamespace(section=section, command=command, args=args)


@pytest.fixture(autouse=True)
def state_home(tmp_path, monkeypatch):
    """Pin the checklist state home to the test tree.

    The executors resolve the state home from the environment; without
    this pin they would write through to the real user state. The pin
    is autouse: an unpinned checklist test leaked a copy into the real
    state home on every suite run before the pin became unconditional.
    """
    home = tmp_path / "state-home"
    monkeypatch.setattr(checklists, "_resolve_state_home",
                        lambda: str(home))
    return home


@pytest.mark.parametrize("command", ["init", "refresh", "lock", "unlock",
                                     "mkview", "commit", "venv"])
def test_init_dispatches_the_project_commands(monkeypatch, command):
    args = make_args(project_dir="/tmp/example")
    monkeypatch.setattr(cli_module, "Configuration",
                        mock.Mock(return_value=SimpleNamespace()))
    monkeypatch.setattr(cli_module, "Subcommands",
                        mock.Mock(return_value=make_parsed("project",
                                                           command, args)))
    command_method = mock.Mock()
    attribute = "do_project_" + command
    monkeypatch.setattr(cli_module.Interpreter, attribute, command_method)

    Interpreter(["debops"])

    command_method.assert_called_once_with(args)


def test_init_dispatches_the_exec_section(monkeypatch):
    args = make_args(project_dir=".")
    monkeypatch.setattr(cli_module, "Configuration",
                        mock.Mock(return_value=SimpleNamespace()))
    monkeypatch.setattr(cli_module, "Subcommands",
                        mock.Mock(return_value=make_parsed("exec", None, args)))
    method = mock.Mock()
    monkeypatch.setattr(cli_module.Interpreter, "do_exec", method)

    Interpreter(["debops"])

    method.assert_called_once_with(args)


@pytest.mark.parametrize("section", ["run", "check"])
def test_init_dispatches_the_run_sections(monkeypatch, section):
    args = make_args(project_dir=".")
    monkeypatch.setattr(cli_module, "Configuration",
                        mock.Mock(return_value=SimpleNamespace()))
    monkeypatch.setattr(cli_module, "Subcommands",
                        mock.Mock(return_value=make_parsed(section, None,
                                                           args)))
    method = mock.Mock()
    monkeypatch.setattr(cli_module.Interpreter, "do_run", method)

    Interpreter(["debops"])

    method.assert_called_once_with(args)


def test_init_dispatches_the_env_section(monkeypatch):
    args = make_args(project_dir=".")
    monkeypatch.setattr(cli_module, "Configuration",
                        mock.Mock(return_value=SimpleNamespace()))
    monkeypatch.setattr(cli_module, "Subcommands",
                        mock.Mock(return_value=make_parsed("env", None, args)))
    method = mock.Mock()
    monkeypatch.setattr(cli_module.Interpreter, "do_env", method)

    Interpreter(["debops"])

    method.assert_called_once_with(args)


def test_init_dispatches_the_tofu_section(monkeypatch):
    args = make_args(project_dir=".")
    monkeypatch.setattr(cli_module, "Configuration",
                        mock.Mock(return_value=SimpleNamespace()))
    monkeypatch.setattr(cli_module, "Subcommands",
                        mock.Mock(return_value=make_parsed("tofu", None,
                                                           args)))
    method = mock.Mock()
    monkeypatch.setattr(cli_module.Interpreter, "do_tofu", method)

    Interpreter(["debops"])

    method.assert_called_once_with(args)


@pytest.mark.parametrize("command", ["list", "get", "set", "check"])
def test_init_dispatches_the_config_commands(monkeypatch, command):
    args = make_args(project_dir=".")
    monkeypatch.setattr(cli_module, "Configuration",
                        mock.Mock(return_value=SimpleNamespace()))
    monkeypatch.setattr(cli_module, "Subcommands",
                        mock.Mock(return_value=make_parsed("config", command,
                                                           args)))
    command_method = mock.Mock()
    attribute = "do_config_" + command
    monkeypatch.setattr(cli_module.Interpreter, attribute, command_method)

    Interpreter(["debops"])

    command_method.assert_called_once_with(args)


@pytest.mark.parametrize("command", ["list", "open", "edit", "commit",
                                     "close"])
def test_init_dispatches_the_checklist_commands(monkeypatch, command):
    args = make_args(project_dir=".")
    monkeypatch.setattr(cli_module, "Configuration",
                        mock.Mock(return_value=SimpleNamespace()))
    monkeypatch.setattr(cli_module, "Subcommands",
                        mock.Mock(return_value=make_parsed("checklist",
                                                           command, args)))
    command_method = mock.Mock()
    attribute = "do_checklist_" + command
    monkeypatch.setattr(cli_module.Interpreter, attribute, command_method)

    Interpreter(["debops"])

    command_method.assert_called_once_with(args)


def test_checklist_list_defaults_the_verbose_to_zero():
    parsed = cli_module.Subcommands(["debops", "checklist", "list"])
    assert parsed.args.verbose == 0


def test_checklist_open_takes_a_copy_id_and_a_checklist():
    parsed = cli_module.Subcommands(["debops", "checklist", "open",
                                     "web", "audit/review"])
    assert parsed.args.checklist == ["web", "audit/review"]


def test_checklist_open_defaults_the_copy_id_to_the_checklist():
    parsed = cli_module.Subcommands(["debops", "checklist", "open",
                                     "audit/review"])
    assert parsed.args.checklist == ["audit/review"]


def test_checklist_open_reset_shorthand_parses():
    parsed = cli_module.Subcommands(["debops", "checklist", "open",
                                     "-r", "web", "audit/review"])
    assert parsed.args.reset is True
    assert parsed.args.checklist == ["web", "audit/review"]


def test_checklist_commit_short_flags_parse():
    parsed = cli_module.Subcommands(["debops", "checklist", "commit",
                                     "-c", "-e", "web"])
    assert parsed.args.close is True
    assert parsed.args.edit is True


def test_checklist_open_rejects_extra_positionals(capsys):
    with pytest.raises(SystemExit) as raised:
        cli_module.Subcommands(["debops", "checklist", "open",
                                "a", "b", "c"])
    assert raised.value.code == 2
    assert "copy id" in capsys.readouterr().err


def test_checklist_open_copies_into_the_state(tmp_path, state_home,
                                              monkeypatch, capsys):
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [ ] Check\n")
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(tmp_path / "packaged"))
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=project)))
    args = make_args(project_dir=str(project), checklist=["audit/review"],
                     reset=False)
    interpreter.do_checklist_open(args)

    state = checklists.checklist_state_dir(project)
    opened = state / "audit" / "review" / "checklist.md"
    assert opened.exists()
    captured = capsys.readouterr()
    assert "Opened audit/review" in captured.out
    # The origin is announced at the moment the shadowing decision
    # matters: which layer's variant of the checklist was opened
    assert "[packaged]" in captured.out
    assert "as copy" not in captured.out


def test_checklist_open_reset_by_copy_id_heals(tmp_path, state_home,
                                               monkeypatch, capsys):
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n")
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(tmp_path / "packaged"))
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    # The copy drifts from the source; the heal re-copies it
    (state / "web" / "checklist.md").write_text("# Drifted\n")
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=project)))
    args = make_args(project_dir=str(project), checklist=["web"],
                     reset=True)
    interpreter.do_checklist_open(args)

    captured = capsys.readouterr()
    assert "Opened audit/review as copy web [packaged]" in captured.out
    assert (state / "web" / "checklist.md").read_text() == \
        "# Review\n- [x] Check\n"


def test_checklist_open_by_copy_id_without_reset_hints(tmp_path,
                                                       state_home,
                                                       monkeypatch,
                                                       capsys):
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n")
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(tmp_path / "packaged"))
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=project)))
    args = make_args(project_dir=str(project), checklist=["web"],
                     reset=False)

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_open(args)

    assert raised.value.code == 1
    lines = capsys.readouterr().err.splitlines()
    assert lines[0] == "Error: Checklist not found: web"
    assert "An open copy web of audit/review exists" in lines[1]
    assert lines[2] == "To reset: debops checklist open web --reset"


def test_checklist_open_reset_with_deleted_source_refuses(
        tmp_path, state_home, monkeypatch, capsys):
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n")
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(tmp_path / "packaged"))
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    source.unlink()
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=project)))
    args = make_args(project_dir=str(project), checklist=["web"],
                     reset=True)

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_open(args)

    assert raised.value.code == 1
    err = capsys.readouterr().err
    assert "An open copy web of audit/review exists" in err
    assert "no longer resolves in any layer" in err
    assert "To reset" not in err
    assert (state / "web").exists()


def test_checklist_open_unknown_name_stays_plain(tmp_path, state_home,
                                                 monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=project)))
    args = make_args(project_dir=str(project), checklist=["typo"],
                     reset=True)

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_open(args)

    assert raised.value.code == 1
    assert capsys.readouterr().err == "Error: Checklist not found: typo\n"


def test_checklist_open_checklist_name_wins_over_copy_id(
        tmp_path, state_home, monkeypatch, capsys):
    # 'web' is both a checklist name and an open copy id; discovery
    # keeps precedence: the checklist opens fresh and --reset
    # discards the copy id's previous state, as reset always does
    packaged = tmp_path / "packaged" / "checklists"
    (packaged / "web.md").parent.mkdir(parents=True)
    (packaged / "web.md").write_text("# Web\n- [ ] Task\n")
    other = packaged / "audit" / "review.md"
    other.parent.mkdir(parents=True)
    other.write_text("# Review\n- [x] Check\n")
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(tmp_path / "packaged"))
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    checklists.open_copy(other, "audit/review", "packaged", "web", state)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=project)))
    args = make_args(project_dir=str(project), checklist=["web"],
                     reset=True)
    interpreter.do_checklist_open(args)

    captured = capsys.readouterr()
    assert "Opened web [packaged]" in captured.out
    sidecar = json.loads((state / "web" / "copy.json").read_text())
    assert sidecar["checklist"] == "web"


def test_print_error_renders_multiline_reports(capsys):
    cli_module.print_error("first line\nsecond line")

    err = capsys.readouterr().err
    assert err.startswith("Error: first line\n")
    assert "second line" in err


class _FakeInventoryRunner(object):
    """The ansible runner stub: a fixed --list-hosts output."""

    output = ""
    returncode = 0
    last_args = None

    def __init__(self, project, ansible_args, **kwargs):
        self.ansible_args = ansible_args
        _FakeInventoryRunner.last_args = ansible_args

    def capture(self):
        return self.returncode, self.output


def test_checklist_open_expands_an_inventory_pattern(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "host-verify.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Verify\n- [ ] Task\n")
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(tmp_path / "packaged"))
    monkeypatch.setattr(cli_module, "AnsibleRunner", _FakeInventoryRunner)
    _FakeInventoryRunner.output = "  hosts (2):\n    web1\n    web2\n"
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project),
                     checklist=["subdir/[webservers]/check",
                                "host-verify"],
                     reset=False)
    interpreter.do_checklist_open(args)

    captured = capsys.readouterr()
    assert "Opened host-verify as copy subdir/web1/check [packaged]" \
        in captured.out
    assert "Opened host-verify as copy subdir/web2/check [packaged]" \
        in captured.out
    for copy_id in ("subdir/web1/check", "subdir/web2/check"):
        assert (state / copy_id / "checklist.md").exists()


def test_checklist_open_quotes_and_screens_the_pattern(
        tmp_path, state_home, monkeypatch, capsys):
    # The pattern reaches the runner shell-quoted, so it cannot carry
    # shell semantics into capture()'s composition; characters that
    # are not valid in an ansible pattern are refused outright
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    source = tmp_path / "packaged" / "checklists" / "host-verify.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Verify\n- [ ] Task\n")
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(tmp_path / "packaged"))
    monkeypatch.setattr(cli_module, "AnsibleRunner", _FakeInventoryRunner)
    _FakeInventoryRunner.output = "  hosts (1):\n    web servers\n"
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))

    args = make_args(project_dir=str(project),
                     checklist=["subdir/[web servers]/check",
                                "host-verify"],
                     reset=False)
    interpreter.do_checklist_open(args)
    runner_args = _FakeInventoryRunner.last_args
    assert runner_args[0] == shlex.quote("web servers")
    assert runner_args[1] == "--list-hosts"

    _FakeInventoryRunner.last_args = None
    args = make_args(project_dir=str(project),
                     checklist=["subdir/[a;b]/check", "host-verify"],
                     reset=False)
    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_open(args)

    assert raised.value.code == 1
    assert "not valid in an" in capsys.readouterr().err


def test_checklist_open_refuses_a_pattern_matching_no_hosts(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "host-verify.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Verify\n- [ ] Task\n")
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(tmp_path / "packaged"))
    monkeypatch.setattr(cli_module, "AnsibleRunner", _FakeInventoryRunner)
    _FakeInventoryRunner.output = "  hosts (0):\n"
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project),
                     checklist=["subdir/[webservers]/check",
                                "host-verify"],
                     reset=False)

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_open(args)

    assert raised.value.code == 1
    assert "matches no hosts" in capsys.readouterr().err
    assert not state.exists()


def test_checklist_open_refuses_two_inventory_patterns(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "host-verify.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Verify\n- [ ] Task\n")
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(tmp_path / "packaged"))
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project),
                     checklist=["a/[x]/b/[y]", "host-verify"],
                     reset=False)

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_open(args)

    assert raised.value.code == 1
    assert "only one inventory pattern" in capsys.readouterr().err
    assert not state.exists()


def test_checklist_open_dry_run_prints_the_expansion(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "host-verify.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Verify\n- [ ] Task\n")
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(tmp_path / "packaged"))
    monkeypatch.setattr(cli_module, "AnsibleRunner", _FakeInventoryRunner)
    _FakeInventoryRunner.output = "  hosts (2):\n    web1\n    web2\n"
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project),
                     checklist=["subdir/[webservers]/check",
                                "host-verify"],
                     reset=False, dry_run=True)
    interpreter.do_checklist_open(args)

    captured = capsys.readouterr()
    assert "Would open 2 of host-verify [packaged]:" in captured.out
    assert "  subdir/web1/check" in captured.out
    assert "  subdir/web2/check" in captured.out
    assert not (state / "subdir").exists()


def test_checklist_open_dry_run_marks_open_copies(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "host-verify.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Verify\n- [ ] Task\n")
    checklists.open_copy(source, "host-verify", "packaged", "web", state)
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(tmp_path / "packaged"))
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project), checklist=["web"],
                     reset=False, dry_run=True)
    interpreter.do_checklist_open(args)

    out = capsys.readouterr().out
    assert "Would open 1 of host-verify [packaged]:" in out
    assert "  web (already open)" in out


def test_checklist_open_bulk_refuses_when_a_copy_is_open(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "host-verify.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Verify\n- [ ] Task\n")
    checklists.open_copy(source, "host-verify", "packaged",
                         "subdir/web1/check", state)
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(tmp_path / "packaged"))
    monkeypatch.setattr(cli_module, "AnsibleRunner", _FakeInventoryRunner)
    _FakeInventoryRunner.output = "  hosts (2):\n    web1\n    web2\n"
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project),
                     checklist=["subdir/[webservers]/check",
                                "host-verify"],
                     reset=False)

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_open(args)

    assert raised.value.code == 1
    assert "Already open: subdir/web1/check" in capsys.readouterr().err
    # All-or-nothing: the unoccupied id of the batch did not open
    assert not (state / "subdir" / "web2" / "check").exists()


def test_checklist_open_bulk_reset_reopens_the_copies(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "host-verify.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Verify\n- [ ] Task\n")
    checklists.open_copy(source, "host-verify", "packaged",
                         "subdir/web1/check", state)
    (state / "subdir" / "web1" / "check" / "checklist.md").write_text(
        "# Drifted\n")
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(tmp_path / "packaged"))
    monkeypatch.setattr(cli_module, "AnsibleRunner", _FakeInventoryRunner)
    _FakeInventoryRunner.output = "  hosts (2):\n    web1\n    web2\n"
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project),
                     checklist=["subdir/[webservers]/check",
                                "host-verify"],
                     reset=True)
    interpreter.do_checklist_open(args)

    captured = capsys.readouterr()
    assert "Opened host-verify as copy subdir/web1/check [packaged]" \
        in captured.out
    assert "Opened host-verify as copy subdir/web2/check [packaged]" \
        in captured.out
    assert (state / "subdir" / "web1" / "check" /
            "checklist.md").read_text() == "# Verify\n- [ ] Task\n"
    assert (state / "subdir" / "web2" / "check" / "checklist.md").exists()


def test_checklist_open_bulk_reset_refuses_a_cross_checklist_batch(
        tmp_path, state_home, monkeypatch, capsys):
    # The expanded ids are manufactured from the inventory: when one
    # of them holds a different checklist, --reset refuses instead of
    # discarding another checklist's copy
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    verify = tmp_path / "packaged" / "checklists" / "host-verify.md"
    verify.parent.mkdir(parents=True)
    verify.write_text("# Verify\n- [ ] Task\n")
    flow = tmp_path / "packaged" / "checklists" / "flow.md"
    flow.write_text("# Flow\n- [ ] Task\n")
    checklists.open_copy(flow, "flow", "packaged",
                         "subdir/web1/check", state)
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(tmp_path / "packaged"))
    monkeypatch.setattr(cli_module, "AnsibleRunner", _FakeInventoryRunner)
    _FakeInventoryRunner.output = "  hosts (2):\n    web1\n    web2\n"
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project),
                     checklist=["subdir/[webservers]/check",
                                "host-verify"],
                     reset=True)

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_open(args)

    assert raised.value.code == 1
    assert "already hold other checklists" in capsys.readouterr().err
    # Neither the foreign copy nor the unoccupied id opened
    assert (state / "subdir" / "web1" / "check" /
            "checklist.md").read_text() == "# Flow\n- [ ] Task\n"
    assert not (state / "subdir" / "web2" / "check").exists()


def _open_single_copy(tmp_path, state_home):
    """One project with one open copy 'web' of audit/review."""
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    return project, state


def test_checklist_commit_defaults_to_the_single_open_copy(
        tmp_path, state_home, monkeypatch):
    project, state = _open_single_copy(tmp_path, state_home)
    interpreter = make_interpreter()
    project_stub = SimpleNamespace(path=str(project), commit=mock.Mock())
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project_stub))
    args = make_args(project_dir=str(project), copy=None, close=False,
                     edit=False)
    interpreter.do_checklist_commit(args)

    records = list((project / "vault" / "checklists" / "audit" / "review" /
                    "_copies" / "web").glob("*.md"))
    assert len(records) == 1


def test_checklist_edit_defaults_to_the_single_open_copy(
        tmp_path, state_home, monkeypatch, capsys):
    project, state = _open_single_copy(tmp_path, state_home)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    run = mock.Mock()
    monkeypatch.setattr(cli_module.subprocess, "run", run)
    args = make_args(project_dir=str(project), copy=None)
    interpreter.do_checklist_edit(args)

    assert run.call_args.args[0][-1] == \
        str(state / "web" / "checklist.md")
    assert "web: 1/1 done" in capsys.readouterr().out


def test_checklist_close_defaults_to_the_single_open_copy(
        tmp_path, state_home, monkeypatch, capsys):
    project, state = _open_single_copy(tmp_path, state_home)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project), copy=None, force=False,
                     all=False)
    interpreter.do_checklist_close(args)

    assert "Closed web" in capsys.readouterr().out
    assert not (state / "web").exists()


def test_checklist_commands_refuse_an_ambiguous_default(
        tmp_path, state_home, monkeypatch, capsys):
    project, state = _open_single_copy(tmp_path, state_home)
    other = tmp_path / "packaged" / "checklists" / "audit" / "other.md"
    other.write_text("# Other\n- [x] Check\n")
    checklists.open_copy(other, "audit/other", "packaged", "db", state)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    for operation, kwargs in (("commit", dict(close=False, edit=False)),
                              ("edit", dict()),
                              ("close", dict(force=False, all=False))):
        args = make_args(project_dir=str(project), copy=None, **kwargs)
        method = getattr(interpreter,
                         'do_checklist_{}'.format(operation))
        with pytest.raises(SystemExit) as raised:
            method(args)

        assert raised.value.code == 1, operation
        assert "Several open copies: db, web; name one" in \
            capsys.readouterr().err, operation


def test_checklist_commit_refuses_an_empty_default(tmp_path, state_home,
                                                   monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project), copy=None, close=False,
                     edit=False)

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_commit(args)

    assert raised.value.code == 1
    assert "No open copies" in capsys.readouterr().err


def _config_with_filters(filters):
    """The config stub contract for both checklist knobs."""
    return lambda items: {
        ('checklist', 'filters'): filters,
        ('checklist', 'commit_path'): 'vault/checklists',
    }.get(tuple(items), {})


def test_checklist_list_filters_the_discovery(tmp_path, monkeypatch,
                                              capsys):
    packaged = tmp_path / "packaged"
    example = packaged / "checklists" / "example" / "audit"
    example.mkdir(parents=True)
    (example / "review.md").write_text("# Review\n- [ ] Task\n")
    system = packaged / "checklists" / "system"
    system.mkdir(parents=True)
    (system / "reboot.md").write_text("# Reboot\n- [ ] Task\n")
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(packaged))
    interpreter = make_interpreter()
    interpreter.config.get.side_effect = _config_with_filters(
        ["!example/**"])
    args = make_args(project_dir=str(tmp_path), active=False, verbose=0,
                     format='text')
    interpreter.do_checklist_list(args)

    out = capsys.readouterr().out
    assert "system/reboot" in out
    assert "example" not in out


def test_checklist_open_refuses_a_filtered_checklist(tmp_path, state_home,
                                                     monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    interpreter = make_interpreter()
    interpreter.config.get.side_effect = _config_with_filters(
        ["!example/**"])
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project),
                     checklist=["example/audit/review"], reset=False)

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_open(args)

    assert raised.value.code == 1
    assert "hidden by checklist.filters" in capsys.readouterr().err
    state = checklists.checklist_state_dir(project)
    assert not state.exists()


def test_checklist_state_survives_new_filters(tmp_path, state_home,
                                              monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "example" / "note.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Note\n- [x] Done\n")
    checklists.open_copy(source, "example/note", "packaged", "web", state)

    # The copy was opened before the filter existed; the state
    # commands do not consult the discovery policy
    interpreter = make_interpreter()
    interpreter.config.get.side_effect = _config_with_filters(
        ["!example/**"])
    project_stub = SimpleNamespace(path=str(project), commit=mock.Mock())
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project_stub))
    args = make_args(project_dir=str(project), copy="web", close=False,
                     edit=False)
    interpreter.do_checklist_commit(args)

    records = list((project / "vault" / "checklists" / "example" /
                    "note" / "_copies" / "web").glob("*.md"))
    assert len(records) == 1

    args = make_args(project_dir=str(project), active=True, verbose=0,
                     format='text')
    interpreter.do_checklist_list(args)
    assert "web" in capsys.readouterr().out


def test_checklist_list_refuses_a_malformed_filter(tmp_path, monkeypatch,
                                                   capsys):
    interpreter = make_interpreter()
    interpreter.config.get.side_effect = _config_with_filters(
        "example/**")
    args = make_args(project_dir=str(tmp_path), active=False, verbose=0,
                     format='text')

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_list(args)

    assert raised.value.code == 1
    assert "must be a list of glob patterns" in capsys.readouterr().err


def test_checklist_list_refuses_a_malformed_glob(tmp_path, monkeypatch,
                                                 capsys):
    # A list-shaped value passes the type guard and fails at compile
    # time; the list command reports it instead of a traceback
    interpreter = make_interpreter()
    interpreter.config.get.side_effect = _config_with_filters(
        ["system/[z-a]"])
    args = make_args(project_dir=str(tmp_path), active=False, verbose=0,
                     format='text')

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_list(args)

    assert raised.value.code == 1
    assert "Invalid checklist.filters pattern" in capsys.readouterr().err


def test_checklist_list_prints_condensed_entries(tmp_path, monkeypatch,
                                                 capsys):
    packaged = tmp_path / "packaged"
    source = packaged / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text('---\ntitle: "Review"\n---\n# Review\n- [ ] Check\n')
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(packaged))
    interpreter = make_interpreter()
    args = make_args(project_dir=str(tmp_path), active=False, verbose=0,
                     format='text')
    interpreter.do_checklist_list(args)

    assert capsys.readouterr().out == "audit/review\n"


def test_checklist_list_verbose_adds_the_title_column(tmp_path,
                                                      monkeypatch, capsys):
    packaged = tmp_path / "packaged"
    source = packaged / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text('---\ntitle: "Review"\n---\n# Review\n- [ ] Check\n')
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(packaged))
    interpreter = make_interpreter()
    args = make_args(project_dir=str(tmp_path), active=False, verbose=1,
                     format='text')
    interpreter.do_checklist_list(args)

    assert capsys.readouterr().out == (
        "audit/review \u2502 Review\n")


def test_checklist_list_very_verbose_adds_the_origin(tmp_path,
                                                     monkeypatch, capsys):
    packaged = tmp_path / "packaged"
    source = packaged / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text('---\ntitle: "Review"\n---\n# Review\n- [ ] Check\n')
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(packaged))
    interpreter = make_interpreter()
    args = make_args(project_dir=str(tmp_path), active=False, verbose=2,
                     format='text')
    interpreter.do_checklist_list(args)

    assert capsys.readouterr().out == (
        "audit/review \u2502 Review [packaged]\n")


def test_checklist_list_marks_the_open_copies(tmp_path, state_home,
                                              monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n- [ ] Wait\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(tmp_path / "packaged"))
    interpreter = make_interpreter()
    args = make_args(project_dir=str(project), active=False, verbose=0,
                     format='text')
    interpreter.do_checklist_list(args)

    assert capsys.readouterr().out == (
        "audit/review\n"
        "\u2514\u2500\u2500 web (1/2 done)\n")


def test_checklist_list_nests_the_copy_ids(tmp_path, state_home,
                                           monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n")
    for copy_id in ("cluster3/host1", "web1/alpha", "web1/beta"):
        checklists.open_copy(source, "audit/review", "packaged", copy_id,
                             state)
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(tmp_path / "packaged"))
    interpreter = make_interpreter()
    args = make_args(project_dir=str(project), active=False, verbose=0,
                     format='text')
    interpreter.do_checklist_list(args)

    assert capsys.readouterr().out == (
        "audit/review\n"
        "\u251c\u2500\u2500 cluster3\n"
        "\u2502   \u2514\u2500\u2500 host1 (1/1 done)\n"
        "\u2514\u2500\u2500 web1\n"
        "    \u251c\u2500\u2500 alpha (1/1 done)\n"
        "    \u2514\u2500\u2500 beta (1/1 done)\n")


def test_checklist_list_tree_strips_the_checklist_prefix(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "flow.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Flow\n- [ ] One\n- [ ] Two\n- [ ] Three\n")
    for copy_id in ("flow", "flow/alpha", "alpha/gamma", "alpha/omega",
                    "alpha/one/beta", "alpha/one/zeta"):
        checklists.open_copy(source, "flow", "packaged", copy_id, state)
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(tmp_path / "packaged"))
    interpreter = make_interpreter()
    args = make_args(project_dir=str(project), active=False, verbose=0,
                     format='text')
    interpreter.do_checklist_list(args)

    # The copy flow/alpha nests directly under the checklist root and
    # carries its own status; the unrelated alpha/ ids group under the
    # same node because their paths share the prefix
    assert capsys.readouterr().out == (
        "flow (0/3 done)\n"
        "\u2514\u2500\u2500 alpha (0/3 done)\n"
        "    \u251c\u2500\u2500 gamma (0/3 done)\n"
        "    \u251c\u2500\u2500 omega (0/3 done)\n"
        "    \u2514\u2500\u2500 one\n"
        "        \u251c\u2500\u2500 beta (0/3 done)\n"
        "        \u2514\u2500\u2500 zeta (0/3 done)\n")


def test_checklist_list_tree_keeps_a_colliding_copy_verbatim(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "flow.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Flow\n- [ ] One\n- [ ] Two\n- [ ] Three\n")
    for copy_id in ("flow", "flow/alpha", "alpha"):
        checklists.open_copy(source, "flow", "packaged", copy_id, state)
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(tmp_path / "packaged"))
    interpreter = make_interpreter()
    args = make_args(project_dir=str(project), active=False, verbose=0,
                     format='text')
    interpreter.do_checklist_list(args)

    # Stripping flow/alpha to alpha would merge two copies into one
    # display node and lose a progress value; the copy keeps its
    # verbatim id instead
    assert capsys.readouterr().out == (
        "flow (0/3 done)\n"
        "\u251c\u2500\u2500 alpha (0/3 done)\n"
        "\u2514\u2500\u2500 flow\n"
        "    \u2514\u2500\u2500 alpha (0/3 done)\n")


def test_checklist_list_tree_from_a_subdirectory(tmp_path, state_home,
                                                 monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "flow.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Flow\n- [ ] One\n- [ ] Two\n- [ ] Three\n")
    for copy_id in ("flow", "flow/alpha", "alpha/gamma", "alpha/omega",
                    "alpha/one/beta", "alpha/one/zeta"):
        checklists.open_copy(source, "flow", "packaged", copy_id, state)
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(tmp_path / "packaged"))
    interpreter = make_interpreter()
    # ProjectDir resolves the project root upward; the stub simulates
    # the invocation from a subdirectory
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project / "ansible"), active=False,
                     verbose=0, format='text')
    interpreter.do_checklist_list(args)

    assert capsys.readouterr().out == (
        "flow (0/3 done)\n"
        "\u2514\u2500\u2500 alpha (0/3 done)\n"
        "    \u251c\u2500\u2500 gamma (0/3 done)\n"
        "    \u251c\u2500\u2500 omega (0/3 done)\n"
        "    \u2514\u2500\u2500 one\n"
        "        \u251c\u2500\u2500 beta (0/3 done)\n"
        "        \u2514\u2500\u2500 zeta (0/3 done)\n")


def test_checklist_tree_falls_back_to_ascii():
    glyphs = cli_module._tree_glyphs("ascii")
    assert glyphs == {"branch": "|-- ", "column": "|", "leaf": "`-- ",
                      "pass": "|   ", "indent": "    "}


def test_checklist_list_active_shortens_long_paths(tmp_path, state_home,
                                                   monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / ("debian/"
                                                     "dist-upgrade/"
                                                     "bookworm-to-trixie.md")
    source.parent.mkdir(parents=True)
    source.write_text("# Upgrade\n- [ ] Task\n")
    checklists.open_copy(source, "debian/dist-upgrade/bookworm-to-trixie",
                         "packaged", "web", state)
    interpreter = make_interpreter()
    args = make_args(project_dir=str(project), active=True, verbose=0,
                     format='text')
    interpreter.do_checklist_list(args)

    output = capsys.readouterr().out
    record = json.loads((state / "web" / "copy.json").read_text())
    date = datetime.fromisoformat(record["opened"]).date().isoformat()
    assert "debian/d...o-trixie" in output
    assert "({})".format(date) in output
    assert "0/1 done" in output
    assert "bookworm-to-trixie" not in output.replace(
        "debian/d...o-trixie", "")


def test_checklist_list_active_shows_implicit_copies_in_full(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / ("debian/"
                                                     "dist-upgrade/"
                                                     "bookworm-to-trixie.md")
    source.parent.mkdir(parents=True)
    source.write_text("# Upgrade\n- [ ] Task\n")
    implicit_id = "debian/dist-upgrade/bookworm-to-trixie"
    checklists.open_copy(source, implicit_id, "packaged", implicit_id,
                         state)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=project)))
    args = make_args(project_dir=str(project), copy=None, force=False,
                     all=False)
    args.active = True
    args.verbose = 0
    args.format = 'text'
    interpreter.do_checklist_list(args)

    output = capsys.readouterr().out
    assert "debian/dist-upgrade/bookworm-to-trixie" in output
    assert "debian/d...o-trixie" not in output


def test_checklist_list_active_shows_the_copies(tmp_path, state_home,
                                                monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n- [ ] Wait\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    record = json.loads((state / "web" / "copy.json").read_text())
    date = datetime.fromisoformat(record["opened"]).date().isoformat()
    interpreter = make_interpreter()
    args = make_args(project_dir=str(project), active=True, verbose=0,
                     format='text')
    interpreter.do_checklist_list(args)

    output = capsys.readouterr().out
    assert output == (
        "web    audit/review    ({})    1/2 done\n".format(date))


def test_checklist_commit_reports_unconfigured_vault(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)

    interpreter = make_interpreter()
    interpreter.config.get.side_effect = lambda items: {}
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project), copy="web", close=False,
                     edit=False)

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_commit(args)

    assert raised.value.code == 1
    assert "not configured" in capsys.readouterr().err


def test_checklist_list_active_very_verbose_adds_the_origin(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    record = json.loads((state / "web" / "copy.json").read_text())
    date = datetime.fromisoformat(record["opened"]).date().isoformat()
    interpreter = make_interpreter()
    args = make_args(project_dir=str(project), active=True, verbose=2,
                     format='text')
    interpreter.do_checklist_list(args)

    output = capsys.readouterr().out
    assert output == (
        "web    audit/review    ({})    1/1 done    [packaged]\n".format(
            date))


def test_checklist_commit_records_the_vault_copy(tmp_path, state_home,
                                                 monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n- [ ] Wait\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)

    interpreter = make_interpreter()
    # The real ProjectDir stores the path as a string; the stub must
    # match, or the executor's Path arithmetic is tested against a
    # fiction
    project_stub = SimpleNamespace(path=str(project), commit=mock.Mock())
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project_stub))
    args = make_args(project_dir=str(project), copy="web", close=False,
                     edit=False)
    interpreter.do_checklist_commit(args)

    captured = capsys.readouterr()
    records = list((project / "vault" / "checklists" / "audit" / "review" /
                    "_copies" / "web").glob("*.md"))
    assert len(records) == 1
    assert "not a git repository" in captured.err
    # The vault records are private by default, matching the state
    # directory posture
    assert records[0].stat().st_mode & 0o777 == 0o600
    call = project_stub.commit.call_args
    assert call.kwargs["message"].startswith(
        "checklist: web audit/review (1/2 done")
    assert call.kwargs["paths"] == [str(records[0])]


def test_checklist_list_active_without_copies(state_home, tmp_path,
                                              capsys):
    interpreter = make_interpreter()
    args = make_args(project_dir=str(tmp_path), active=True, verbose=0,
                     format='text')
    interpreter.do_checklist_list(args)

    assert capsys.readouterr().out == ""


def test_checklist_list_resolves_the_project_from_a_subdirectory(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)

    interpreter = make_interpreter()
    # ProjectDir resolves the project root upward; the stub simulates
    # the resolution from a subdirectory invocation
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project / "ansible"), active=True,
                     verbose=0, format='text')
    interpreter.do_checklist_list(args)

    assert "web" in capsys.readouterr().out


def test_checklist_list_survives_an_undecodable_file(tmp_path, monkeypatch,
                                                     capsys):
    packaged = tmp_path / "packaged"
    broken = packaged / "checklists" / "broken.md"
    broken.parent.mkdir(parents=True)
    broken.write_bytes(b"\xff\xfe not utf-8 \xff\n")
    good = packaged / "checklists" / "audit" / "review.md"
    good.parent.mkdir(parents=True)
    good.write_text("# Review\n- [ ] Check\n")
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(packaged))
    interpreter = make_interpreter()
    args = make_args(project_dir=str(tmp_path), active=False, verbose=1,
                     format='text')
    interpreter.do_checklist_list(args)

    out = capsys.readouterr().out
    assert "audit/review" in out
    assert "broken" not in out


def test_checklist_list_verbose_without_entries_is_empty(tmp_path,
                                                         monkeypatch,
                                                         capsys):
    packaged = tmp_path / "packaged"
    (packaged / "checklists").mkdir(parents=True)
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(packaged))
    interpreter = make_interpreter()
    args = make_args(project_dir=str(tmp_path), active=False, verbose=1,
                     format='text')
    interpreter.do_checklist_list(args)

    assert capsys.readouterr().out == ""


def test_checklist_list_json_format(tmp_path, monkeypatch, capsys):
    packaged = tmp_path / "packaged"
    source = packaged / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text('---\ntitle: "Review"\n---\n# Review\n- [x] Check\n'
                      '- [ ] Wait\n')
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(packaged))
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    sidecar = json.loads(
        (state / "web" / "copy.json").read_text())
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project), active=False, verbose=0,
                     format='json')
    interpreter.do_checklist_list(args)

    records = json.loads(capsys.readouterr().out)
    assert len(records) == 1
    entry = records[0]
    assert entry["checklist"] == "audit/review"
    assert entry["origin"] == "packaged"
    assert entry["title"] == "Review"
    assert entry["path"].endswith("audit/review.md")
    assert entry["copies"] == [{
        "copy_id": "web", "implicit": False,
        "opened": sidecar["opened"],
        "counts": {"open": 1, "done": 1, "blocked": 0, "failed": 0,
                   "not_applicable": 0}}]


def test_checklist_list_active_json_format(tmp_path, state_home,
                                           monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    sidecar = json.loads((state / "web" / "copy.json").read_text())
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project), active=True, verbose=0,
                     format='json')
    interpreter.do_checklist_list(args)

    records = json.loads(capsys.readouterr().out)
    assert records == [{
        "copy_id": "web", "implicit": False,
        "checklist": "audit/review",
        "path": str(state / "web" / "checklist.md"),
        "origin": "packaged",
        "opened": sidecar["opened"],
        "counts": {"open": 0, "done": 1, "blocked": 0, "failed": 0,
                   "not_applicable": 0}}]


def test_checklist_list_json_without_entries_is_an_empty_array(
        tmp_path, monkeypatch, capsys):
    packaged = tmp_path / "packaged"
    (packaged / "checklists").mkdir(parents=True)
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(packaged))
    interpreter = make_interpreter()
    args = make_args(project_dir=str(tmp_path), active=False, verbose=0,
                     format='json')
    interpreter.do_checklist_list(args)

    assert json.loads(capsys.readouterr().out) == []


def test_print_error_strips_control_characters(capsys):
    cli_module.print_error("bad \x1b]0;pwned\x07 name")

    err = capsys.readouterr().err
    assert "bad ]0;pwned name" in err
    assert "\x1b" not in err
    assert "\x07" not in err


def test_checklist_edit_runs_the_editor_and_reports_progress(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n- [ ] Wait\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    run = mock.Mock()
    monkeypatch.setattr(cli_module.subprocess, "run", run)
    args = make_args(project_dir=str(project), copy="web")
    interpreter.do_checklist_edit(args)

    argv = run.call_args.args[0]
    assert argv[-1] == str(state / "web" / "checklist.md")
    assert "web: 1/2 done" in capsys.readouterr().out


def test_checklist_edit_falls_back_from_a_broken_editor(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    monkeypatch.setattr(cli_module.checklists, "editor_argv",
                        mock.Mock(side_effect=checklists.ChecklistError(
                            "The EDITOR value is broken")))
    run = mock.Mock()
    monkeypatch.setattr(cli_module.subprocess, "run", run)
    args = make_args(project_dir=str(project), copy="web")
    interpreter.do_checklist_edit(args)

    assert run.call_args.args[0] == ["sensible-editor",
                                     str(state / "web" / "checklist.md")]
    assert "using sensible-editor" in capsys.readouterr().err


def test_checklist_edit_reports_a_missing_editor(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    monkeypatch.setattr(cli_module.subprocess, "run",
                        mock.Mock(side_effect=FileNotFoundError(
                            2, "No such file or directory")))
    args = make_args(project_dir=str(project), copy="web")

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_edit(args)

    assert raised.value.code == 1
    assert "The editor could not be run" in capsys.readouterr().err


def test_checklist_commit_twice_reports_no_changes(tmp_path, state_home,
                                                   monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n- [ ] Wait\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)

    interpreter = make_interpreter()
    project_stub = SimpleNamespace(path=str(project), commit=mock.Mock())
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project_stub))
    args = make_args(project_dir=str(project), copy="web", close=False,
                     edit=False)
    interpreter.do_checklist_commit(args)
    interpreter.do_checklist_commit(args)

    captured = capsys.readouterr()
    assert captured.out.count("Committed") == 1
    assert "No changes since the last commit" in captured.out
    # The git commit is attempted even when the record content is
    # unchanged: a previous run may have written the record and failed
    # the git commit (a rejecting pre-commit hook), and the re-run is
    # the only chance to get the record into history
    assert project_stub.commit.call_count == 2

    args_close = make_args(project_dir=str(project), copy="web",
                           close=True, edit=False)
    interpreter.do_checklist_commit(args_close)
    captured = capsys.readouterr()
    assert "No changes since the last commit" in captured.out
    assert not (state / "web").exists()
    assert project_stub.commit.call_count == 3


def test_checklist_commit_surfaces_git_failures(tmp_path, state_home,
                                                monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)

    interpreter = make_interpreter()
    failing = mock.Mock(side_effect=GitCommandError('git commit', 1))
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project), commit=failing)))
    args = make_args(project_dir=str(project), copy="web", close=False,
                     edit=False)

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_commit(args)

    assert raised.value.code == 1
    assert "git commit of the vault record failed" in \
        capsys.readouterr().err
    # The record stays on disk; the next commit re-attempts the git
    # side instead of treating the record as already committed
    records = list((project / "vault" / "checklists" / "audit" / "review" /
                    "_copies" / "web").glob("*.md"))
    assert len(records) == 1


def test_checklist_commit_retries_git_after_a_failure(tmp_path, state_home,
                                                      monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)

    interpreter = make_interpreter()
    failing = mock.Mock(side_effect=GitCommandError('git commit', 1))
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project), commit=failing)))
    args = make_args(project_dir=str(project), copy="web", close=False,
                     edit=False)
    with pytest.raises(SystemExit):
        interpreter.do_checklist_commit(args)

    healed = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project), commit=healed)))
    interpreter.do_checklist_commit(args)

    assert "No changes since the last commit" in capsys.readouterr().out
    # The record content matches the vault, but the git commit was
    # never made; the re-run must attempt it anyway
    assert healed.called


def test_checklist_commit_roundtrips_utf8_content(tmp_path, state_home,
                                                  monkeypatch):
    monkeypatch.setattr(locale, "getpreferredencoding",
                        lambda do_setlocale=False: "ascii")
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Café check\n", encoding='utf-8')
    checklists.open_copy(source, "audit/review", "packaged", "web", state)

    interpreter = make_interpreter()
    project_stub = SimpleNamespace(path=str(project), commit=mock.Mock())
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project_stub))
    args = make_args(project_dir=str(project), copy="web", close=False,
                     edit=False)
    interpreter.do_checklist_commit(args)

    records = list((project / "vault" / "checklists" / "audit" / "review" /
                    "_copies" / "web").glob("*.md"))
    assert records[0].read_text(encoding='utf-8') == \
        "# Review\n- [x] Café check\n"


def test_checklist_close_refuses_open_items(tmp_path, state_home,
                                            monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [ ] Check\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=project)))
    args = make_args(project_dir=str(project), copy="web", force=False,
                     all=False)

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_close(args)

    assert raised.value.code == 1
    captured = capsys.readouterr()
    assert "is incomplete" in captured.err
    assert "Still open" not in captured.err
    assert (state / "web").exists()


def test_checklist_close_force_discards(tmp_path, state_home, monkeypatch,
                                        capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [ ] Check\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=project)))
    args = make_args(project_dir=str(project), copy="web", force=True,
                     all=False)
    interpreter.do_checklist_close(args)

    assert "Closed web" in capsys.readouterr().out
    assert not (state / "web").exists()


def test_checklist_open_refuses_a_zero_item_checklist(tmp_path, state_home,
                                                      monkeypatch, capsys):
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n\nJust commentary, no task items.\n")
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(tmp_path / "packaged"))
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=project)))
    args = make_args(project_dir=str(project), checklist=["audit/review"],
                     reset=False)

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_open(args)

    assert raised.value.code == 1
    assert "does not contain any task items" in capsys.readouterr().err
    state = checklists.checklist_state_dir(project)
    assert not state.exists()


def test_checklist_commit_refuses_a_copy_without_its_checklist(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    (state / "web" / "copy.json").write_text(
        '{"checklist": "../../elsewhere", '
        '"opened": "2026-11-10T08:00:00+00:00"}')

    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project), copy="web", close=False,
                     edit=False)

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_commit(args)

    assert raised.value.code == 1
    assert "does not record its checklist" in capsys.readouterr().err
    assert not (project / "vault").exists()


def test_checklist_close_refuses_a_zero_item_copy(tmp_path, state_home,
                                                  monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n\nNo task items here.\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=project)))
    args = make_args(project_dir=str(project), copy="web", force=False,
                     all=False)

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_close(args)

    assert raised.value.code == 1
    assert "does not contain any task items" in capsys.readouterr().err
    assert (state / "web").exists()


def test_checklist_close_force_closes_a_zero_item_copy(tmp_path, state_home,
                                                       monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n\nNo task items here.\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=project)))
    args = make_args(project_dir=str(project), copy="web", force=True,
                     all=False)
    interpreter.do_checklist_close(args)

    assert "Closed web" in capsys.readouterr().out
    assert not (state / "web").exists()


def test_checklist_commit_refuses_a_zero_item_copy(tmp_path, state_home,
                                                   monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n\nNo task items here.\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project), copy="web", close=False,
                     edit=False)

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_commit(args)

    assert raised.value.code == 1
    assert "does not contain any task items" in capsys.readouterr().err
    assert not (project / "vault").exists()


def test_checklist_close_all_reports_zero_item_copies(tmp_path, state_home,
                                                      monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    done = tmp_path / "packaged" / "checklists" / "audit" / "done.md"
    done.parent.mkdir(parents=True)
    done.write_text("# Done\n- [x] Check\n")
    empty = tmp_path / "packaged" / "checklists" / "audit" / "empty.md"
    empty.write_text("# Empty\n\nNo task items.\n")
    checklists.open_copy(done, "audit/done", "packaged", "web", state)
    checklists.open_copy(empty, "audit/empty", "packaged", "db", state)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=project)))
    args = make_args(project_dir=str(project), copy=None, force=False,
                     all=True)
    interpreter.do_checklist_close(args)

    captured = capsys.readouterr()
    assert "Closed web" in captured.out
    assert "Still open (no task items): db" in captured.err
    assert (state / "db").exists()


def test_checklist_close_all_closes_completed_copies(tmp_path, state_home,
                                                     monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    complete = tmp_path / "packaged" / "checklists" / "done.md"
    complete.parent.mkdir(parents=True)
    complete.write_text("# Done\n- [x] Check\n")
    pending = tmp_path / "packaged" / "checklists" / "pending.md"
    pending.write_text("# Pending\n- [ ] Check\n")
    checklists.open_copy(complete, "done", "packaged", "web", state)
    checklists.open_copy(pending, "pending", "packaged", "db", state)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=project)))
    args = make_args(project_dir=str(project), copy=None, force=False,
                     all=True)
    interpreter.do_checklist_close(args)

    captured = capsys.readouterr()
    assert "Closed web" in captured.out
    assert "Closed db" not in captured.out
    assert "Still open (incomplete): db" in captured.err
    assert "Error:" not in captured.err
    assert (state / "db").exists()


def test_checklist_close_all_force_closes_everything(tmp_path, state_home,
                                                     monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    complete = tmp_path / "packaged" / "checklists" / "done.md"
    complete.parent.mkdir(parents=True)
    complete.write_text("# Done\n- [x] Check\n")
    pending = tmp_path / "packaged" / "checklists" / "pending.md"
    pending.write_text("# Pending\n- [ ] Check\n")
    checklists.open_copy(complete, "done", "packaged", "web", state)
    checklists.open_copy(pending, "pending", "packaged", "db", state)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=project)))
    args = make_args(project_dir=str(project), copy=None, force=True,
                     all=True)
    interpreter.do_checklist_close(args)

    output = capsys.readouterr().out
    assert "Closed web" in output
    assert "Closed db" in output
    assert not state.exists()


def test_checklist_close_all_without_open_copies_is_silent(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=project)))
    args = make_args(project_dir=str(project), copy=None, force=False,
                     all=True)
    interpreter.do_checklist_close(args)

    assert capsys.readouterr().out == ""


def test_checklist_close_rejects_copy_with_all(capsys):
    with pytest.raises(SystemExit) as raised:
        cli_module.Subcommands(["debops", "checklist", "close",
                                "web", "--all"])
    assert raised.value.code == 2
    assert "not both" in capsys.readouterr().err


def test_checklist_close_needs_a_copy_or_all(tmp_path, state_home,
                                             monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    interpreter = make_interpreter()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project), copy=None, force=False,
                     all=False)

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_close(args)

    assert raised.value.code == 1
    assert "No open copies" in capsys.readouterr().err


def test_checklist_close_force_shorthand_parses():
    parsed = cli_module.Subcommands(["debops", "checklist", "close",
                                     "-f", "web"])
    assert parsed.args.force is True
    assert parsed.args.all is False


def test_init_ignores_unknown_project_commands(monkeypatch):
    monkeypatch.setattr(cli_module, "Configuration",
                        mock.Mock(return_value=SimpleNamespace()))
    monkeypatch.setattr(cli_module, "Subcommands",
                        mock.Mock(return_value=make_parsed(
                            "project", "bogus", make_args())))
    command_methods = {name: mock.Mock() for name in
                       ("do_project_init", "do_project_refresh",
                        "do_project_lock", "do_project_unlock",
                        "do_project_mkview", "do_project_commit",
                        "do_project_venv")}
    for name, method in command_methods.items():
        monkeypatch.setattr(cli_module.Interpreter, name, method)

    Interpreter(["debops"])

    for method in command_methods.values():
        method.assert_not_called()


def test_project_init_creates_the_project(monkeypatch):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    monkeypatch.setattr(cli_module, "ProjectVenv", mock.Mock())
    interpreter = make_interpreter()
    args = make_args(project_dir="/tmp/example", type="legacy",
                     default_view="system", venv=False, requirements=True,
                     git=True, encrypt=None, keys=None, spec_sources=None,
                     allow_io=False, dry_run=False, force=False,
                     graph=False, list=False, host=None, ssh=False,
                     tofu=False, pre_commit=False)

    interpreter.do_project_init(args)

    cli_module.ProjectDir.assert_called_once_with(
        path="/tmp/example", config=interpreter.config, cwd="/shell/cwd",
        project_type="legacy", create=True, encrypt=None, keys=None)
    project.create.assert_called_once_with(
        git_repo=True, venv=False, requirements=True,
        default_view="system", spec_sources=None, allow_io=False,
        dry_run=False, force=False, inspect_mode=None, inspect_host=None, ssh=False)
    cli_module.ProjectVenv.assert_not_called()


def test_project_init_installs_the_virtual_environment(monkeypatch):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    venv = mock.Mock()
    projectvenv_type = mock.Mock(return_value=venv)
    monkeypatch.setattr(cli_module, "ProjectVenv", projectvenv_type)
    interpreter = make_interpreter()
    args = make_args(project_dir="/tmp/example", type="modern",
                     default_view="system", venv=True, requirements=True,
                     git=True, encrypt=None, keys=None, spec_sources=None,
                     allow_io=False, dry_run=False, force=False,
                     graph=False, list=False, host=None, ssh=False,
                     tofu=False, pre_commit=False)

    interpreter.do_project_init(args)

    projectvenv_type.assert_called_once_with(project)
    venv.install.assert_called_once_with()


def test_project_init_skips_the_venv_install_without_requirements(monkeypatch):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    projectvenv_type = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectVenv", projectvenv_type)
    interpreter = make_interpreter()
    args = make_args(project_dir="/tmp/example", type="modern",
                     default_view="system", venv=True, requirements=False,
                     git=True, encrypt=None, keys=None, spec_sources=None,
                     allow_io=False, dry_run=False, force=False,
                     graph=False, list=False, host=None, ssh=False,
                     tofu=False, pre_commit=False)

    interpreter.do_project_init(args)

    project.create.assert_called_once_with(
        git_repo=True, venv=True, requirements=False,
        default_view="system", spec_sources=None, allow_io=False,
        dry_run=False, force=False, inspect_mode=None, inspect_host=None, ssh=False)
    projectvenv_type.assert_not_called()


@pytest.mark.parametrize("action", ["install", "upgrade", "recreate"])
def test_project_venv_runs_the_scoped_actions(monkeypatch, action):
    project = mock.Mock()
    venv = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    monkeypatch.setattr(cli_module, "ProjectVenv",
                        mock.Mock(return_value=venv))
    interpreter = make_interpreter()
    args = make_args(project_dir=".", action=action, scope="python")

    interpreter.do_project_venv(args)

    getattr(venv, action).assert_called_once_with(scope="python")


def test_project_venv_enable_enables_the_project(monkeypatch):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    projectvenv_type = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectVenv", projectvenv_type)
    interpreter = make_interpreter()

    interpreter.do_project_venv(make_args(project_dir=".", action="enable",
                                          scope="all"))

    project.enable_venv.assert_called_once_with(scope="all")
    projectvenv_type.assert_not_called()


def test_project_venv_enable_reports_a_failure(monkeypatch, capsys):
    project = mock.Mock()
    project.enable_venv.side_effect = ValueError("boom")
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_project_venv(make_args(project_dir=".",
                                              action="enable", scope="all"))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().err


def test_project_venv_freezes_the_requirements(monkeypatch):
    project = mock.Mock()
    venv = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    monkeypatch.setattr(cli_module, "ProjectVenv",
                        mock.Mock(return_value=venv))
    interpreter = make_interpreter()

    interpreter.do_project_venv(make_args(project_dir=".", action="freeze",
                                          scope="all"))

    venv.freeze.assert_called_once_with(scope="all")


def test_project_venv_reports_a_failure(monkeypatch, capsys):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=ValueError("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_project_venv(make_args(project_dir=".",
                                              action="install", scope="all"))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().err


@pytest.mark.parametrize("exception", [
    IsADirectoryError, NotADirectoryError, PermissionError,
    InventorySpecError, FileNotFoundError, ChildProcessError, ValueError])
def test_project_init_reports_a_failure(monkeypatch, capsys, exception):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=exception("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_project_init(make_args(
            project_dir="/tmp/example", type="legacy", default_view="system",
            encrypt=None, keys=None, ssh=False))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().err


def test_project_refresh_refreshes_the_project(monkeypatch):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter()

    interpreter.do_project_refresh(make_args(
        project_dir=".", view="system", spec_sources=None, allow_io=False,
        dry_run=False, force=False, graph=False, list=False, host=None))

    project.refresh.assert_called_once_with(
        spec_sources=None, allow_io=False, dry_run=False, force=False,
        inspect_mode=None, inspect_host=None)


def test_project_lock_locks_the_project(monkeypatch):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter()

    interpreter.do_project_lock(make_args(project_dir=".", view="system"))

    project.lock.assert_called_once_with()


def test_project_lock_reports_a_missing_default_view(monkeypatch, capsys):
    project = mock.Mock()
    project.lock.side_effect = NoDefaultViewException("no view")
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_project_lock(make_args(project_dir=".", view="system"))

    assert caught.value.code == 1
    assert "Error: no view" in capsys.readouterr().err


def test_project_unlock_unlocks_the_project(monkeypatch):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter()

    interpreter.do_project_unlock(make_args(project_dir=".", view="system"))

    project.unlock.assert_called_once_with()


def test_project_mkview_creates_the_view(monkeypatch):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter()

    interpreter.do_project_mkview(make_args(
        project_dir=".", new_view="webservers", encrypt=None, keys=None,
        ssh=False))

    project.mkview.assert_called_once_with(view="webservers", ssh=False)


def test_project_commit_commits_interactively(monkeypatch):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter()

    interpreter.do_project_commit(make_args(project_dir="."))

    project.commit.assert_called_once_with(interactive=True)


def test_exec_runs_the_runner(monkeypatch):
    project = mock.Mock()
    runner = mock.Mock()
    runner.execute.return_value = 3
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    runner_type = mock.Mock(return_value=runner)
    monkeypatch.setattr(cli_module, "AnsibleRunner", runner_type)
    interpreter = make_interpreter()
    args = make_args(project_dir=".", view="system", eval=False, bell=True,
                     accept=False, ansible_args=["all"])

    with pytest.raises(SystemExit) as caught:
        interpreter.do_exec(args)

    assert caught.value.code == 3
    runner_type.assert_called_once_with(project, ansible_args=["all"],
                                        bell=True, accept=False)
    runner.execute.assert_called_once_with()


def test_exec_eval_mode_delegates_to_the_runner(monkeypatch, capsys):
    project = mock.Mock()
    runner = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    monkeypatch.setattr(cli_module, "AnsibleRunner",
                        mock.Mock(return_value=runner))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_exec(make_args(project_dir=".", view="system",
                                      eval=True, bell=False,
                                      accept=False,
                                      ansible_args=["all"]))

    assert caught.value.code == 0
    runner.eval.assert_called_once_with()
    runner.execute.assert_not_called()


@pytest.mark.parametrize("exception", [
    NoDefaultViewException, ValueError, FileNotFoundError])
def test_exec_reports_a_runner_failure(monkeypatch, capsys, exception):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    monkeypatch.setattr(cli_module, "AnsibleRunner",
                        mock.Mock(side_effect=exception("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_exec(make_args(project_dir=".", view="system",
                                      eval=False, bell=False,
                                      accept=False,
                                      ansible_args=["all"]))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().err


def test_exec_reports_an_aborted_hook(monkeypatch, capsys):
    project = mock.Mock()
    runner = mock.Mock()
    runner.execute.side_effect = ChildProcessError(
            'Hook pre-exec aborted, not executing Ansible command')
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    monkeypatch.setattr(cli_module, "AnsibleRunner", mock.Mock(return_value=runner))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_exec(make_args(project_dir=".", view="system",
                                      eval=False, bell=False,
                                      accept=False,
                                      ansible_args=["all"]))

    assert caught.value.code == 1
    assert "Hook pre-exec aborted" in capsys.readouterr().err


def test_run_executes_the_playbooks(monkeypatch):
    project = mock.Mock()
    runner = mock.Mock()
    runner.execute.return_value = 0
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    monkeypatch.setattr(cli_module, "AnsiblePlaybookRunner",
                        mock.Mock(return_value=runner))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_run(make_args(project_dir=".", view="system",
                                     eval=False, bell=False,
                                     accept=False,
                                     ansible_args=["site.yml"],
                                     debug=False))

    assert caught.value.code == 0
    runner.execute.assert_called_once_with()


def test_run_reports_a_child_process_failure(monkeypatch, capsys):
    project = mock.Mock()
    runner = mock.Mock()
    runner.execute.side_effect = ChildProcessError("dirty working tree")
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    monkeypatch.setattr(cli_module, "AnsiblePlaybookRunner",
                        mock.Mock(return_value=runner))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_run(make_args(project_dir=".", view="system",
                                     eval=False, bell=False,
                                     accept=False,
                                     ansible_args=["site.yml"],
                                     debug=False))

    assert caught.value.code == 1
    assert "Error: dirty working tree" in capsys.readouterr().err


def test_env_executes_the_command(monkeypatch):
    project = mock.Mock()
    runner = mock.Mock()
    runner.execute.return_value = 0
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    monkeypatch.setattr(cli_module, "EnvRunner",
                        mock.Mock(return_value=runner))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_env(make_args(project_dir=".", view="system",
                                     command_args=["ls"], scope="local"))

    assert caught.value.code == 0
    runner.execute.assert_called_once_with()
    runner.show_env.assert_not_called()


def test_env_shows_the_environment_without_a_command(monkeypatch, capsys):
    project = mock.Mock()
    runner = mock.Mock()
    runner.show_env.return_value = ["DEBOPS_TEST_VARIABLE=1"]
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    monkeypatch.setattr(cli_module, "EnvRunner",
                        mock.Mock(return_value=runner))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_env(make_args(project_dir=".", view="system",
                                     command_args=[], scope="full"))

    assert caught.value.code == 0
    runner.show_env.assert_called_once_with(scope="full")
    assert "DEBOPS_TEST_VARIABLE=1" in capsys.readouterr().out


def test_env_reports_an_aborted_hook(monkeypatch, capsys):
    project = mock.Mock()
    runner = mock.Mock()
    runner.execute.side_effect = ChildProcessError(
            'Hook pre-env aborted, not running command in environment')
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    monkeypatch.setattr(cli_module, "EnvRunner", mock.Mock(return_value=runner))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_env(make_args(project_dir=".", view="system",
                                     command_args=["ls"], scope="local"))

    assert caught.value.code == 1
    assert "Hook pre-env aborted" in capsys.readouterr().err


def test_config_list_lists_the_configuration(monkeypatch, capsys):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter()
    interpreter.config.config_list.return_value = [
        "# Configuration files:", "example"]

    interpreter.do_config_list(make_args(project_dir="."))

    interpreter.config.config_list.assert_called_once_with()
    assert "example" in capsys.readouterr().out


def test_config_list_works_outside_of_a_project(monkeypatch):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=IsADirectoryError("not a dir")))
    interpreter = make_interpreter()
    interpreter.config.config_list.return_value = []

    interpreter.do_config_list(make_args(project_dir="."))

    interpreter.config.config_list.assert_called_once_with()


def test_config_get_prints_the_requested_keys(monkeypatch):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter()
    args = make_args(project_dir=".", key=["project.name", "project.type"],
                     format="json", keys=True, root=False,
                     show_origin=False, show_scope=False)

    interpreter.do_config_get(args)

    assert interpreter.config.config_get.call_count == 2
    interpreter.config.config_get.assert_any_call(
        "project.name", format="json", keys=True, root=False,
        show_origin=False, show_scope=False)
    interpreter.config.config_get.assert_any_call(
        "project.type", format="json", keys=True, root=False,
        show_origin=False, show_scope=False)


def test_config_get_prints_the_whole_configuration(monkeypatch):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=NotADirectoryError("nope")))
    interpreter = make_interpreter()

    interpreter.do_config_get(make_args(project_dir=".", key=None,
                                        format="unix", keys=False,
                                        root=False, show_origin=False,
                                        show_scope=False))

    interpreter.config.config_get.assert_called_once_with(
        ".", format="unix", keys=False, root=False, show_origin=False,
        show_scope=False)


def test_config_get_show_origin_flags(monkeypatch):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter()
    args = make_args(project_dir=".", key=["syslog.level"],
                     format="unix", keys=False, root=False,
                     show_origin=True, show_scope=True)

    interpreter.do_config_get(args)

    interpreter.config.config_get.assert_called_once_with(
        "syslog.level", format="unix", keys=False, root=False,
        show_origin=True, show_scope=True)


def test_config_set_writes_to_the_project_configuration(
        configuration, monkeypatch, tmp_path):
    project = mock.Mock()
    project.path = str(tmp_path)
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter(config=configuration)

    interpreter.do_config_set(make_args(project_dir=".", user=False,
                                        delete=False, key="syslog.level",
                                        values=["DEBUG"], type=None))

    path = (tmp_path / ".debops" / "conf.d" / "override" /
            "99_config_set.json")
    assert json.loads(path.read_text()) == {"syslog": {"level": "DEBUG"}}


def test_config_set_writes_to_the_user_configuration(
        configuration, monkeypatch, tmp_path):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=NotADirectoryError("nope")))
    monkeypatch.setattr(cli_module, "xdg_config_home", str(tmp_path))
    interpreter = make_interpreter(config=configuration)

    interpreter.do_config_set(make_args(project_dir=".", user=False,
                                        delete=False, key="syslog.level",
                                        values=["DEBUG"], type=None))

    path = (tmp_path / "debops" / "conf.d" / "override" /
            "99_config_set.json")
    assert json.loads(path.read_text()) == {"syslog": {"level": "DEBUG"}}


def test_config_set_user_flag_skips_the_project_resolution(
        configuration, monkeypatch, tmp_path):
    project_dir_mock = mock.Mock(side_effect=AssertionError("called"))
    monkeypatch.setattr(cli_module, "ProjectDir", project_dir_mock)
    monkeypatch.setattr(cli_module, "xdg_config_home", str(tmp_path))
    interpreter = make_interpreter(config=configuration)

    interpreter.do_config_set(make_args(project_dir=".", user=True,
                                        delete=False, key="syslog.level",
                                        values=["DEBUG"], type=None))

    project_dir_mock.assert_not_called()
    path = (tmp_path / "debops" / "conf.d" / "override" /
            "99_config_set.json")
    assert json.loads(path.read_text()) == {"syslog": {"level": "DEBUG"}}


def test_config_set_deletes_from_the_project_configuration(
        configuration, monkeypatch, tmp_path):
    project = mock.Mock()
    project.path = str(tmp_path)
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    option_file = (tmp_path / ".debops" / "conf.d" /
                   "override" / "99_config_set.json")
    option_file.parent.mkdir(parents=True)
    option_file.write_text('{"syslog": {"level": "DEBUG", '
                           '"facility": "user"}}\n')
    interpreter = make_interpreter(config=configuration)

    interpreter.do_config_set(make_args(project_dir=".", user=False,
                                        delete=True, key="syslog.level",
                                        values=None, type=None))

    assert json.loads(option_file.read_text()) == {
        "syslog": {"facility": "user"}}


def test_config_set_reports_errors(configuration, monkeypatch, tmp_path,
                                   capsys):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=NotADirectoryError("nope")))
    monkeypatch.setattr(cli_module, "xdg_config_home", str(tmp_path))
    interpreter = make_interpreter(config=configuration)

    with pytest.raises(SystemExit):
        interpreter.do_config_set(make_args(project_dir=".", user=False,
                                            delete=False,
                                            key="myscript.retries",
                                            values=["5"], type=None))

    assert "custom options belong" in capsys.readouterr().err


def test_config_check_passes_a_clean_configuration(configuration, monkeypatch,
                                                   caplog):
    caplog.set_level(logging.NOTICE)
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=NotADirectoryError("nope")))
    interpreter = make_interpreter(config=configuration)

    interpreter.do_config_check(make_args(project_dir=".", strict=False))

    assert "The DebOps configuration is valid" in caplog.text


def test_config_check_fails_on_dropped_options(configuration, monkeypatch):
    configuration._violations.append(
        {"kind": "type", "file": "/etc/debops/conf.d/options.yml",
         "option": "syslog.port", "dropped": True,
         "message": "option 'syslog.port' must be of type integer, "
                    "not str"})
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=NotADirectoryError("nope")))
    interpreter = make_interpreter(config=configuration)

    with pytest.raises(SystemExit) as excinfo:
        interpreter.do_config_check(make_args(project_dir=".",
                                              strict=False))

    assert excinfo.value.code == 1


def test_config_check_tolerates_unknown_options_by_default(
        configuration, monkeypatch, caplog):
    caplog.set_level(logging.NOTICE)
    configuration._violations.append(
        {"kind": "unknown", "file": "/etc/debops/conf.d/custom.yml",
         "option": "myscript", "dropped": False,
         "message": "unknown option 'myscript'"})
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=NotADirectoryError("nope")))
    interpreter = make_interpreter(config=configuration)

    interpreter.do_config_check(make_args(project_dir=".", strict=False))

    assert "The DebOps configuration is valid" in caplog.text


def test_config_check_strict_fails_on_unknown_options(configuration,
                                                      monkeypatch):
    configuration._violations.append(
        {"kind": "unknown", "file": "/etc/debops/conf.d/custom.yml",
         "option": "myscript", "dropped": False,
         "message": "unknown option 'myscript'"})
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=NotADirectoryError("nope")))
    interpreter = make_interpreter(config=configuration)

    with pytest.raises(SystemExit) as excinfo:
        interpreter.do_config_check(make_args(project_dir=".",
                                              strict=True))

    assert excinfo.value.code == 1


def test_project_refresh_reports_a_failure(monkeypatch, capsys):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=ValueError("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_project_refresh(make_args(project_dir=".",
                                                 view="system"))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().err


@pytest.mark.parametrize("exception", [
    IsADirectoryError, NotADirectoryError, PermissionError,
    ChildProcessError])
def test_project_lock_reports_a_project_failure(monkeypatch, capsys,
                                                exception):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=exception("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_project_lock(make_args(project_dir=".", view="system"))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().err


def test_project_unlock_reports_a_missing_default_view(monkeypatch, capsys):
    project = mock.Mock()
    project.unlock.side_effect = NoDefaultViewException("no view")
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_project_unlock(make_args(project_dir=".",
                                                view="system"))

    assert caught.value.code == 1
    assert "Error: no view" in capsys.readouterr().err


@pytest.mark.parametrize("exception", [
    IsADirectoryError, NotADirectoryError, PermissionError,
    ChildProcessError])
def test_project_unlock_reports_a_project_failure(monkeypatch, capsys,
                                                  exception):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=exception("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_project_unlock(make_args(project_dir=".",
                                                view="system"))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().err


def test_project_mkview_reports_a_failure(monkeypatch, capsys):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=ValueError("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_project_mkview(make_args(
            project_dir=".", new_view="webservers", encrypt=None, keys=None))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().err


def test_project_commit_reports_a_failure(monkeypatch, capsys):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=PermissionError("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_project_commit(make_args(project_dir="."))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().err


@pytest.mark.parametrize("exception", [IsADirectoryError, NotADirectoryError])
def test_exec_reports_a_project_failure(monkeypatch, capsys, exception):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=exception("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_exec(make_args(project_dir=".", view="system",
                                      eval=False, bell=False,
                                      accept=False))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().err


@pytest.mark.parametrize("exception", [
    IsADirectoryError, NotADirectoryError, ChildProcessError])
def test_run_reports_a_project_failure(monkeypatch, capsys, exception):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=exception("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_run(make_args(project_dir=".", view="system",
                                     eval=False, bell=False,
                                     accept=False))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().err


@pytest.mark.parametrize("exception", [
    NoDefaultViewException, ValueError, FileNotFoundError,
    ChildProcessError])
def test_run_reports_a_runner_failure(monkeypatch, capsys, exception):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    monkeypatch.setattr(cli_module, "AnsiblePlaybookRunner",
                        mock.Mock(side_effect=exception("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_run(make_args(project_dir=".", view="system",
                                     eval=False, bell=False,
                                     accept=False,
                                     ansible_args=["site.yml"],
                                     debug=False))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().err


def test_run_eval_mode_delegates_to_the_runner(monkeypatch):
    project = mock.Mock()
    runner = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    monkeypatch.setattr(cli_module, "AnsiblePlaybookRunner",
                        mock.Mock(return_value=runner))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_run(make_args(project_dir=".", view="system",
                                     eval=True, bell=False,
                                     accept=False,
                                     ansible_args=["site.yml"], debug=False))

    assert caught.value.code == 0
    runner.eval.assert_called_once_with()
    runner.execute.assert_not_called()


@pytest.mark.parametrize("exception", [IsADirectoryError, NotADirectoryError])
def test_env_reports_a_project_failure(monkeypatch, capsys, exception):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=exception("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_env(make_args(project_dir=".", view="system",
                                     command_args=[], scope="local"))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().err


@pytest.mark.parametrize("exception", [
    NoDefaultViewException, ValueError, FileNotFoundError])
def test_env_reports_a_runner_failure(monkeypatch, capsys, exception):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    monkeypatch.setattr(cli_module, "EnvRunner",
                        mock.Mock(side_effect=exception("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_env(make_args(project_dir=".", view="system",
                                     command_args=[], scope="local"))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().err


def test_config_get_names_the_undefined_option(monkeypatch, capsys):
    """An undefined option exits non-zero and names the option: a
    mistyped key -- or an option consumed as one -- must not fail
    silently."""
    from debops.core.exceptions import OptionNotFoundError
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter()
    interpreter.config.config_get.side_effect = OptionNotFoundError(
        "not defined")

    args = make_args(project_dir=".", key=["tofu.mistyped"],
                     format=None, keys=False, root=False,
                     show_origin=False, show_scope=False)
    with pytest.raises(SystemExit):
        interpreter.do_config_get(args)

    err = capsys.readouterr().err
    assert "The option 'tofu.mistyped' is not defined" in err


def test_config_get_undefined_option_prints_empty_json(monkeypatch,
                                                       capsys):
    """The json consumers of the undefined-option path keep their
    contract: the empty object on stdout, no error on stderr, the
    non-zero exit."""
    from debops.core.exceptions import OptionNotFoundError
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter()
    interpreter.config.config_get.side_effect = OptionNotFoundError(
        "not defined")

    args = make_args(project_dir=".", key=["tofu.mistyped"],
                     format="json", keys=False, root=False,
                     show_origin=False, show_scope=False)
    with pytest.raises(SystemExit):
        interpreter.do_config_get(args)

    captured = capsys.readouterr()
    assert captured.out.strip() == "{}"
    assert captured.err == ""


def test_config_set_warns_when_the_value_is_shadowed(
        configuration, tmp_path, caplog, monkeypatch):
    """A file of the override directory which sorts after the managed
    one shadows the value 'debops config set' just wrote: the command
    names it, so the set does not fail silently."""
    directory = tmp_path / ".debops" / "conf.d"
    (directory / "override").mkdir(parents=True)
    (directory / "override" / "z-late.toml").write_text(
        "[syslog]\nport = 514\n")
    project = mock.Mock(path=str(tmp_path))
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    configuration.merge({"config": {
        "override_filename": "override/99_config_set.json"}})
    interpreter = make_interpreter(config=configuration)

    args = make_args(project_dir=str(tmp_path), key="syslog.port",
                     values=["514"], delete=False, type=None,
                     user=False)
    with caplog.at_level(logging.WARNING):
        interpreter.do_config_set(args)

    assert "shadowed by" in caplog.text
    assert "z-late.toml" in caplog.text


def test_config_set_is_silent_without_a_shadow(
        configuration, tmp_path, caplog, monkeypatch):
    """The set without a shadowing file stays silent: the warning
    fires only when another file actually wins."""
    project = mock.Mock(path=str(tmp_path))
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    configuration.merge({"config": {
        "override_filename": "override/99_config_set.json"}})
    interpreter = make_interpreter(config=configuration)

    args = make_args(project_dir=str(tmp_path), key="syslog.port",
                     values=["514"], delete=False, type=None,
                     user=False)
    with caplog.at_level(logging.WARNING):
        interpreter.do_config_set(args)

    assert "shadowed by" not in caplog.text


def test_project_init_creates_the_tofu_view(monkeypatch):
    """The '--tofu' option creates the OpenTofu view of the default
    view after the project is created: a fresh project open, the
    seeded dependency sets and the plain store when no encryption
    decision was made -- silently, the refusals belong to the
    existing projects and 'debops tofu mkview'."""
    project = mock.Mock()
    fresh = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=[project, fresh]))
    create_view = mock.Mock()
    monkeypatch.setattr(cli_module, "create_view", create_view)
    monkeypatch.setattr(cli_module, "resolve_providers",
                        mock.Mock(return_value=["lxc/incus"]))
    monkeypatch.setattr(cli_module, "resolve_modules",
                        mock.Mock(return_value={}))
    interpreter = make_interpreter()
    args = make_args(project_dir="/tmp/example", type="modern",
                     default_view="system", venv=False, requirements=True,
                     git=True, encrypt=None, keys=None, spec_sources=None,
                     allow_io=False, dry_run=False, force=False,
                     graph=False, list=False, host=None, ssh=False,
                     tofu=True, pre_commit=False)

    interpreter.do_project_init(args)

    assert cli_module.ProjectDir.call_args_list[1] == mock.call(
        path="/tmp/example", config=interpreter.config,
        cwd="/shell/cwd", view="system")
    create_view.assert_called_once_with(
        fresh, "system", providers=["lxc/incus"], modules={},
        encrypt="plain", keys=None)


def test_project_init_carries_the_encryption_decision(monkeypatch):
    """The '--encrypt' decision of the initialization carries over to
    the view's store: 'git-crypt' joins the repository-wide store
    with the '--keys' recipients, the '--tofu' option adds no
    encryption decision of its own."""
    project = mock.Mock()
    fresh = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=[project, fresh]))
    create_view = mock.Mock()
    monkeypatch.setattr(cli_module, "create_view", create_view)
    monkeypatch.setattr(cli_module, "resolve_providers", mock.Mock())
    monkeypatch.setattr(cli_module, "resolve_modules", mock.Mock())
    interpreter = make_interpreter()
    args = make_args(project_dir="/tmp/example", type="modern",
                     default_view="system", venv=False, requirements=True,
                     git=True, encrypt="git-crypt", keys="a@example.com",
                     spec_sources=None, allow_io=False, dry_run=False,
                     force=False, graph=False, list=False, host=None,
                     ssh=False, tofu=True, pre_commit=False)

    interpreter.do_project_init(args)

    create_view.assert_called_once_with(
        fresh, "system", providers=mock.ANY, modules=mock.ANY,
        encrypt="git-crypt", keys="a@example.com")


def test_project_init_refuses_the_failed_view_creation(
        monkeypatch, capsys):
    """A failed view creation fails the initialization: the operator
    explicitly asked for the view."""
    project = mock.Mock()
    fresh = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=[project, fresh]))
    monkeypatch.setattr(cli_module, "create_view",
                        mock.Mock(side_effect=ValueError(
                            "the view 'system' already exists")))
    monkeypatch.setattr(cli_module, "resolve_providers", mock.Mock())
    monkeypatch.setattr(cli_module, "resolve_modules", mock.Mock())
    interpreter = make_interpreter()
    args = make_args(project_dir="/tmp/example", type="modern",
                     default_view="system", venv=False, requirements=True,
                     git=True, encrypt="git-crypt", keys=None,
                     spec_sources=None, allow_io=False, dry_run=False,
                     force=False, graph=False, list=False, host=None,
                     ssh=False, tofu=True, pre_commit=False)

    with pytest.raises(SystemExit) as exc:
        interpreter.do_project_init(args)

    assert exc.value.code == 1
    assert 'already exists' in capsys.readouterr().err


def test_project_init_installs_the_pre_commit_hook(monkeypatch, caplog,
                                                   capsys):
    """The '--pre-commit' option runs 'pre-commit install' in the
    project directory; the tool's own output reports the hook path."""
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    result = mock.Mock(returncode=0,
                       stdout="pre-commit installed at .git/hooks/pre-commit\n",
                       stderr="")
    run = mock.Mock(return_value=result)
    monkeypatch.setattr(cli_module.subprocess, "run", run)
    interpreter = make_interpreter()
    args = make_args(project_dir="/tmp/example", type="modern",
                     default_view="system", venv=False, requirements=True,
                     git=True, encrypt=None, keys=None, spec_sources=None,
                     allow_io=False, dry_run=False, force=False,
                     graph=False, list=False, host=None, ssh=False,
                     tofu=False, pre_commit=True)

    with caplog.at_level(logging.INFO):
        interpreter.do_project_init(args)

    run.assert_called_once_with(["pre-commit", "install"],
                                cwd="/tmp/example",
                                capture_output=True, text=True)
    assert '.git/hooks/pre-commit' in capsys.readouterr().out
    assert 'installed' in caplog.text


def test_project_init_skips_the_hook_without_the_tool(monkeypatch, caplog):
    """A missing 'pre-commit' binary notices and skips: the hook
    engages when the operator installs the tool and runs the install
    by hand."""
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    run = mock.Mock(side_effect=FileNotFoundError("pre-commit"))
    monkeypatch.setattr(cli_module.subprocess, "run", run)
    interpreter = make_interpreter()
    args = make_args(project_dir="/tmp/example", type="modern",
                     default_view="system", venv=False, requirements=True,
                     git=True, encrypt=None, keys=None, spec_sources=None,
                     allow_io=False, dry_run=False, force=False,
                     graph=False, list=False, host=None, ssh=False,
                     tofu=False, pre_commit=True)

    with caplog.at_level(logging.INFO):
        interpreter.do_project_init(args)

    run.assert_called_once()
    assert 'not on the PATH' in caplog.text


def test_project_init_skips_the_hook_without_the_git_repository(
        monkeypatch, caplog):
    """The '--no-git' option leaves no repository for the hook to
    attach to: the install is skipped with the way out named."""
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    run = mock.Mock()
    monkeypatch.setattr(cli_module.subprocess, "run", run)
    interpreter = make_interpreter()
    args = make_args(project_dir="/tmp/example", type="modern",
                     default_view="system", venv=False, requirements=True,
                     git=False, encrypt=None, keys=None, spec_sources=None,
                     allow_io=False, dry_run=False, force=False,
                     graph=False, list=False, host=None, ssh=False,
                     tofu=False, pre_commit=True)

    with caplog.at_level(logging.INFO):
        interpreter.do_project_init(args)

    run.assert_not_called()
    assert 'without a git repository' in caplog.text


def test_project_init_notices_the_failed_hook_install(monkeypatch, caplog):
    """A failed 'pre-commit install' reports the tool's output and
    skips: the initialization does not fail over the optional
    development tool."""
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    result = mock.Mock(returncode=1, stdout="", stderr="cyclic dependency\n")
    monkeypatch.setattr(cli_module.subprocess, "run",
                        mock.Mock(return_value=result))
    interpreter = make_interpreter()
    args = make_args(project_dir="/tmp/example", type="modern",
                     default_view="system", venv=False, requirements=True,
                     git=True, encrypt=None, keys=None, spec_sources=None,
                     allow_io=False, dry_run=False, force=False,
                     graph=False, list=False, host=None, ssh=False,
                     tofu=False, pre_commit=True)

    with caplog.at_level(logging.INFO):
        interpreter.do_project_init(args)

    assert 'cyclic dependency' in caplog.text


def test_checklist_commit_honors_the_commit_path_knob(tmp_path, state_home,
                                                      monkeypatch):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)

    interpreter = make_interpreter()
    interpreter.config.get.side_effect = lambda items: 'records/vault'
    project_stub = SimpleNamespace(path=str(project), commit=mock.Mock())
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project_stub))
    args = make_args(project_dir=str(project), copy="web", close=False,
                     edit=False)
    interpreter.do_checklist_commit(args)

    records = list((project / "records" / "vault" / "audit" / "review" /
                    "_copies" / "web").glob("*.md"))
    assert len(records) == 1


def test_checklist_commit_refuses_vault_outside_project(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)

    interpreter = make_interpreter()
    interpreter.config.get.side_effect = lambda items: str(tmp_path / "elsewhere")
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project), copy="web", close=False,
                     edit=False)

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_commit(args)

    assert raised.value.code == 1
    assert "outside of the project" in capsys.readouterr().err
    assert not (tmp_path / "elsewhere").exists()


def test_checklist_commit_refuses_vault_escape(tmp_path, state_home,
                                               monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)

    interpreter = make_interpreter()
    interpreter.config.get.side_effect = lambda items: '../shared'
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project), copy="web", close=False,
                     edit=False)

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_commit(args)

    assert raised.value.code == 1
    assert "outside of the project" in capsys.readouterr().err


def test_checklist_commit_refuses_symlink_vault(tmp_path, state_home,
                                                monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)

    outside = tmp_path / "outside"
    outside.mkdir()
    (project / "vault").symlink_to(outside, target_is_directory=True)
    interpreter = make_interpreter()
    interpreter.config.get.side_effect = lambda items: 'vault'
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=SimpleNamespace(
                            path=str(project))))
    args = make_args(project_dir=str(project), copy="web", close=False,
                     edit=False)

    with pytest.raises(SystemExit) as raised:
        interpreter.do_checklist_commit(args)

    assert raised.value.code == 1
    assert "outside of the project" in capsys.readouterr().err


def test_checklist_commit_allows_vault_resolving_inside(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)

    interpreter = make_interpreter()
    interpreter.config.get.side_effect = lambda items: 'vault/../records'
    project_stub = SimpleNamespace(path=str(project), commit=mock.Mock())
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project_stub))
    args = make_args(project_dir=str(project), copy="web", close=False,
                     edit=False)
    interpreter.do_checklist_commit(args)

    records = list((project / "records" / "audit" / "review" /
                    "_copies" / "web").glob("*.md"))
    assert len(records) == 1
