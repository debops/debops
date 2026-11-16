# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for ``debops.core.ssh.scp``.

The external tools come from the shared ``fake_tools`` fixture; the
scp command builder only composes arguments, so its binary is a plain
path in the configuration.
"""

import logging

import pytest

from debops.core.ssh.scp import _uri_operand, build_scp_command, \
    split_operand, translate_ssh_args


def in_sequence(command, arguments):
    """Whether the argument run appears in the command."""
    length = len(arguments)
    return any(command[index:index + length] == arguments
               for index in range(len(command) + 1 - length))


@pytest.mark.parametrize("operand,user,host,path", [
    ("web:/tmp/file", None, "web", "/tmp/file"),
    ("root@web:/tmp/file", "root", "web", "/tmp/file"),
    ("[2001:db8::1]:/tmp/file", None, "2001:db8::1", "/tmp/file"),
    ("root@[2001:db8::1]:/tmp/file", "root", "2001:db8::1", "/tmp/file"),
    ("/tmp/local-file", None, None, "/tmp/local-file"),
    ("relative/path", None, None, "relative/path"),
    # A slash before the separating colon makes the operand local,
    # the way scp reads it: the name of the file carries a colon
    ("/tmp/backup-2026-11-16T00:10.tar", None, None,
     "/tmp/backup-2026-11-16T00:10.tar"),
    ("relative/path:with:colon", None, None, "relative/path:with:colon"),
])
def test_split_operand_covers_the_scp_grammar(operand, user, host, path):
    assert split_operand(operand) == (user, host, path)


@pytest.mark.parametrize("ssh_args,translated,dropped", [
    (["-J", "jump@bastion"], [("-o", "ProxyJump=jump@bastion")], []),
    (["-Jjump@bastion"], [("-o", "ProxyJump=jump@bastion")], []),
    (["-o", "ControlMaster=auto"], [("-o", "ControlMaster=auto")], []),
    (["-oControlMaster=auto"], [("-o", "ControlMaster=auto")], []),
    (["-L", "8080:localhost:80"], [], ["-L 8080:localhost:80"]),
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

    assert translated == [("-o", "ControlMaster=auto"),
                          ("-o", "ProxyJump=jump@bastion")]
    assert dropped == []


def make_project(stub_project, fake_tools, ssh_mode="user"):
    raw = {"binaries": dict(fake_tools["binaries"])}
    if ssh_mode:
        raw["ssh"] = {"known_hosts": ssh_mode}
    return stub_project(raw=raw)


def test_build_scp_command_resolves_both_sides(stub_project, fake_tools):
    project = make_project(stub_project, fake_tools)

    command = build_scp_command(project, ["web:/tmp/source"],
                                "web:/tmp/destination")

    assert command[0] == "/usr/bin/scp"
    assert command[-2:] == ["admin@192.0.2.10:/tmp/source",
                            "admin@192.0.2.10:/tmp/destination"]
    index = command.index("-P")
    assert command[index + 1] == "2222"


def test_build_scp_command_with_a_local_destination(stub_project,
                                                    fake_tools):
    project = make_project(stub_project, fake_tools)

    command = build_scp_command(project, ["web:/tmp/source"],
                                "/tmp/local-copy")

    assert command[-2:] == ["admin@192.0.2.10:/tmp/source", "/tmp/local-copy"]


def test_build_scp_command_translates_the_jump(stub_project, fake_tools):
    project = make_project(stub_project, fake_tools)

    command = build_scp_command(project, ["web:/tmp/source"],
                                "/tmp/local-copy")

    assert "ProxyCommand=ssh -W '[%h]:%p' jump@bastion" in command


def test_build_scp_command_adds_the_accept_option(stub_project,
                                                  fake_tools):
    project = make_project(stub_project, fake_tools)

    command = build_scp_command(project, ["web:/tmp/source"],
                                "/tmp/local-copy", accept=True)

    assert "StrictHostKeyChecking=accept-new" in command


def test_build_scp_command_declares_the_project_store(stub_project,
                                                      fake_tools):
    project = stub_project(
        cfg_options={"ssh_args": "-o UserKnownHostsFile=/store"},
        raw={"binaries": dict(fake_tools["binaries"]),
             "views": {"system": {"ssh": {"known_hosts": "project"}}}})

    command = build_scp_command(project, ["web:/tmp/source"],
                                "/tmp/local-copy")

    assert "-o" in command
    assert "UserKnownHostsFile=/store" in command


def test_build_scp_command_passes_the_operator_options(stub_project,
                                                       fake_tools):
    project = make_project(stub_project, fake_tools)

    command = build_scp_command(project, ["web:/tmp/source"],
                                "/tmp/local-copy",
                                scp_args=["-r", "-q"])

    assert "-r" in command and "-q" in command


TWO_HOST_INVENTORY = (
    "#!/bin/sh\n"
    'if [ "$1" = "--host" ]; then\n'
    'if [ "$2" = "web" ]; then\n'
    "    printf '%s' '{\"ansible_host\": \"192.0.2.10\","
    " \"ansible_port\": \"2222\", \"ansible_user\": \"admin\","
    " \"ansible_ssh_private_key_file\": \"/keys/web\"}'\n"
    'elif [ "$2" = "web2" ]; then\n'
    "    printf '%s' '{\"ansible_host\": \"192.0.2.11\","
    " \"ansible_port\": \"2223\", \"ansible_user\": \"admin2\","
    " \"ansible_ssh_private_key_file\": \"/keys/web2\"}'\n"
    "else\n"
    "    echo 'ERROR! no such host' >&2\n"
    "    exit 5\n"
    "fi\n"
    'elif [ "$1" = "--list" ]; then\n'
    'if [ "$3" = "web" ]; then\n'
    "    printf '%s' '{\"_meta\": {\"hostvars\": {\"web\": "
    "{\"ansible_host\": \"192.0.2.10\", \"ansible_port\": \"2222\","
    " \"ansible_user\": \"admin\","
    " \"ansible_ssh_private_key_file\": \"/keys/web\"}}}}'\n"
    'elif [ "$3" = "web2" ]; then\n'
    "    printf '%s' '{\"_meta\": {\"hostvars\": {\"web2\": "
    "{\"ansible_host\": \"192.0.2.11\", \"ansible_port\": \"2223\","
    " \"ansible_user\": \"admin2\","
    " \"ansible_ssh_private_key_file\": \"/keys/web2\"}}}}'\n"
    "else\n"
    "    printf '%s' '{\"_meta\": {\"hostvars\": {}}}'\n"
    "fi\n"
    "fi\n")


def two_host_project(stub_project, fake_tools, fake_binary):
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "two-host-inventory", TWO_HOST_INVENTORY)
    return stub_project(raw={"binaries": binaries})


def test_build_scp_command_composes_the_conflicting_ports_as_uris(
        stub_project, fake_tools, fake_binary):
    """Two operands which resolve to different ssh ports compose in
    the 'scp://' URI form, which carries a port per connection."""
    project = two_host_project(stub_project, fake_tools, fake_binary)

    command = build_scp_command(project, ["web:/src"], "web2:/dst")

    assert "-P" not in command
    assert "scp://admin@192.0.2.10:2222//src" in command
    assert "scp://admin2@192.0.2.11:2223//dst" in command


def test_build_scp_command_keeps_local_operands_plain_on_conflict(
        stub_project, fake_tools, fake_binary):
    """A local operand stays a local path when the remote operands
    carry their own ports."""
    project = two_host_project(stub_project, fake_tools, fake_binary)

    command = build_scp_command(project, ["/etc/hostname", "web:/src"],
                                "web2:/dst")

    assert "/etc/hostname" in command
    assert "scp://admin@192.0.2.10:2222//src" in command
    assert "scp://admin2@192.0.2.11:2223//dst" in command


def test_uri_operand_encodes_the_path_and_carries_the_parts():
    """The URI operand percent-encodes the path, brackets the IPv6
    authority and addresses the absolute paths behind a double
    slash."""
    assert _uri_operand(None, "web", "2222", "/tmp/with space") == \
        "scp://web:2222//tmp/with%20space"
    assert _uri_operand("admin", "2001:db8::1", None, "relative/dir") == \
        "scp://admin@[2001:db8::1]/relative/dir"
    assert _uri_operand("admin", "web", 22, "") == "scp://admin@web:22"


def test_build_scp_command_reports_the_differing_identities(
        stub_project, fake_tools, fake_binary):
    """Two operands which resolve to different private keys get no
    identity option."""
    project = two_host_project(stub_project, fake_tools, fake_binary)

    command = build_scp_command(project, ["web:/src"], "web2:/dst")

    assert "-i" not in command


def test_build_scp_command_uses_the_explicit_identity(
        stub_project, fake_tools, fake_binary):
    project = two_host_project(stub_project, fake_tools, fake_binary)

    command = build_scp_command(project, ["web:/src"], "web2:/dst",
                                identity="/keys/explicit")

    assert command[command.index("-i") + 1] == "/keys/explicit"


def test_build_scp_command_drops_the_forwards(stub_project, fake_tools,
                                              inventory_fake):
    """A forward configured for a host does not transfer to the file
    transfer connection."""
    inventory = inventory_fake(
        "forward-inventory",
        '{"ansible_host": "192.0.2.10",'
        ' "ansible_ssh_common_args": "-L 1234:localhost:5678"}')
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = inventory
    project = stub_project(raw={"binaries": binaries})

    command = build_scp_command(project, ["web:/src"], "web:/dst")

    assert "-L" not in command
    assert "1234:localhost:5678" not in command


def test_build_scp_command_copies_multiple_sources(stub_project, fake_tools):
    """Several sources compose in their written order, with the
    destination last, matching real scp."""
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    command = build_scp_command(project, ["web:/tmp/a", "web:/tmp/b"],
                                "local")

    assert command[-3:] == ["admin@192.0.2.10:/tmp/a",
                            "admin@192.0.2.10:/tmp/b", "local"]


def test_build_scp_command_keeps_option_values_with_spaces(
        stub_project, fake_tools, tmp_path):
    """Identity paths and store paths with spaces stay single argv
    elements; no quoting round-trip splits them."""
    identity = "/keys/with space/id"
    store = str(tmp_path / "known_hosts")
    project = stub_project(
        cfg_options={"ssh_args": "-o UserKnownHostsFile=" + store},
        raw={"binaries": dict(fake_tools["binaries"]),
             "views": {"system": {"ssh": {"known_hosts": "project"}}}})

    command = build_scp_command(project, ["web:/src"], "local",
                                identity=identity)

    assert command[command.index("-i") + 1] == identity
    assert any(store in token for token in command)


def test_translate_ssh_args_keeps_option_values_with_spaces():
    """A '-o' value with spaces (a ProxyCommand, for example) stays
    one argv element after the translation."""
    translated, dropped = translate_ssh_args(
        ["-o", "ProxyCommand=/bin/nc --option %h %p"])

    assert translated == [("-o", "ProxyCommand=/bin/nc --option %h %p")]
    assert dropped == []


def test_build_scp_command_refuses_an_undeclared_store(stub_project, fake_tools):
    """In project mode the transfers refuse to run when the view does
    not declare a store, the same way rescan does - silently falling
    back to the user's known_hosts would defeat the mode."""
    project = stub_project(raw={
        "binaries": dict(fake_tools["binaries"]),
        "views": {"system": {"ssh": {"known_hosts": "project"}}}})

    with pytest.raises(ValueError) as error:
        build_scp_command(project, ["web:/src"], "local")

    assert "does not declare a known_hosts store" in str(error.value)


