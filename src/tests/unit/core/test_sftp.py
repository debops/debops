# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for ``debops.core.ssh.sftp``.

The external tools come from the shared ``fake_tools`` fixture; the
sftp command builder only composes arguments, so its binary is a plain
path in the configuration.
"""

from debops.core.ssh.sftp import build_sftp_command


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
             "ssh": {"known_hosts": "project"}})

    command = build_sftp_command(project, "web")

    assert "-o" in command
    assert "UserKnownHostsFile=/store" in command


def test_build_sftp_command_passes_the_operator_options(stub_project,
                                                        fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    command = build_sftp_command(project, "web", sftp_args=["-r"])

    assert "-r" in command
