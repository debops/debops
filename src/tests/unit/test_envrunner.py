# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import configparser
import os
from unittest import mock

import pytest

import debops.envrunner as runner_module
from debops.envrunner import EnvRunner


@pytest.fixture(autouse=True)
def stub_ansible_inventory(monkeypatch):
    monkeypatch.setattr(runner_module, "AnsibleInventory", mock.Mock())


def test_command_is_the_user_supplied_arguments(stub_project):
    runner = EnvRunner(stub_project(), command_args=["env"])
    assert runner._command == ["env"]


def test_missing_ansible_cfg_is_reported(stub_project):
    project = stub_project(cfg_error=configparser.NoSectionError("defaults"))
    with pytest.raises(FileNotFoundError):
        EnvRunner(project, command_args=["env"])


def test_missing_defaults_section_in_an_existing_file(stub_project):
    project = stub_project(cfg_error=configparser.NoSectionError("defaults"))
    with open(project.ansible_cfg.path, "w") as handle:
        handle.write("[other]\n")

    with pytest.raises(ValueError):
        EnvRunner(project, command_args=["env"])


def test_missing_inventory_option_aborts(stub_project, capsys):
    project = stub_project(cfg_options={})
    with pytest.raises(SystemExit) as exception:
        EnvRunner(project, command_args=["env"])

    assert exception.value.code == 1
    assert "No inventory specified" in capsys.readouterr().err


def test_show_env_local_prints_configured_variables(stub_project, capsys):
    project = stub_project(env_vars={"DEBOPS_PROJECT_VIEW": "system"})
    runner = EnvRunner(project, command_args=["env"])

    runner.show_env("local")

    assert capsys.readouterr().out.strip() == "DEBOPS_PROJECT_VIEW=system"


def test_show_env_full_prints_process_environment(stub_project, capsys,
                                                  monkeypatch):
    monkeypatch.setenv("DEBOPS_TEST_VARIABLE", "1")
    runner = EnvRunner(stub_project(), command_args=["env"])

    runner.show_env("full")

    assert "DEBOPS_TEST_VARIABLE=1" in capsys.readouterr().out


def test_execute_returns_the_command_return_code(stub_project, monkeypatch):
    runner = EnvRunner(stub_project(), command_args=["true"])
    executor = mock.Mock(returncode=3)
    executor.communicate.return_value = (b"", b"")
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.inventory.unlock.return_value = False

    assert runner.execute() == 3


def test_execute_sets_the_configured_environment(stub_project, monkeypatch):
    project = stub_project(env_vars={"DEBOPS_PROJECT_VIEW": "system"})
    runner = EnvRunner(project, command_args=["true"])
    monkeypatch.delenv("DEBOPS_PROJECT_VIEW", raising=False)
    executor = mock.Mock(returncode=0)
    executor.communicate.return_value = (b"", b"")
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.inventory.unlock.return_value = False

    runner.execute()

    assert os.environ["DEBOPS_PROJECT_VIEW"] == "system"


def test_execute_aborts_when_the_pre_hook_fails(stub_project, monkeypatch):
    runner = EnvRunner(stub_project(), command_args=["true"])
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=False))

    with pytest.raises(ChildProcessError):
        runner.execute()


def test_execute_runs_post_hook_with_return_code(stub_project, monkeypatch):
    runner = EnvRunner(stub_project(), command_args=["true"])
    executor = mock.Mock(returncode=4)
    executor.communicate.return_value = (b"", b"")
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    hooks = mock.Mock(return_value=True)
    monkeypatch.setattr(runner_module, "run_hooks", hooks)
    runner.inventory.unlock.return_value = False

    runner.execute()

    assert [call.args[1] for call in hooks.call_args_list] == ["pre-env",
                                                               "post-env"]
    assert hooks.call_args.kwargs["extra_env"] == {"DEBOPS_RETURN_CODE": 4}


def test_execute_locks_the_inventory_when_it_was_unlocked(stub_project,
                                                          monkeypatch):
    runner = EnvRunner(stub_project(), command_args=["true"])
    executor = mock.Mock(returncode=0)
    executor.communicate.return_value = (b"", b"")
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.inventory.unlock.return_value = True

    runner.execute()

    runner.inventory.lock.assert_called_once_with()


def test_execute_handles_keyboard_interrupt(stub_project, monkeypatch):
    runner = EnvRunner(stub_project(), command_args=["true"])
    executor = mock.Mock()
    executor.communicate.side_effect = KeyboardInterrupt
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.inventory.unlock.return_value = True

    with pytest.raises(SystemExit):
        runner.execute()

    assert runner.inventory.lock.called


def test_execute_handles_interrupt_without_unlocking(stub_project,
                                                     monkeypatch):
    runner = EnvRunner(stub_project(), command_args=["true"])
    executor = mock.Mock()
    executor.communicate.side_effect = KeyboardInterrupt
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.inventory.unlock.return_value = False

    with pytest.raises(SystemExit):
        runner.execute()

    runner.inventory.lock.assert_not_called()
