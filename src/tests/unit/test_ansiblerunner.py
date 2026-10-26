# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import configparser
import os
from unittest import mock

import pytest

import debops.ansiblerunner as runner_module
from debops.ansiblerunner import AnsibleRunner


@pytest.fixture(autouse=True)
def stub_ansible_inventory(monkeypatch):
    monkeypatch.setattr(runner_module, "AnsibleInventory", mock.Mock())


def test_command_starts_with_the_ansible_binary(stub_project):
    runner = AnsibleRunner(stub_project(), ansible_args=[])
    assert runner._ansible_command == ["ansible"]


def test_environment_points_at_the_ansible_config(stub_project):
    project = stub_project()
    runner = AnsibleRunner(project, ansible_args=[])
    assert runner._ansible_env == {"ANSIBLE_CONFIG": project.ansible_cfg.path}


def test_flags_without_arguments_are_kept_in_order(stub_project):
    runner = AnsibleRunner(stub_project(), ansible_args=["-v", "--diff", "all"])
    assert runner._ansible_command == ["ansible", "-v", "--diff", "all"]


def test_option_with_an_argument_is_kept_in_order(stub_project):
    runner = AnsibleRunner(stub_project(),
                           ansible_args=["--limit", "web", "all"])
    assert runner._ansible_command == ["ansible", "--limit", "web", "all"]


def test_option_followed_by_an_option_is_kept(stub_project):
    runner = AnsibleRunner(stub_project(),
                           ansible_args=["--limit", "--verbose", "all"])
    assert runner._ansible_command == ["ansible", "--limit", "--verbose", "all"]


def test_option_argument_with_spaces_is_quoted(stub_project):
    runner = AnsibleRunner(stub_project(), ansible_args=["--limit", "web srv"])
    assert runner._ansible_command == ["ansible", "--limit", '"web srv"']


def test_single_dash_option_is_not_taken_as_an_argument(stub_project):
    # '-x y' is an option, not the value of '--limit'
    runner = AnsibleRunner(stub_project(),
                           ansible_args=["--limit", "-x y", "all"])
    assert runner._ansible_command == ["ansible", "--limit", "-x y", "all"]


def test_double_dash_is_dropped(stub_project):
    runner = AnsibleRunner(stub_project(), ansible_args=["--", "all"])
    assert runner._ansible_command == ["ansible", "all"]


def test_quote_spaces_leaves_simple_strings_alone(stub_project):
    runner = AnsibleRunner(stub_project(), ansible_args=[])
    assert runner._quote_spaces("web") == "web"


def test_global_vars_are_added_as_extra_vars(stub_project, tmp_path):
    (tmp_path / "ansible" / "inventory").mkdir(parents=True)
    (tmp_path / "ansible" / "global-vars.yml").write_text("---\n")

    runner = AnsibleRunner(stub_project(), ansible_args=[])

    assert runner._ansible_command[0] == "ansible"
    assert runner._ansible_command[1] == "--extra-vars"
    assert runner._ansible_command[2].startswith("@")


def test_missing_inventory_means_no_extra_vars(stub_project):
    runner = AnsibleRunner(stub_project(), ansible_args=[])
    assert "--extra-vars" not in runner._ansible_command


def test_missing_ansible_cfg_is_reported(stub_project):
    project = stub_project(cfg_error=configparser.NoSectionError("defaults"))
    with pytest.raises(FileNotFoundError):
        AnsibleRunner(project, ansible_args=[])


def test_missing_defaults_section_in_an_existing_file(stub_project):
    project = stub_project(cfg_error=configparser.NoSectionError("defaults"))
    with open(project.ansible_cfg.path, "w") as handle:
        handle.write("[other]\n")

    with pytest.raises(ValueError):
        AnsibleRunner(project, ansible_args=[])


def test_missing_inventory_option_aborts(stub_project, capsys):
    project = stub_project(cfg_options={})
    with pytest.raises(SystemExit) as exception:
        AnsibleRunner(project, ansible_args=[])

    assert exception.value.code == 1
    assert "No inventory specified" in capsys.readouterr().out


def test_eval_prints_the_command(stub_project, capsys):
    runner = AnsibleRunner(stub_project(), ansible_args=["-v"])
    runner.eval()

    output = capsys.readouterr().out
    assert "export ANSIBLE_CONFIG=" in output
    assert "ansible -v" in output


def test_execute_returns_the_command_return_code(stub_project, monkeypatch):
    runner = AnsibleRunner(stub_project(), ansible_args=["all"])
    executor = mock.Mock()
    executor.communicate.return_value = (b"", b"")
    executor.returncode = 7
    popen = mock.Mock(return_value=executor)
    monkeypatch.setattr(runner_module.subprocess, "Popen", popen)
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.inventory.unlock.return_value = False

    assert runner.execute() == 7
    assert popen.call_args.kwargs["shell"] is True


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


def test_execute_sets_the_environment(stub_project, monkeypatch):
    """The runner exports its environment for the spawned Ansible process.

    The export writes the process environment directly, which would leak
    into every test which runs afterwards through the shared pytest
    environment; the patch isolates the writes and restores the original
    state afterwards.
    """
    project = stub_project()
    runner = AnsibleRunner(project, ansible_args=["all"])
    executor = mock.Mock(returncode=0)
    executor.communicate.return_value = (b"", b"")
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.inventory.unlock.return_value = False

    with mock.patch.dict(os.environ, clear=True):
        runner.execute()

        assert os.environ["ANSIBLE_CONFIG"] == project.ansible_cfg.path


def test_execute_rings_the_bell(stub_project, monkeypatch, capsys):
    runner = AnsibleRunner(stub_project(), ansible_args=["all"], bell=True)
    executor = mock.Mock(returncode=0)
    executor.communicate.return_value = (b"", b"")
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.inventory.unlock.return_value = False

    runner.execute()

    assert capsys.readouterr().out.count("\a") == 1


def test_execute_aborts_when_the_pre_hook_fails(stub_project, monkeypatch):
    runner = AnsibleRunner(stub_project(), ansible_args=["all"])
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=False))

    with pytest.raises(RuntimeError):
        runner.execute()


def test_execute_runs_post_hook_with_return_code(stub_project, monkeypatch):
    runner = AnsibleRunner(stub_project(), ansible_args=["all"])
    executor = mock.Mock(returncode=2)
    executor.communicate.return_value = (b"", b"")
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    hooks = mock.Mock(return_value=True)
    monkeypatch.setattr(runner_module, "run_hooks", hooks)
    runner.inventory.unlock.return_value = False

    runner.execute()

    assert [call.args[1] for call in hooks.call_args_list] == ["pre-exec",
                                                               "post-exec"]
    assert hooks.call_args.kwargs["extra_env"] == {"DEBOPS_RETURN_CODE": 2}


def test_execute_locks_the_inventory_when_it_was_unlocked(stub_project,
                                                          monkeypatch):
    runner = AnsibleRunner(stub_project(), ansible_args=["all"])
    executor = mock.Mock(returncode=0)
    executor.communicate.return_value = (b"", b"")
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.inventory.unlock.return_value = True

    runner.execute()

    runner.inventory.lock.assert_called_once_with()


def test_execute_handles_keyboard_interrupt(stub_project, monkeypatch):
    runner = AnsibleRunner(stub_project(), ansible_args=["all"])
    executor = mock.Mock()
    executor.communicate.side_effect = KeyboardInterrupt
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.inventory.unlock.return_value = True

    with pytest.raises(SystemExit):
        runner.execute()

    runner.inventory.lock.assert_called_once_with()
