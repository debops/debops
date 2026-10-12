# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import configparser
import datetime
import os
from unittest import mock

import pytest

import debops.ansibleplaybookrunner as runner_module
from debops.ansibleplaybookrunner import AnsiblePlaybookRunner


@pytest.fixture(autouse=True)
def stub_ansible_inventory(monkeypatch):
    monkeypatch.setattr(runner_module, "AnsibleInventory", mock.Mock())


@pytest.fixture(autouse=True)
def stub_logger_notice(monkeypatch):
    # debops.__main__ installs this on logging.Logger; importing the runner
    # alone does not, but the module relies on it.
    monkeypatch.setattr(runner_module.logger, "notice",
                        lambda *args, **kwargs: None,
                        raising=False)


class Friday(datetime.date):

    @classmethod
    def today(cls):
        return cls(2026, 10, 16)


def test_command_starts_with_ansible_playbook(stub_project):
    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=[])
    assert runner._ansible_command == ["ansible-playbook"]


def test_playbook_in_the_project_is_found(stub_project, tmp_path):
    (tmp_path / "ansible" / "playbooks").mkdir(parents=True)
    (tmp_path / "ansible" / "playbooks" / "site.yml").write_text("---\n")

    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=["site.yml"])

    assert runner._found_playbooks
    assert runner._found_playbooks[0].endswith(
        os.path.join("ansible", "playbooks", "site.yml"))


def test_missing_playbook_passes_the_name_through(stub_project):
    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=["site.yml"])
    assert runner._found_playbooks == ["site.yml"]


def test_playbook_extension_is_added(stub_project, tmp_path):
    (tmp_path / "ansible" / "playbooks").mkdir(parents=True)
    (tmp_path / "ansible" / "playbooks" / "site.yml").write_text("---\n")

    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=["site"])

    assert runner._found_playbooks
    assert runner._found_playbooks[0].endswith(
        os.path.join("ansible", "playbooks", "site.yml"))


def test_playbook_set_is_expanded(stub_project):
    project = stub_project()
    project.config.raw["views"] = {
        "system": {"playbook_sets": {"site": ["a.yml", "b.yml"]}}}

    runner = AnsiblePlaybookRunner(project, ansible_args=["site"])

    assert runner._found_playbooks == ["a.yml", "b.yml"]


def test_playbook_set_must_be_a_list(stub_project):
    project = stub_project()
    project.config.raw["views"] = {
        "system": {"playbook_sets": {"site": "a.yml"}}}

    with pytest.raises(ValueError):
        AnsiblePlaybookRunner(project, ansible_args=["site"])


def test_playbook_in_a_collection_is_found(stub_project, tmp_path):
    playbooks = (tmp_path / "ansible" / "collections"
                 / "ansible_collections" / "debops" / "debops" / "playbooks")
    playbooks.mkdir(parents=True)
    (playbooks / "site.yml").write_text("---\n")

    project = stub_project(collections=str(tmp_path / "ansible" / "collections"))
    runner = AnsiblePlaybookRunner(project,
                                   ansible_args=["debops.debops/site.yml"])

    assert runner._found_playbooks == [str(playbooks / "site.yml")]


def test_find_collections_discovers_collection_playbooks(stub_project,
                                                         tmp_path):
    playbooks = (tmp_path / "ansible" / "collections"
                 / "ansible_collections" / "debops" / "debops" / "playbooks")
    playbooks.mkdir(parents=True)

    project = stub_project(collections=str(tmp_path / "ansible" / "collections"))
    runner = AnsiblePlaybookRunner(project, ansible_args=[])

    assert "debops.debops" in runner._known_collections
    assert runner._known_collections["debops.debops"] == str(playbooks)


def test_read_only_friday_switches_to_check_mode(stub_project, monkeypatch):
    project = stub_project()
    project.config.raw["project"] = {"read_only_friday": True}
    monkeypatch.setattr(runner_module.datetime, "date", Friday)

    runner = AnsiblePlaybookRunner(project, ansible_args=["site.yml"])

    assert runner._ansible_command == ["ansible-playbook", "site.yml",
                                       "--diff", "--check"]


