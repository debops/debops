# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

import configparser
import datetime
import logging
import os
from unittest import mock

import pytest

import debops.core.ansible.projectrunner as projectrunner_module
import debops.core.runner as runner_base_module
import debops.core.ansible.ansibleplaybookrunner as runner_module
from debops.core.ansible.ansibleplaybookrunner import AnsiblePlaybookRunner


@pytest.fixture(autouse=True)
def stub_project_secrets(monkeypatch):
    monkeypatch.setattr(runner_base_module, "SecretManager",
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


def test_playbook_in_a_collection_with_dots_is_found(stub_project, tmp_path):
    """The dot-separated name is the format ansible-playbook itself
    uses for collection playbooks."""
    playbooks = (tmp_path / "ansible" / "collections"
                 / "ansible_collections" / "debops" / "debops" / "playbooks")
    playbooks.mkdir(parents=True)
    (playbooks / "site.yml").write_text("---\n")

    project = stub_project(collections=str(tmp_path / "ansible" / "collections"))
    runner = AnsiblePlaybookRunner(project,
                                   ansible_args=["debops.debops.site"])

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


def test_read_only_friday_switches_to_check_mode(stub_project, monkeypatch,
                                                 capsys, caplog):
    project = stub_project()
    project.config.raw["project"] = {"read_only_friday": True}
    monkeypatch.setattr(runner_module.datetime, "date", Friday)

    with caplog.at_level(logging.NOTICE, logger="debops.notice"):
        runner = AnsiblePlaybookRunner(project, ansible_args=["site.yml"])

    assert runner._ansible_command == ["ansible-playbook", "site.yml",
                                       "--diff", "--check"]

    # The notice reaches the journal and the terminal by default
    # (routed to both handlers); the stdout stays reserved for the
    # generated Ansible command ('--eval' consumers)
    assert "Read-Only Friday" in caplog.text
    assert capsys.readouterr().out == ""


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


def test_eval_returns_the_command(stub_project):
    runner = AnsiblePlaybookRunner(stub_project(),
                                   ansible_args=["--check", "site.yml"])

    output = runner.eval()

    assert "export ANSIBLE_CONFIG=" in output
    assert "ansible-playbook" in output
    assert "site.yml" in output


def test_execute_without_playbooks_aborts(stub_project):
    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=[])

    with pytest.raises(ValueError, match="No playbooks specified"):
        runner.execute()


def test_execute_returns_the_command_return_code(stub_project, monkeypatch,
                                                 tmp_path):
    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=["site.yml"])
    executor = mock.Mock(returncode=0)
    executor.communicate.return_value = (b"", b"")
    popen = mock.Mock(return_value=executor)
    monkeypatch.setattr(runner_module.subprocess, "Popen", popen)
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.secrets.unlock.return_value = False

    assert runner.execute() == 0
    assert popen.call_args.kwargs["shell"] is True
    # The command runs in the project directory, not the caller's
    assert popen.call_args.kwargs["cwd"] == str(tmp_path)


def test_execute_uses_the_run_hooks(stub_project, monkeypatch):
    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=["site.yml"])
    executor = mock.Mock(returncode=0)
    executor.communicate.return_value = (b"", b"")
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    hooks = mock.Mock(return_value=True)
    monkeypatch.setattr(runner_module, "run_hooks", hooks)
    runner.secrets.unlock.return_value = False

    runner.execute()

    assert [call.args[1] for call in hooks.call_args_list] == ["pre-run",
                                                               "post-run"]
    assert hooks.call_args.kwargs["extra_env"] == {"DEBOPS_RETURN_CODE": 0}


def test_execute_uses_the_check_hooks_in_check_mode(stub_project, monkeypatch):
    runner = AnsiblePlaybookRunner(stub_project(),
                                   ansible_args=["--check", "site.yml"])
    executor = mock.Mock(returncode=0)
    executor.communicate.return_value = (b"", b"")
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    hooks = mock.Mock(return_value=True)
    monkeypatch.setattr(runner_module, "run_hooks", hooks)
    runner.secrets.unlock.return_value = False

    runner.execute()

    assert [call.args[1] for call in hooks.call_args_list] == ["pre-check",
                                                               "post-check"]


