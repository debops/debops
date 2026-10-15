# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the command line parser in ``debops.subcommands``.

``Subcommands`` parses the whole command line in its constructor and stores
the resulting namespace in ``self.args``, so each test builds one and inspects
what the user would get.
"""

import os

import pytest

from debops.subcommands import Subcommands


def parse_cli(*argv):
    """Parse ``debops <argv>`` and return the completed Subcommands object."""
    return Subcommands(["debops", *argv])


def test_section_and_command_are_detected():
    subcommands = parse_cli("project", "init", "/tmp/example")

    assert subcommands.section == "project"
    assert subcommands.command == "init"


def test_unknown_section_exits_with_an_error(capsys):
    with pytest.raises(SystemExit) as exc:
        parse_cli("bogus")

    assert exc.value.code == 1
    assert "unrecognized section" in capsys.readouterr().out


def test_unknown_project_command_exits_with_an_error(capsys):
    with pytest.raises(SystemExit) as exc:
        parse_cli("project", "bogus")

    assert exc.value.code == 1
    assert "unrecognized command" in capsys.readouterr().out


def test_unknown_config_command_exits_with_an_error(capsys):
    with pytest.raises(SystemExit) as exc:
        parse_cli("config", "bogus")

    assert exc.value.code == 1
    assert "unrecognized command" in capsys.readouterr().out


def test_project_init_defaults():
    subcommands = parse_cli("project", "init", "/tmp/example")
    args = subcommands.args

    assert args.type == "legacy"
    assert args.default_view == "system"
    assert args.project_dir == "/tmp/example"
    # Both are enabled by default
    assert args.git is True
    assert args.requirements is True
    # The Python virtual environment is opt-in
    assert args.venv is False
    assert args.encrypt is None
    assert args.spec_sources is None
    assert args.dry_run is False


def test_project_init_disable_flags():
    subcommands = parse_cli("project", "init", "--no-git",
                            "--no-requirements", "/tmp/example")
    args = subcommands.args

    assert args.git is False
    assert args.requirements is False


def test_project_init_enables_the_virtual_environment():
    subcommands = parse_cli("project", "init", "-t", "modern", "--venv",
                            "/tmp/example")

    assert subcommands.args.venv is True


def test_project_init_accepts_all_options():
    subcommands = parse_cli(
        "project", "init", "-t", "modern", "-V", "webservers",
        "--encrypt", "git-crypt", "--keys", "A,B", "--template", "spec.yml",
        "--dry-run", "--force", "--allow-io", "/tmp/example")
    args = subcommands.args

    assert args.type == "modern"
    assert args.default_view == "webservers"
    assert args.encrypt == "git-crypt"
    assert args.keys == "A,B"
    assert args.spec_sources == ["spec.yml"]
    assert args.dry_run is True
    assert args.force is True
    assert args.allow_io is True


def test_project_init_collects_several_specifications():
    subcommands = parse_cli("project", "init", "--template", "first.yml",
                            "--template", "second.yml")
    args = subcommands.args

    assert args.spec_sources == ["first.yml", "second.yml"]


def test_project_init_rejects_an_unknown_type():
    with pytest.raises(SystemExit) as exc:
        parse_cli("project", "init", "-t", "bogus")

    assert exc.value.code == 2


def test_project_refresh_options():
    subcommands = parse_cli("project", "refresh", "-V", "webservers",
                            "--force", "/tmp/example")
    args = subcommands.args

    assert args.view == "webservers"
    assert args.force is True
    assert args.project_dir == "/tmp/example"


@pytest.mark.parametrize("command", ["lock", "unlock"])
def test_project_secret_commands_take_a_view(command):
    subcommands = parse_cli("project", command, "-V", "webservers",
                            "/tmp/example")

    assert subcommands.args.view == "webservers"
    assert subcommands.args.project_dir == "/tmp/example"


def test_project_mkview_options():
    subcommands = parse_cli("project", "mkview", "--encrypt", "encfs",
                            "--keys", "A", "newview")

    assert subcommands.args.new_view == "newview"
    assert subcommands.args.encrypt == "encfs"
    assert subcommands.args.keys == "A"


def test_project_commit_defaults_to_the_current_directory():
    subcommands = parse_cli("project", "commit")

    assert subcommands.args.project_dir == os.getcwd()


def test_project_venv_defaults():
    subcommands = parse_cli("project", "venv", "install", "/tmp/example")
    args = subcommands.args

    assert args.action == "install"
    assert args.scope == "all"
    assert args.project_dir == "/tmp/example"


def test_project_venv_defaults_to_the_current_directory():
    subcommands = parse_cli("project", "venv", "install")

    assert subcommands.args.project_dir == os.getcwd()


@pytest.mark.parametrize(("option", "scope"), [
    ("--python", "python"),
    ("--collections", "collections"),
    ("--all", "all"),
])
def test_project_venv_scope_options(option, scope):
    subcommands = parse_cli("project", "venv", "upgrade", option)

    assert subcommands.args.scope == scope


def test_project_venv_rejects_an_unknown_action():
    with pytest.raises(SystemExit) as exc:
        parse_cli("project", "venv", "bogus")

    assert exc.value.code == 2


def test_project_venv_enable():
    subcommands = parse_cli("project", "venv", "enable", "/tmp/example")
    args = subcommands.args

    assert args.action == "enable"
    assert args.scope == "all"
    assert args.project_dir == "/tmp/example"


@pytest.mark.parametrize("action", ["enable", "install", "upgrade",
                                    "recreate", "freeze"])
def test_project_venv_scope_options_on_all_actions(action):
    subcommands = parse_cli("project", "venv", action, "--python")

    assert subcommands.args.scope == "python"


def test_exec_captures_the_ansible_arguments():
    subcommands = parse_cli("exec", "-V", "webservers", "-E", "--eval",
                            "all", "-m", "ping")
    args = subcommands.args

    assert args.view == "webservers"
    assert args.bell is True
    assert args.eval is True
    assert args.ansible_args == ["all", "-m", "ping"]


def test_run_captures_several_playbooks():
    subcommands = parse_cli("run", "-V", "webservers", "site.yml",
                            "extra.yml", "--limit", "web")
    args = subcommands.args

    assert args.view == "webservers"
    assert args.ansible_args == ["site.yml", "extra.yml", "--limit", "web"]


def test_check_adds_the_check_mode_flags():
    subcommands = parse_cli("check", "site.yml")
    args = subcommands.args

    assert args.ansible_args == ["site.yml", "--diff", "--check"]


def test_check_adds_only_the_missing_flag():
    subcommands = parse_cli("check", "site.yml", "--diff")
    args = subcommands.args

    assert args.ansible_args == ["site.yml", "--diff", "--check"]


def test_check_does_not_duplicate_the_flags():
    subcommands = parse_cli("check", "site.yml", "--diff", "--check")
    args = subcommands.args

    assert args.ansible_args == ["site.yml", "--diff", "--check"]


def test_check_does_not_duplicate_the_short_flags():
    subcommands = parse_cli("check", "site.yml", "-D", "-C")
    args = subcommands.args

    assert args.ansible_args == ["site.yml", "-D", "-C"]


def test_env_defaults_to_the_local_scope():
    subcommands = parse_cli("env", "ls", "-l")
    args = subcommands.args

    assert args.scope == "local"
    assert args.command_args == ["ls", "-l"]


def test_env_accepts_the_full_scope():
    subcommands = parse_cli("env", "--scope", "full", "env")

    assert subcommands.args.scope == "full"


def test_config_list_defaults_to_the_current_directory():
    subcommands = parse_cli("config", "list")

    assert subcommands.args.project_dir == os.getcwd()


def test_config_get_defaults():
    subcommands = parse_cli("config", "get", "project.name")
    args = subcommands.args

    assert args.format == "unix"
    assert args.keys is False
    assert args.key == ["project.name"]


def test_config_get_keys_flag():
    subcommands = parse_cli("config", "get", "-k", "project")

    assert subcommands.args.keys is True


def test_config_get_format_choice():
    subcommands = parse_cli("config", "get", "--format", "json",
                            "project.name")

    assert subcommands.args.format == "json"
