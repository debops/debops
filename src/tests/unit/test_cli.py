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

import pytest

import debops.cli as cli_module
from debops.cli import Interpreter
from debops.exceptions import NoDefaultViewException


def make_args(**kwargs):
    return SimpleNamespace(**kwargs)


def make_interpreter(config=None):
    interpreter = Interpreter.__new__(Interpreter)
    interpreter.args = None
    interpreter.config = (config if config is not None
                          else mock.Mock())
    interpreter.parsed_args = None
    return interpreter


def make_parsed(section, command, args):
    return SimpleNamespace(section=section, command=command, args=args)


@pytest.mark.parametrize("command", ["init", "refresh", "lock", "unlock",
                                     "mkview", "commit"])
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


@pytest.mark.parametrize("command", ["list", "get"])
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


def test_init_ignores_unknown_project_commands(monkeypatch):
    monkeypatch.setattr(cli_module, "Configuration",
                        mock.Mock(return_value=SimpleNamespace()))
    monkeypatch.setattr(cli_module, "Subcommands",
                        mock.Mock(return_value=make_parsed(
                            "project", "bogus", make_args())))
    command_methods = {name: mock.Mock() for name in
                       ("do_project_init", "do_project_refresh",
                        "do_project_lock", "do_project_unlock",
                        "do_project_mkview", "do_project_commit")}
    for name, method in command_methods.items():
        monkeypatch.setattr(cli_module.Interpreter, name, method)

    Interpreter(["debops"])

    for method in command_methods.values():
        method.assert_not_called()


def test_project_init_creates_the_project(monkeypatch):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter()
    args = make_args(project_dir="/tmp/example", type="legacy",
                     default_view="system")

    interpreter.do_project_init(args)

    cli_module.ProjectDir.assert_called_once_with(
        path="/tmp/example", config=interpreter.config, create=True,
        project_dir="/tmp/example", type="legacy", default_view="system")
    project.create.assert_called_once_with()


@pytest.mark.parametrize("exception", [
    IsADirectoryError, NotADirectoryError, PermissionError, ValueError])
def test_project_init_reports_a_failure(monkeypatch, capsys, exception):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=exception("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_project_init(make_args(
            project_dir="/tmp/example", type="legacy", default_view="system"))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().out


def test_project_refresh_refreshes_the_project(monkeypatch):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter()

    interpreter.do_project_refresh(make_args(project_dir=".", view="system"))

    project.refresh.assert_called_once_with()


def test_project_lock_locks_the_project(monkeypatch):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter()

    interpreter.do_project_lock(make_args(project_dir=".", view="system"))

    project.lock.assert_called_once_with()


def test_project_lock_ignores_a_missing_default_view(monkeypatch, capsys):
    project = mock.Mock()
    project.lock.side_effect = NoDefaultViewException("no view")
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_project_lock(make_args(project_dir=".", view="system"))

    assert caught.value.code == 1
    assert "Error: no view" in capsys.readouterr().out


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
        project_dir=".", new_view="webservers", encrypt=None, keys=None))

    project.mkview.assert_called_once_with(view="webservers")


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
    args = make_args(project_dir=".", view="system", eval=False, bell=True)

    with pytest.raises(SystemExit) as caught:
        interpreter.do_exec(args)

    assert caught.value.code == 3
    runner_type.assert_called_once_with(project, project_dir=".", view="system",
                                        eval=False, bell=True)
    runner.execute.assert_called_once_with()


def test_exec_prints_the_command_in_eval_mode(monkeypatch, capsys):
    project = mock.Mock()
    runner = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    monkeypatch.setattr(cli_module, "AnsibleRunner",
                        mock.Mock(return_value=runner))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_exec(make_args(project_dir=".", view="system",
                                      eval=True, bell=False))

    assert caught.value.code == 0
    runner.eval.assert_called_once_with()


@pytest.mark.parametrize("exception", [ValueError, FileNotFoundError])
def test_exec_reports_a_runner_failure(monkeypatch, capsys, exception):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    monkeypatch.setattr(cli_module, "AnsibleRunner",
                        mock.Mock(side_effect=exception("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_exec(make_args(project_dir=".", view="system",
                                      eval=False, bell=False))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().out


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
                                     eval=False, bell=False))

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
                                     eval=False, bell=False))

    assert caught.value.code == 1
    assert "Error: dirty working tree" in capsys.readouterr().out


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