def test_build_scp_command_uses_the_per_host_executable_and_extra_args(
        stub_project, fake_tools, inventory_fake):
    """ansible_scp_executable and ansible_scp_extra_args from the
    inventory shape the transfer command."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = inventory_fake(
        "transfer-inventory",
        '{"ansible_host": "192.0.2.10",'
        ' "ansible_scp_executable": "/usr/bin/scp-legacy",'
        ' "ansible_scp_extra_args": "-O"}')
    project = stub_project(raw={"binaries": binaries})

    command = build_scp_command(project, ["web:/src"], "local")

    assert command[0] == "/usr/bin/scp-legacy"
    assert "-O" in command


def test_build_scp_command_carries_the_resolved_ssh_args(
        stub_project, fake_tools, caplog):
    """The resolved 'ssh_args' reach the transfer: a jump host written
    there applies to the copy the way it applies to 'debops ssh' and
    to the Ansible transfers."""
    project = stub_project(
        raw={"binaries": dict(fake_tools["binaries"])},
        cfg_options={"ssh_args": "-J bastion@jump"})

    command = build_scp_command(project, ["/etc/hostname"], "web:/tmp/x")

    assert in_sequence(command, ["-o", "ProxyCommand=ssh "
                                 "-W '[%h]:%p' bastion@jump"])


def test_build_scp_command_passes_the_transfer_flags_through(
        stub_project, fake_tools, caplog):
    """The compression flag of ssh is a flag of scp as well and passes
    through without a drop notice; a cluster of unknown flags is
    dropped with one."""
    with caplog.at_level(logging.NOTICE):
        project = stub_project(
            raw={"binaries": dict(fake_tools["binaries"])},
            cfg_options={"ssh_args": "-C"})

    command = build_scp_command(project, ["/etc/hostname"], "web:/tmp/x")

    assert "-C" in command
    assert not caplog.records

    project = stub_project(
        raw={"binaries": dict(fake_tools["binaries"])},
        cfg_options={"ssh_args": "-Cv"})

    with caplog.at_level(logging.NOTICE):
        command = build_scp_command(project, ["/etc/hostname"],
                                    "web:/tmp/x")

    assert "-C" not in command
    assert "were dropped" in caplog.text


def test_build_scp_command_carries_the_store_once(stub_project,
                                                  fake_tools,
                                                  fake_binary,
                                                  tmp_path):
    """The store of the view is injected first; the drop-in's own
    store declaration in 'ssh_args' is filtered out, so the command
    carries the store once."""
    store = str(tmp_path / ".debops" / "ssh" / "views" / "system" /
                "known_hosts")
    project = stub_project(
        raw={"binaries": dict(fake_tools["binaries"]),
             "views": {"system": {"ssh": {"known_hosts": "project"}}}},
        cfg_options={"ssh_args":
                     "-C -o ControlMaster=auto "
                     "-o UserKnownHostsFile=" + store})

    command = build_scp_command(project, ["/etc/hostname"], "web:/tmp/x")

    # The jump process carries the store inside the ProxyCommand as
    # well; the top-level declaration stays the only one
    assert sum(token.startswith("UserKnownHostsFile=")
               for token in command) == 1
    assert command[command.index("-o") + 1].startswith(
        "UserKnownHostsFile=")
    store_position = next(index
                          for index, token in enumerate(command)
                          if "UserKnownHostsFile=" in token)
    assert command.index("ControlMaster=auto") > store_position


def test_build_scp_command_leads_the_derived_options(stub_project,
                                                     fake_tools,
                                                     inventory_fake):
    """The store, the accept-new instruction and the port of the
    inventory precede the translated arguments: ssh applies the first
    obtained value, and the derived values must not be defeated by
    the view's ssh_args."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = inventory_fake(
        "hardened-inventory",
        '{"ansible_host": "192.0.2.10",'
        ' "ansible_port": 2222,'
        ' "ansible_ssh_args": "-o StrictHostKeyChecking=yes'
        ' -o Port=9999"}')
    project = stub_project(
        raw={"binaries": binaries,
             "views": {"system": {"ssh": {"known_hosts": "project"}}}},
        cfg_options={"ssh_args": "-o UserKnownHostsFile=/store"})

    command = build_scp_command(project, ["/etc/hostname"],
                                "web:/tmp/x", accept=True)

    accept_position = command.index("StrictHostKeyChecking=accept-new")
    assert "StrictHostKeyChecking=yes" in command
    assert accept_position < command.index("StrictHostKeyChecking=yes")
    assert in_sequence(command, ["-P", "2222"])
    # scp re-emits its own port after the forwarded options, so a
    # 'Port=' in the resolved arguments would win at connection time
    # regardless of the composed order; the resolved ports are
    # stripped and the inventory port is the port the transfer uses
    assert "Port=9999" not in command


def test_build_scp_command_strips_the_resolved_ports(stub_project,
                                                     fake_tools,
                                                     inventory_fake):
    """scp re-emits its own port after the options it forwards, so a
    'Port=' in the resolved arguments would win over the '-P' of the
    inventory regardless of the composed order; the resolved ports
    are stripped and the inventory port is the port the transfer
    uses."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = inventory_fake(
        "ported-args-inventory",
        '{"ansible_host": "192.0.2.10",'
        ' "ansible_port": 2222,'
        ' "ansible_ssh_args": "-o Port=9999"}')
    project = stub_project(raw={"binaries": binaries})

    command = build_scp_command(project, ["/etc/hostname"], "web:/tmp/x")

    assert in_sequence(command, ["-P", "2222"])
    assert "Port=9999" not in command