def test_execute_sets_the_environment(stub_project, monkeypatch):
    """The runner exports its environment for the spawned Ansible process.

    The export writes the process environment directly, which would leak
    into every test which runs afterwards through the shared pytest
    environment; the patch isolates the writes and restores the original
    state afterwards.
    """
    project = stub_project()
    runner = AnsiblePlaybookRunner(project, ansible_args=["site.yml"])
    executor = mock.Mock(returncode=0)
    executor.communicate.return_value = (b"", b"")
    popen = mock.Mock(return_value=executor)
    monkeypatch.setattr(runner_module.subprocess, "Popen", popen)
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.secrets.unlock.return_value = False

    with mock.patch.dict(os.environ, clear=True):
        runner.execute()

        env = popen.call_args.kwargs["env"]
        assert env["ANSIBLE_CONFIG"] == project.ansible_cfg.path


def test_execute_aborts_when_the_pre_hook_fails(stub_project, monkeypatch):
    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=["site.yml"])
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=False))

    with pytest.raises(ChildProcessError):
        runner.execute()


def test_execute_locks_the_inventory_when_it_was_unlocked(stub_project,
                                                          monkeypatch):
    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=["site.yml"])
    executor = mock.Mock(returncode=0)
    executor.communicate.return_value = (b"", b"")
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.secrets.unlock.return_value = True

    runner.execute()

    runner.secrets.lock.assert_called_once_with()


def test_execute_handles_keyboard_interrupt(stub_project, monkeypatch,
                                            caplog):
    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=["site.yml"])
    executor = mock.Mock()
    executor.communicate.side_effect = KeyboardInterrupt
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    monkeypatch.setattr(runner_module, "run_hooks", mock.Mock(return_value=True))
    runner.secrets.unlock.return_value = True

    with caplog.at_level(
            logging.NOTICE, logger="debops.core.ansible.ansibleplaybookrunner"):
        with pytest.raises(SystemExit):
            runner.execute()

    runner.secrets.lock.assert_called_once_with()
    assert "interrupted by user" in caplog.text


def test_missing_ansible_cfg_is_reported(stub_project):
    project = stub_project(cfg_error=configparser.NoSectionError("defaults"))

    with pytest.raises(FileNotFoundError):
        AnsiblePlaybookRunner(project, ansible_args=[])


def test_missing_defaults_section_in_an_existing_file(stub_project, caplog):
    project = stub_project(cfg_error=configparser.NoSectionError("defaults"))
    with open(project.ansible_cfg.path, "w") as handle:
        handle.write("[other]\n")

    with pytest.raises(ValueError):
        AnsiblePlaybookRunner(project, ansible_args=[])

    assert project.ansible_cfg.path in caplog.text


def test_missing_inventory_option_aborts(stub_project):
    project = stub_project(cfg_options={})

    with pytest.raises(ValueError, match="No inventory specified"):
        AnsiblePlaybookRunner(project, ansible_args=[])


def test_global_vars_are_added_as_extra_vars(stub_project, tmp_path):
    (tmp_path / "ansible" / "inventory").mkdir(parents=True)
    (tmp_path / "ansible" / "global-vars.yml").write_text("---\n")

    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=[])

    assert runner._ansible_command[0] == "ansible-playbook"
    index = runner._ansible_command.index("--extra-vars")
    assert runner._ansible_command[index + 1].startswith("@")


def test_option_with_an_argument_is_kept_in_order(stub_project):
    runner = AnsiblePlaybookRunner(stub_project(),
                                   ansible_args=["--limit", "web",
                                                 "site.yml"])

    assert runner._ansible_command[:3] == ["ansible-playbook", "--limit",
                                           "web"]
    assert runner._found_playbooks == ["site.yml"]


def test_option_followed_by_an_option_is_kept(stub_project):
    runner = AnsiblePlaybookRunner(stub_project(),
                                   ansible_args=["--limit", "--verbose",
                                                 "site.yml"])

    assert runner._ansible_command[:3] == ["ansible-playbook", "--limit",
                                           "--verbose"]
    assert runner._found_playbooks == ["site.yml"]


def test_option_argument_with_spaces_is_quoted(stub_project):
    runner = AnsiblePlaybookRunner(stub_project(),
                                   ansible_args=["-e", "a=b c", "site.yml"])

    assert '"a=b c"' in runner._ansible_command


def test_single_dash_option_is_not_taken_as_an_argument(stub_project):
    # '-x y' is an option, not the value of '--limit'
    runner = AnsiblePlaybookRunner(stub_project(),
                                   ansible_args=["site.yml", "--limit",
                                                 "-x y"])

    assert runner._ansible_command[-2:] == ["--limit", "-x y"]
    assert runner._found_playbooks == ["site.yml"]