def test_read_only_friday_respects_existing_check_mode(stub_project,
                                                       monkeypatch):
    project = stub_project()
    project.config.raw["project"] = {"read_only_friday": True}
    monkeypatch.setattr(runner_module.datetime, "date", Friday)

    runner = AnsiblePlaybookRunner(project, ansible_args=["--check", "site.yml"])

    assert runner._ansible_command.count("--check") == 1


def test_get_check_mode_defaults_to_run(stub_project):
    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=["site.yml"])
    assert runner._get_check_mode() == "run"


def test_get_check_mode_detects_the_check_flag(stub_project):
    runner = AnsiblePlaybookRunner(stub_project(),
                                   ansible_args=["--check", "site.yml"])
    assert runner._get_check_mode() == "check"


def test_eval_prints_the_command(stub_project, capsys):
    runner = AnsiblePlaybookRunner(stub_project(),
                                   ansible_args=["--check", "site.yml"])
    runner.eval()

    output = capsys.readouterr().out
    assert "export ANSIBLE_CONFIG=" in output
    assert "ansible-playbook" in output


def test_execute_without_playbooks_aborts(stub_project, capsys):
    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=[])

    with pytest.raises(SystemExit) as exception:
        runner.execute()

    assert exception.value.code == 1
    assert "No playbooks specified" in capsys.readouterr().out


def test_execute_returns_the_command_return_code(stub_project, monkeypatch):
    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=["site.yml"])
    executor = mock.Mock(returncode=0)
    executor.communicate.return_value = (b"", b"")
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.inventory.unlock.return_value = False

    assert runner.execute() == 0


def test_execute_uses_the_run_hooks(stub_project, monkeypatch):
    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=["site.yml"])
    executor = mock.Mock(returncode=0)
    executor.communicate.return_value = (b"", b"")
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    hooks = mock.Mock(return_value=True)
    monkeypatch.setattr(runner_module, "run_hooks", hooks)
    runner.inventory.unlock.return_value = False

    runner.execute()

    assert [call.args[1] for call in hooks.call_args_list] == ["pre-run",
                                                               "post-run"]


def test_execute_uses_the_check_hooks_in_check_mode(stub_project, monkeypatch):
    runner = AnsiblePlaybookRunner(stub_project(),
                                   ansible_args=["--check", "site.yml"])
    executor = mock.Mock(returncode=0)
    executor.communicate.return_value = (b"", b"")
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    hooks = mock.Mock(return_value=True)
    monkeypatch.setattr(runner_module, "run_hooks", hooks)
    runner.inventory.unlock.return_value = False

    runner.execute()

    assert [call.args[1] for call in hooks.call_args_list] == ["pre-check",
                                                               "post-check"]


def test_execute_sets_the_environment(stub_project, monkeypatch):
    project = stub_project()
    runner = AnsiblePlaybookRunner(project, ansible_args=["site.yml"])
    monkeypatch.delenv("ANSIBLE_CONFIG", raising=False)
    executor = mock.Mock(returncode=0)
    executor.communicate.return_value = (b"", b"")
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.inventory.unlock.return_value = False

    runner.execute()

    assert os.environ["ANSIBLE_CONFIG"] == project.ansible_cfg.path


def test_execute_aborts_when_the_pre_hook_fails(stub_project, monkeypatch):
    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=["site.yml"])
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=False))

    with pytest.raises(RuntimeError):
        runner.execute()


def test_execute_locks_the_inventory_when_it_was_unlocked(stub_project,
                                                          monkeypatch):
    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=["site.yml"])
    executor = mock.Mock(returncode=0)
    executor.communicate.return_value = (b"", b"")
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.inventory.unlock.return_value = True

    runner.execute()

    runner.inventory.lock.assert_called_once_with()


def test_execute_handles_keyboard_interrupt(stub_project, monkeypatch):
    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=["site.yml"])
    executor = mock.Mock()
    executor.communicate.side_effect = KeyboardInterrupt
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.inventory.unlock.return_value = True

    with pytest.raises(SystemExit):
        runner.execute()

    assert runner.inventory.lock.called
