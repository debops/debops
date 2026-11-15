# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for ``debops.core.ssh.sftp``.

The external tools come from the shared ``fake_tools`` fixture; the
sftp command builder only composes arguments, so its binary is a plain
path in the configuration.
"""

import logging

import pytest

from debops.core.ssh.sftp import build_sftp_command


def in_sftp_sequence(command, arguments):
    """Whether the argument run appears in the command."""
    length = len(arguments)
    return any(
        command[index:index + length] == arguments
        for index in range(len(command) + 1 - length))


def test_build_sftp_command_resolves_the_host(stub_project, fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    command = build_sftp_command(project, "web")

    assert command == [
        "/usr/bin/sftp",
        "-P", "2222",
        "-i", "/keys/web",
        "-o", "ProxyJump=jump@bastion",
        "-o", "Foo=1",
        "admin@192.0.2.10",
    ]


def test_build_sftp_command_keeps_the_start_path(stub_project, fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    command = build_sftp_command(project, "root@web:/upload")

    assert "-P" in command and "2222" in command
    assert command[-1] == "root@192.0.2.10:/upload"
    assert "admin" not in command


def test_build_sftp_command_translates_the_jump(stub_project, fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    command = build_sftp_command(project, "web")

    assert "ProxyJump=jump@bastion" in command


def test_build_sftp_command_adds_the_accept_option(stub_project,
                                                   fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    command = build_sftp_command(project, "web", accept=True)

    assert "StrictHostKeyChecking=accept-new" in command


def test_build_sftp_command_omits_the_user_store(stub_project, fake_tools):
    """The user known_hosts mode leaves the store to ssh's own
    defaults; no option is injected."""
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    command = build_sftp_command(project, "web")

    assert not any("UserKnownHostsFile" in token for token in command)


def test_build_sftp_command_declares_the_project_store(stub_project,
                                                       fake_tools):
    project = stub_project(
        cfg_options={"ssh_args": "-o UserKnownHostsFile=/store"},
        raw={"binaries": dict(fake_tools["binaries"]),
             "views": {"system": {"ssh": {"known_hosts": "project"}}}})

    command = build_sftp_command(project, "web")

    assert "-o" in command
    assert "UserKnownHostsFile=/store" in command


def test_build_sftp_command_passes_the_operator_options(stub_project,
                                                        fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    command = build_sftp_command(project, "web", sftp_args=["-r"])

    assert "-r" in command


def test_build_sftp_command_drops_the_forwards(stub_project, fake_tools,
                                               fake_binary):
    """A forward configured for a host does not transfer to the file
    transfer session."""
    inventory = fake_binary(
        "forward-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"192.0.2.10\","
        " \"ansible_ssh_common_args\": \"-L 1234:localhost:5678\"}'\n")
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = inventory
    project = stub_project(raw={"binaries": binaries})

    command = build_sftp_command(project, "web")

    assert "-L" not in command
    assert "1234:localhost:5678" not in command


def test_build_sftp_command_keeps_option_values_with_spaces(
        stub_project, fake_tools, tmp_path):
    """A store path with spaces stays a single argv element; no
    quoting round-trip splits it."""
    store = str(tmp_path / "known hosts")
    project = stub_project(
        cfg_options={"ssh_args":
                     "-o 'UserKnownHostsFile=" + store + "'"},
        raw={"binaries": dict(fake_tools["binaries"]),
             "views": {"system": {"ssh": {"known_hosts": "project"}}}})

    command = build_sftp_command(project, "web")

    assert any(store in token for token in command)


def test_build_sftp_command_refuses_an_undeclared_store(stub_project, fake_tools):
    project = stub_project(raw={
        "binaries": dict(fake_tools["binaries"]),
        "views": {"system": {"ssh": {"known_hosts": "project"}}}})

    with pytest.raises(ValueError) as error:
        build_sftp_command(project, "web")

    assert "does not declare a known_hosts store" in str(error.value)


def test_build_sftp_command_carries_the_resolved_ssh_args(
        stub_project, fake_tools):
    """The resolved 'ssh_args' reach the session: a jump host written
    there applies to the session the way it applies to 'debops ssh'."""
    project = stub_project(
        raw={"binaries": dict(fake_tools["binaries"])},
        cfg_options={"ssh_args": "-J bastion@jump"})

    command = build_sftp_command(project, "web:/srv")

    assert in_sftp_sequence(command, ["-o", "ProxyJump=bastion@jump"])


def test_build_sftp_command_passes_the_transfer_flags_through(
        stub_project, fake_tools, caplog):
    """The compression flag of ssh is a flag of sftp as well and
    passes through without a drop notice."""
    with caplog.at_level(logging.NOTICE):
        project = stub_project(
            raw={"binaries": dict(fake_tools["binaries"])},
            cfg_options={"ssh_args": "-C"})

    command = build_sftp_command(project, "web:/srv")

    assert "-C" in command
    assert not caplog.records


def test_build_sftp_command_carries_the_store_once(stub_project,
                                                   fake_tools,
                                                   fake_binary,
                                                   tmp_path):
    """The store of the view is injected first; the drop-in's own
    store declaration in 'ssh_args' is filtered out."""
    store = str(tmp_path / ".debops" / "ssh" / "views" / "system" /
                "known_hosts")
    project = stub_project(
        raw={"binaries": dict(fake_tools["binaries"]),
             "views": {"system": {"ssh": {"known_hosts": "project"}}}},
        cfg_options={"ssh_args":
                     "-o ControlMaster=auto "
                     "-o UserKnownHostsFile=" + store})

    command = build_sftp_command(project, "web:/srv")

    assert sum("UserKnownHostsFile=" in token
               for token in command) == 1
    assert command[command.index("-o") + 1].startswith(
        "UserKnownHostsFile=")
    store_position = next(index
                          for index, token in enumerate(command)
                          if "UserKnownHostsFile=" in token)
    assert command.index("ControlMaster=auto") > store_position