def test_double_dash_is_dropped(stub_project):
    runner = AnsiblePlaybookRunner(stub_project(),
                                   ansible_args=["--", "site.yml"])

    assert "--" not in runner._ansible_command
    assert runner._found_playbooks == ["site.yml"]


def test_flags_without_arguments_are_kept_in_order(stub_project):
    runner = AnsiblePlaybookRunner(stub_project(),
                                   ansible_args=["-vvv", "--diff",
                                                 "site.yml"])

    assert runner._ansible_command[:3] == ["ansible-playbook", "-vvv",
                                           "--diff"]


def test_quote_spaces_leaves_simple_strings_alone(stub_project):
    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=[])
    assert runner._quote_spaces("web") == "web"


def test_get_check_mode_detects_the_short_flag(stub_project):
    runner = AnsiblePlaybookRunner(stub_project(),
                                   ansible_args=["-C", "site.yml"])

    assert runner._get_check_mode() == "check"


def test_playbook_found_relative_to_the_working_directory(stub_project,
                                                          tmp_path,
                                                          monkeypatch):
    (tmp_path / "local.yml").write_text("---\n")
    monkeypatch.chdir(tmp_path)

    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=["local.yml"])

    assert runner._found_playbooks == ["local.yml"]


def test_playbook_in_a_view_collection_is_found(stub_project, tmp_path):
    playbooks = (tmp_path / "ansible" / "collections" / "ansible_collections"
                 / "myns" / "mycoll" / "playbooks")
    playbooks.mkdir(parents=True)
    (playbooks / "deploy.yml").write_text("---\n")
    project = stub_project(
        collections=str(tmp_path / "ansible" / "collections"))
    project.config.raw["views"] = {
        "system": {"playbook_collections": ["myns.mycoll"]}}

    runner = AnsiblePlaybookRunner(project, ansible_args=["deploy.yml"])

    assert runner._found_playbooks == [str(playbooks / "deploy.yml")]


def test_collections_path_relative_to_the_view(stub_project, tmp_path,
                                               monkeypatch):
    view_collections = (tmp_path / "ansible" / "views" / "system"
                        / "collections")
    view_collections.mkdir(parents=True)
    project = stub_project(collections="collections")
    runner = AnsiblePlaybookRunner.__new__(AnsiblePlaybookRunner)
    seen = []
    monkeypatch.setattr(runner, "_walklevel",
                        lambda directory, level: seen.append(directory)
                        or iter(()))

    runner._find_collections(project)

    assert seen == [str(view_collections)]


def test_execute_returns_a_nonzero_code(stub_project, monkeypatch):
    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=["site.yml"])
    executor = mock.Mock(returncode=3)
    executor.communicate.return_value = (b"", b"")
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    monkeypatch.setattr(runner_module, "run_hooks",
                        mock.Mock(return_value=True))
    runner.secrets.unlock.return_value = False

    assert runner.execute() == 3


def test_execute_rings_the_bell(stub_project, monkeypatch, capsys):
    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=["site.yml"],
                                   bell=True)
    executor = mock.Mock(returncode=0)
    executor.communicate.return_value = (b"", b"")
    monkeypatch.setattr(runner_module.subprocess, "Popen",
                        mock.Mock(return_value=executor))
    monkeypatch.setattr(runner_module, "run_hooks",
                        mock.Mock(return_value=True))
    runner.secrets.unlock.return_value = False

    runner.execute()

    # The bell is a bare BEL on standard error: a log record would
    # append a newline and advance the line the bell leaves alone
    assert capsys.readouterr().err == "\a"


def test_execute_re_raises_a_failed_unlock(stub_project, monkeypatch):
    runner = AnsiblePlaybookRunner(stub_project(), ansible_args=["site.yml"])
    runner.secrets.unlock.side_effect = ChildProcessError("dirty tree")
    monkeypatch.setattr(runner_module, "run_hooks",
                        mock.Mock(return_value=True))

    with pytest.raises(ChildProcessError, match="dirty tree"):
        runner.execute()


def test_debug_mode_adds_verbosity_and_env(stub_project):
    runner = AnsiblePlaybookRunner(stub_project(), debug=True,
                                   ansible_args=[])
    runner.secrets = mock.Mock()

    assert "-vv" in runner._ansible_command
    assert runner._ansible_env["ANSIBLE_DEBUG"] == "true"
    assert runner._ansible_env["ANSIBLE_KEEP_REMOTE_FILES"] == "1"
