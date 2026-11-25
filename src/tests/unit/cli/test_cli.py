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
import logging
import pytest

import debops.cli.interpreter as cli_module
from debops.cli.interpreter import Interpreter
from debops.core import checklists
from debops.core.exceptions import InventorySpecError, NoDefaultViewException


def make_args(**kwargs):
    return SimpleNamespace(**kwargs)


def make_interpreter(config=None):
    interpreter = Interpreter.__new__(Interpreter)
    interpreter.args = None
    interpreter.config = (config if config is not None
                          else mock.Mock())
    if config is None:
        # The default the shipped configuration carries; the commit
        # executor resolves the vault directory through it
        interpreter.config.get.return_value = 'vault/checklists'
    interpreter.parsed_args = None
    interpreter.cwd = "/shell/cwd"
    return interpreter


def make_parsed(section, command, args):
    return SimpleNamespace(section=section, command=command, args=args)


@pytest.fixture
def state_home(tmp_path, monkeypatch):
    """Pin the checklist state home to the test tree.

    The executors resolve the state home from the environment; without
    this pin they would write through to the real user state.
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
    assert "Opened audit/review" in capsys.readouterr().out
    assert "as copy" not in capsys.readouterr().out


def test_checklist_list_prints_condensed_entries(tmp_path, monkeypatch,
                                                 capsys):
    packaged = tmp_path / "packaged"
    source = packaged / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text('---\ntitle: "Review"\n---\n# Review\n- [ ] Check\n')
    monkeypatch.setattr(cli_module.checklists, "DEBOPS_PACKAGE_DATA",
                        str(packaged))
    interpreter = make_interpreter()
    args = make_args(project_dir=str(tmp_path), active=False, verbose=0)
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
    args = make_args(project_dir=str(tmp_path), active=False, verbose=1)
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
    args = make_args(project_dir=str(tmp_path), active=False, verbose=2)
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
    args = make_args(project_dir=str(project), active=False, verbose=0)
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
    args = make_args(project_dir=str(project), active=False, verbose=0)
    interpreter.do_checklist_list(args)

    assert capsys.readouterr().out == (
        "audit/review\n"
        "\u251c\u2500\u2500 cluster3\n"
        "\u2502   \u2514\u2500\u2500 host1 (1/1 done)\n"
        "\u2514\u2500\u2500 web1\n"
        "    \u251c\u2500\u2500 alpha (1/1 done)\n"
        "    \u2514\u2500\u2500 beta (1/1 done)\n")


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
    args = make_args(project_dir=str(project), active=True, verbose=0)
    interpreter.do_checklist_list(args)

    output = capsys.readouterr().out
    assert "debian/d...o-trixie" in output
    assert "(2026-11-25)" in output
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
    interpreter = make_interpreter()
    args = make_args(project_dir=str(project), active=True, verbose=0)
    interpreter.do_checklist_list(args)

    output = capsys.readouterr().out
    assert output == (
        "web    audit/review    (2026-11-25)    1/2 done\n")


def test_checklist_list_active_very_verbose_adds_the_origin(
        tmp_path, state_home, monkeypatch, capsys):
    project = tmp_path / "project"
    (project / ".debops").mkdir(parents=True)
    state = checklists.checklist_state_dir(project)
    source = tmp_path / "packaged" / "checklists" / "audit" / "review.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Review\n- [x] Check\n")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    interpreter = make_interpreter()
    args = make_args(project_dir=str(project), active=True, verbose=2)
    interpreter.do_checklist_list(args)

    output = capsys.readouterr().out
    assert output == (
        "web    audit/review    (2026-11-25)    1/1 done    [packaged]\n")


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
                    "web").glob("*.md"))
    assert len(records) == 1
    assert "not a git repository" in captured.err
    call = project_stub.commit.call_args
    assert call.kwargs["message"].startswith(
        "checklist: web audit/review (1/2 done")
    assert call.kwargs["paths"] == [str(records[0])]


def test_checklist_list_active_without_copies(state_home, tmp_path,
                                              capsys):
    interpreter = make_interpreter()
    args = make_args(project_dir=str(tmp_path), active=True, verbose=0)
    interpreter.do_checklist_list(args)

    assert capsys.readouterr().out == ""


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
    assert project_stub.commit.call_count == 1

    args_close = make_args(project_dir=str(project), copy="web",
                           close=True, edit=False)
    interpreter.do_checklist_commit(args_close)
    captured = capsys.readouterr()
    assert "No changes since the last commit" in captured.out
    assert not (state / "web").exists()
    assert project_stub.commit.call_count == 1


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
    assert "Still open" in capsys.readouterr().err
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


def test_checklist_close_needs_a_copy_or_all(capsys):
    with pytest.raises(SystemExit) as raised:
        cli_module.Subcommands(["debops", "checklist", "close"])
    assert raised.value.code == 2
    assert "needs a copy id" in capsys.readouterr().err


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
    interpreter.config.get.return_value = 'records/vault'
    project_stub = SimpleNamespace(path=str(project), commit=mock.Mock())
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project_stub))
    args = make_args(project_dir=str(project), copy="web", close=False,
                     edit=False)
    interpreter.do_checklist_commit(args)

    records = list((project / "records" / "vault" / "audit" /
                    "review" / "web").glob("*.md"))
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
    interpreter.config.get.return_value = str(tmp_path / "elsewhere")
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
    interpreter.config.get.return_value = '../shared'
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
    interpreter.config.get.return_value = 'vault'
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
    interpreter.config.get.return_value = 'vault/../records'
    project_stub = SimpleNamespace(path=str(project), commit=mock.Mock())
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project_stub))
    args = make_args(project_dir=str(project), copy="web", close=False,
                     edit=False)
    interpreter.do_checklist_commit(args)

    records = list((project / "records" / "audit" /
                    "review" / "web").glob("*.md"))
    assert len(records) == 1