def test_env_shows_the_environment_without_a_command(monkeypatch):
    project = mock.Mock()
    runner = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    monkeypatch.setattr(cli_module, "EnvRunner",
                        mock.Mock(return_value=runner))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit):
        interpreter.do_env(make_args(project_dir=".", view="system",
                                     command_args=[], scope="full"))

    runner.show_env.assert_called_once_with(scope="full")


def test_config_list_lists_the_configuration(monkeypatch):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter()

    interpreter.do_config_list(make_args(project_dir="."))

    interpreter.config.config_list.assert_called_once_with()


def test_config_list_works_outside_of_a_project(monkeypatch):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=IsADirectoryError("not a dir")))
    interpreter = make_interpreter()

    interpreter.do_config_list(make_args(project_dir="."))

    interpreter.config.config_list.assert_called_once_with()


def test_config_get_prints_the_requested_keys(monkeypatch):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter()
    args = make_args(project_dir=".", key=["project.name", "project.type"],
                     format="json", keys=True)

    interpreter.do_config_get(args)

    assert interpreter.config.config_get.call_count == 2
    interpreter.config.config_get.assert_any_call(
        "project.name", format="json", keys=True)
    interpreter.config.config_get.assert_any_call(
        "project.type", format="json", keys=True)


def test_config_get_prints_the_whole_configuration(monkeypatch):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=NotADirectoryError("nope")))
    interpreter = make_interpreter()

    interpreter.do_config_get(make_args(project_dir=".", key=None,
                                        format="unix", keys=False))

    interpreter.config.config_get.assert_called_once_with(
        ".", format="unix", keys=False)


def test_project_refresh_reports_a_failure(monkeypatch, capsys):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=ValueError("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_project_refresh(make_args(project_dir="."))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().out


def test_project_lock_reports_a_project_failure(monkeypatch, capsys):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=PermissionError("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_project_lock(make_args(project_dir=".", view="system"))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().out


def test_project_unlock_ignores_a_missing_default_view(monkeypatch, capsys):
    project = mock.Mock()
    project.unlock.side_effect = NoDefaultViewException("no view")
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_project_unlock(make_args(project_dir=".",
                                                view="system"))

    assert caught.value.code == 1
    assert "Error: no view" in capsys.readouterr().out


def test_project_unlock_reports_a_project_failure(monkeypatch, capsys):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=NotADirectoryError("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_project_unlock(make_args(project_dir=".",
                                                view="system"))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().out


def test_project_mkview_reports_a_failure(monkeypatch, capsys):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=ValueError("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_project_mkview(make_args(
            project_dir=".", new_view="webservers", encrypt=None, keys=None))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().out


def test_project_commit_reports_a_failure(monkeypatch, capsys):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=PermissionError("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_project_commit(make_args(project_dir="."))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().out


def test_exec_reports_a_project_failure(monkeypatch, capsys):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=IsADirectoryError("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_exec(make_args(project_dir=".", view="system",
                                      eval=False, bell=False))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().out


def test_run_reports_a_project_failure(monkeypatch, capsys):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=ChildProcessError("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_run(make_args(project_dir=".", view="system",
                                     eval=False, bell=False))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().out


def test_run_reports_a_runner_failure(monkeypatch, capsys):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    monkeypatch.setattr(cli_module, "AnsiblePlaybookRunner",
                        mock.Mock(side_effect=FileNotFoundError("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_run(make_args(project_dir=".", view="system",
                                     eval=False, bell=False))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().out


def test_run_prints_the_command_in_eval_mode(monkeypatch):
    project = mock.Mock()
    runner = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    monkeypatch.setattr(cli_module, "AnsiblePlaybookRunner",
                        mock.Mock(return_value=runner))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_run(make_args(project_dir=".", view="system",
                                     eval=True, bell=False))

    assert caught.value.code == 0
    runner.eval.assert_called_once_with()
    runner.execute.assert_not_called()


def test_env_reports_a_project_failure(monkeypatch, capsys):
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(side_effect=NotADirectoryError("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_env(make_args(project_dir=".", view="system",
                                     command_args=[], scope="local"))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().out


def test_env_reports_a_runner_failure(monkeypatch, capsys):
    project = mock.Mock()
    monkeypatch.setattr(cli_module, "ProjectDir",
                        mock.Mock(return_value=project))
    monkeypatch.setattr(cli_module, "EnvRunner",
                        mock.Mock(side_effect=ValueError("boom")))
    interpreter = make_interpreter()

    with pytest.raises(SystemExit) as caught:
        interpreter.do_env(make_args(project_dir=".", view="system",
                                     command_args=[], scope="local"))

    assert caught.value.code == 1
    assert "Error: boom" in capsys.readouterr().out
