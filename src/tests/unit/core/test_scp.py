# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for ``debops.core.ssh.scp``.

The external tools come from the shared ``fake_tools`` fixture; the
scp command builder only composes arguments, so its binary is a plain
path in the configuration.
"""

import pytest

from debops.core.ssh.scp import build_scp_command, split_operand, \
    translate_ssh_args


@pytest.mark.parametrize("operand,user,host,path", [
    ("web:/tmp/file", None, "web", "/tmp/file"),
    ("root@web:/tmp/file", "root", "web", "/tmp/file"),
    ("[2001:db8::1]:/tmp/file", None, "2001:db8::1", "/tmp/file"),
    ("root@[2001:db8::1]:/tmp/file", "root", "2001:db8::1", "/tmp/file"),
    ("/tmp/local-file", None, None, "/tmp/local-file"),
    ("relative/path", None, None, "relative/path"),
])
def test_split_operand_covers_the_scp_grammar(operand, user, host, path):
    assert split_operand(operand) == (user, host, path)


@pytest.mark.parametrize("ssh_args,translated,dropped", [
    (["-J", "jump@bastion"], ["-o ProxyJump=jump@bastion"], []),
    (["-Jjump@bastion"], ["-o ProxyJump=jump@bastion"], []),
    (["-o", "ControlMaster=auto"], ["-o ControlMaster=auto"], []),
    (["-oControlMaster=auto"], ["-oControlMaster=auto"], []),
    (["-L", "8080:localhost:80"], [], ["-L", "8080:localhost:80"]),
    (["-N"], [], ["-N"]),
    (["-J"], [], ["-J"]),
    (["-o"], [], ["-o"]),
])
def test_translate_ssh_args_translates_and_drops(ssh_args, translated,
                                                 dropped):
    assert translate_ssh_args(ssh_args) == (translated, dropped)


def test_translate_ssh_args_passes_strings_through_shlex():
    translated, dropped = translate_ssh_args(
        "-o ControlMaster=auto -J jump@bastion")

    assert translated == ["-o ControlMaster=auto",
                          "-o ProxyJump=jump@bastion"]
    assert dropped == []


def make_project(stub_project, fake_tools, ssh_mode="user"):
    raw = {"binaries": dict(fake_tools["binaries"])}
    if ssh_mode:
        raw["ssh"] = {"known_hosts": ssh_mode}
    return stub_project(raw=raw)


def test_build_scp_command_resolves_both_sides(stub_project, fake_tools):
    project = make_project(stub_project, fake_tools)

    command = build_scp_command(project, "web:/tmp/source",
                                "web:/tmp/destination")

    assert command[0] == "/usr/bin/scp"
    assert command[-2:] == ["admin@192.0.2.10:/tmp/source",
                            "admin@192.0.2.10:/tmp/destination"]
    index = command.index("-P")
    assert command[index + 1] == "2222"


def test_build_scp_command_with_a_local_destination(stub_project,
                                                    fake_tools):
    project = make_project(stub_project, fake_tools)

    command = build_scp_command(project, "web:/tmp/source",
                                "/tmp/local-copy")

    assert command[-2:] == ["admin@192.0.2.10:/tmp/source", "/tmp/local-copy"]


def test_build_scp_command_translates_the_jump(stub_project, fake_tools):
    project = make_project(stub_project, fake_tools)

    command = build_scp_command(project, "web:/tmp/source",
                                "/tmp/local-copy")

    assert "ProxyJump=jump@bastion" in command


def test_build_scp_command_adds_the_accept_option(stub_project,
                                                  fake_tools):
    project = make_project(stub_project, fake_tools)

    command = build_scp_command(project, "web:/tmp/source",
                                "/tmp/local-copy", accept=True)

    assert "StrictHostKeyChecking=accept-new" in command


def test_build_scp_command_declares_the_project_store(stub_project,
                                                      fake_tools):
    project = stub_project(
        cfg_options={"ssh_args": "-o UserKnownHostsFile=/store"},
        raw={"binaries": dict(fake_tools["binaries"]),
             "ssh": {"known_hosts": "project"}})

    command = build_scp_command(project, "web:/tmp/source",
                                "/tmp/local-copy")

    assert "-o" in command
    assert "UserKnownHostsFile=/store" in command


def test_build_scp_command_passes_the_operator_options(stub_project,
                                                       fake_tools):
    project = make_project(stub_project, fake_tools)

    command = build_scp_command(project, "web:/tmp/source",
                                "/tmp/local-copy",
                                scp_args=["-r", "-q"])

    assert "-r" in command and "-q" in command
