# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import configparser
import logging
import os
from unittest import mock

import pytest

import debops.core.ansible.projectrunner as projectrunner_module
import debops.core.envrunner as runner_module
from debops.core.envrunner import EnvRunner


@pytest.fixture(autouse=True)
def stub_ansible_inventory(monkeypatch):
    monkeypatch.setattr(projectrunner_module, "AnsibleInventory",
                        mock.Mock())


@pytest.fixture(autouse=True)
def _isolated_environment():
    """The runners write the process environment directly as they run, and
    the process environment is shared with every test which runs after
    them in the pytest process: leak instances of 'ANSIBLE_CONFIG' have
    broken integration tests in mysterious ways. The patch snapshots the
    environment before each test and restores it afterwards.
    """
    patcher = mock.patch.dict(os.environ)
    patcher.start()
    yield
    patcher.stop()


def test_command_is_the_user_supplied_arguments(stub_project):
    runner = EnvRunner(stub_project(), command_args=["env"])
    assert runner._command == ["env"]


def test_missing_ansible_cfg_is_reported(stub_project):
    project = stub_project(cfg_error=configparser.NoSectionError("defaults"))
    with pytest.raises(FileNotFoundError):
        EnvRunner(project, command_args=["env"])


def test_missing_defaults_section_in_an_existing_file(stub_project, caplog):
    project = stub_project(cfg_error=configparser.NoSectionError("defaults"))
    with open(project.ansible_cfg.path, "w") as handle:
        handle.write("[other]\n")

    with pytest.raises(ValueError):
        EnvRunner(project, command_args=["env"])

    assert project.ansible_cfg.path in caplog.text


def test_missing_inventory_option_aborts(stub_project):
    project = stub_project(cfg_options={})
    with pytest.raises(ValueError, match="No inventory specified"):
        EnvRunner(project, command_args=["env"])


def test_show_env_local_returns_configured_variables(stub_project,
                                                     monkeypatch):
    monkeypatch.setenv("DEBOPS_UNCONFIGURED", "1")
    project = stub_project(env_vars={"DEBOPS_PROJECT_VIEW": "system"})
    runner = EnvRunner(project, command_args=["env"])

    lines = runner.show_env("local")

    assert lines == ["DEBOPS_PROJECT_VIEW=system"]


def test_show_env_full_returns_the_process_environment(stub_project,
                                                       monkeypatch):
    monkeypatch.setenv("DEBOPS_TEST_VARIABLE", "1")
    runner = EnvRunner(stub_project(), command_args=["env"])

    lines = runner.show_env("full")

    assert "DEBOPS_TEST_VARIABLE=1" in lines


def test_execute_returns_the_command_return_code(stub_project, monkeypatch,
                                                 tmp_path):
    runner = EnvRunner(stub_project(), command_args=["true"])
    executor = mock.Mock(returncode=3)
    executor.communicate.return_value = (b"", b"")
    popen = mock.Mock(return_value=executor)
    monkeypatch.setattr(runner_module.subprocess, "Popen", popen)
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.inventory.unlock.return_value = False

    assert runner.execute() == 3
    # The command runs in the project directory, not the caller's
    assert popen.call_args.kwargs["cwd"] == str(tmp_path)
    assert popen.call_args.kwargs["shell"] is True


def test_execute_sets_the_configured_environment(stub_project, monkeypatch):
    project = stub_project(env_vars={"DEBOPS_PROJECT_VIEW": "system"})
    runner = EnvRunner(project, command_args=["true"])
    monkeypatch.delenv("DEBOPS_PROJECT_VIEW", raising=False)
    executor = mock.Mock(returncode=0)
    executor.communicate.return_value = (b"", b"")
    popen = mock.Mock(return_value=executor)
    monkeypatch.setattr(runner_module.subprocess, "Popen", popen)
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.inventory.unlock.return_value = False

    runner.execute()

    # The configured variable reaches the spawned command, not the
    # process environment
    env = popen.call_args.kwargs["env"]
    assert env["DEBOPS_PROJECT_VIEW"] == "system"
    assert "DEBOPS_PROJECT_VIEW" not in os.environ


def test_execute_aborts_when_the_pre_hook_fails(stub_project, monkeypatch):
    runner = EnvRunner(stub_project(), command_args=["true"])
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=False))

    with pytest.raises(ChildProcessError):
        runner.execute()


def test_execute_re_raises_a_failed_unlock(stub_project, monkeypatch):
    runner = EnvRunner(stub_project(), command_args=["true"])
    runner.inventory.unlock.side_effect = ChildProcessError("dirty tree")
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))

    with pytest.raises(ChildProcessError, match="dirty tree"):
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


def test_execute_handles_keyboard_interrupt(stub_project, monkeypatch,
                                            caplog):
    runner = EnvRunner(stub_project(), command_args=["true"])
    executor = mock.Mock()
    executor.communicate.side_effect = KeyboardInterrupt
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.inventory.unlock.return_value = True

    with caplog.at_level(logging.NOTICE, logger="debops.core.envrunner"):
        with pytest.raises(SystemExit):
            runner.execute()

    runner.inventory.lock.assert_called_once_with()
    assert "interrupted by user" in caplog.text


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
