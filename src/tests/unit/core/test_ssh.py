# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for ``debops.core.ssh``.

The external tools are fake executables in the temporary directory:
the 'ansible-inventory' fake answers with a fixed JSON host variable
document and reports unknown hosts the way the real binary does, the
'ssh-keygen' and 'ssh-keyscan' fakes log their arguments and emit a
fixed key line. The ssh command builder only composes arguments, so
its binary is a plain path in the configuration.
"""

import base64
import hashlib
import logging
import os
import socket
from unittest import mock

import pytest

import debops.core.ssh as ssh_module
from debops.core.ssh import (SCP_OPTIONS_WITH_VALUE, SFTP_OPTIONS_WITH_VALUE,
                             SSH_OPTIONS_WITH_VALUE,
                             build_handoff_command, build_ssh_command,
                             ensure_store_dir, host_identifiers,
                             known_hosts_mode, known_hosts_option,
                             known_hosts_store,
                             parse_config_stores, remove_command,
                             render_config_snippet,
                             rescan_actions, resolve_destination,
                             require_store, resolve_host, resolve_patterns,
                             rescan_hosts, scan_command, split_destination,
                             split_operand, without_known_hosts_options,
                             split_options_operands, translate_ssh_args,
                             value_options_of, write_config_snippet)


@pytest.mark.parametrize("destination,user,host,port", [
    ("web", None, "web", None),
    ("root@web", "root", "web", None),
    ("ssh://root@web:2222", "root", "web", "2222"),
    ("ssh://web", None, "web", None),
    ("ssh://root@[2001:db8::1]:22", "root", "2001:db8::1", "22"),
    ("ssh://[2001:db8::1]", None, "2001:db8::1", None),
    ("2001:db8::1", None, "2001:db8::1", None),
    ("127.0.0.1:22", None, "127.0.0.1:22", None),
])
def test_split_destination_covers_the_ssh_grammar(destination, user, host,
                                                  port):
    """The ssh destination grammar: '[user@]hostname' and the URI
    'ssh://[user@]hostname[:port]'. The forms ssh itself does not
    support -- the port on the plain destination -- pass through
    verbatim and fail the same way ssh fails on them."""
    assert split_destination(destination) == (user, host, port)


def in_sequence(command, arguments):
    """Whether the argument list appears as a contiguous run."""
    length = len(arguments)
    return any(command[index:index + length] == arguments
               for index in range(len(command) + 1 - length))


def test_known_hosts_mode_defaults_to_user(stub_project):
    assert known_hosts_mode(stub_project()) == "user"


def test_known_hosts_store_resolves_the_user_store(stub_project):
    assert known_hosts_store(stub_project()) == os.path.expanduser(
        "~/.ssh/known_hosts")


def test_known_hosts_store_reads_the_declared_project_store(
        stub_project, tmp_path):
    declared = str(tmp_path / ".debops" / "ssh" / "views" / "system" /
                   "known_hosts")
    project = stub_project(
        cfg_options={"ssh_args": "-o UserKnownHostsFile=" + declared},
        raw={"views": {"system": {"ssh": {"known_hosts":
                                          "project"}}}})

    assert known_hosts_store(project) == declared


def test_known_hosts_store_expands_the_tilde_of_the_declared_store(
        stub_project, monkeypatch):
    monkeypatch.setenv("HOME", "/home/operator")
    project = stub_project(
        cfg_options={
            "ssh_args": "-o UserKnownHostsFile=~/.ssh/project_store"},
        raw={"views": {"system": {"ssh": {"known_hosts":
                                          "project"}}}})

    assert known_hosts_store(project) == "/home/operator/.ssh/project_store"


def test_known_hosts_store_is_dormant_without_the_declaration(stub_project):
    project = stub_project(raw={"views": {"system": {"ssh": {
        "known_hosts": "project"}}}})

    assert known_hosts_store(project) is None


def test_resolve_host_returns_the_inventory_parameters(stub_project,
                                                       fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    parameters = resolve_host(project, "web")

    assert parameters["destination"] == "192.0.2.10"
    assert parameters["user"] == "admin"
    assert parameters["port"] == 2222
    assert parameters["identity"] == "/keys/web"
    assert parameters["common_args"] == "-J jump@bastion"
    assert parameters["extra_args"] == "-o Foo=1"


def test_resolve_host_reports_an_unknown_host(stub_project, fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    with pytest.raises(ValueError, match="Cannot resolve the host"):
        resolve_host(project, "no-such-host")


def test_build_ssh_command_prefers_the_explicit_options(
        stub_project, fake_tools):
    """The explicit options and the destination's own 'user@host' parts
    take precedence over the inventory values, the way ssh precedence
    works."""
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})
    parameters = resolve_host(project, "web")

    command = build_ssh_command(project, "web", parameters,
                                user="override", port=1022,
                                identity="/other/key")

    assert command == [
        "/usr/bin/ssh",
        "-l", "override",
        "-p", "1022",
        "-i", "/other/key",
        "-J", "jump@bastion",
        "-o", "Foo=1",
        "-o", "ConnectTimeout=10",
        "192.0.2.10",
    ]


def test_build_ssh_command_splits_the_user_at_destination(
        stub_project, fake_tools):
    """'user@host' in the destination overrides the inventory's
    ansible_user, the way the destination overrides -l in ssh."""
    user, host, port = split_destination("root@web")
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})
    parameters = resolve_host(project, host)

    command = build_ssh_command(project, host, parameters,
                                user=user or "override")

    assert command[:2] == ["/usr/bin/ssh", "-l"]
    assert "root" in command
    assert "admin" not in command


def test_build_ssh_command_falls_back_to_the_explicit_options(stub_project,
                                                              fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    command = build_ssh_command(project, "plain", parameters={},
                                user="operator", port=2200)

    assert command == ["/usr/bin/ssh", "-l", "operator", "-p", "2200",
                       "-o", "ConnectTimeout=10", "plain"]


def test_build_ssh_command_passes_the_connection_extras_through(
        stub_project, fake_tools):
    project = stub_project(
        raw={"binaries": dict(fake_tools["binaries"])},
        cfg_options={"ssh_args": "-o ControlMaster=auto"})
    parameters = resolve_host(project, "web")

    command = build_ssh_command(project, "web", parameters,
                                ssh_args=["ls", "-l", "/"])

    assert in_sequence(command, ["-o", "ControlMaster=auto"])
    assert in_sequence(command, ["-J", "jump@bastion"])
    assert in_sequence(command, ["-o", "Foo=1"])
    assert command[command.index("192.0.2.10"):] == \
        ["192.0.2.10", "ls", "-l", "/"]


def test_build_ssh_command_places_the_caller_arguments_like_ssh(
        stub_project, fake_tools):
    """The arguments after the host follow the destination, the way
    ssh itself places the remote command and its arguments. Without a
    user from the options or the inventory, no '-l' is composed: ssh
    picks the user from the operator's SSH client configuration."""
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    command = build_ssh_command(project, "web", parameters={},
                                ssh_args=["uptime"])

    assert command == ["/usr/bin/ssh", "-o", "ConnectTimeout=10",
                       "web", "uptime"]


def test_host_identifiers_expand_the_resolved_addresses(
        stub_project, fake_tools, monkeypatch):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})
    parameters = resolve_host(project, "web")

    def fake_getaddrinfo(name, *args, **kwargs):
        if name == "web":
            return [(2, 1, 6, "", ("192.0.2.10", 0)),
                    (2, 1, 6, "", ("192.0.2.10", 0))]
        if name == "192.0.2.10":
            raise socket.gaierror("no reverse DNS")
        raise AssertionError("unexpected name " + name)

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    assert host_identifiers(project, "web", parameters) == \
        [("192.0.2.10", True), ("web", True)]


def test_host_identifiers_keep_an_unresolvable_name(stub_project,
                                                    fake_tools,
                                                    monkeypatch):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    def fake_getaddrinfo(name, *args, **kwargs):
        raise socket.gaierror("no DNS")

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    assert host_identifiers(project, "lonely") == [("lonely", False)]


def test_scan_command_passes_the_port_of_the_host():
    """The scanner connects on the port the resolution defines."""
    command = scan_command({"ssh-keyscan": "keyscan"}, "web", port=2222,
                           timeout=10)

    assert command == ["keyscan", "-H", "-T", "10", "-p", "2222", "web"]


def test_scan_command_omits_the_port_when_none_is_defined():
    assert "-p" not in scan_command({"ssh-keyscan": "keyscan"}, "web",
                                    timeout=10)


def test_remove_command_qualifies_the_ported_identifiers():
    """The entries of a host on a non-default port carry the
    '[host]:port' form, and only the qualified identifier matches
    them for the removal."""
    command = remove_command({"ssh-keygen": "keygen"}, "web", "store",
                             port="2222")

    assert command == ["keygen", "-R", "[web]:2222", "-f", "store"]


def test_remove_command_keeps_the_bare_identifiers_of_the_default_port():
    command = remove_command({"ssh-keygen": "keygen"}, "web", "store",
                             port="22")

    assert command == ["keygen", "-R", "web", "-f", "store"]
    assert remove_command({"ssh-keygen": "keygen"}, "web", "store") == \
        ["keygen", "-R", "web", "-f", "store"]


def test_rescan_actions_qualify_the_ported_identifiers(
        stub_project, fake_tools, monkeypatch):
    """The actions carry the port forms of both tools, and the
    unresolvable names contribute removals without scans."""
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    def fake_getaddrinfo(name, *args, **kwargs):
        if name == "192.0.2.10":
            return [(2, 1, 6, "", ("192.0.2.10", 0))]
        raise socket.gaierror("no DNS")

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    actions, resolvable = rescan_actions(project, "web", "store")

    assert [phase for phase, argv in actions] == \
        ["remove", "remove", "scan"]
    assert in_sequence(actions[0][1], ["-R", "[web]:2222"])
    assert in_sequence(actions[1][1], ["-R", "[192.0.2.10]:2222"])
    assert in_sequence(actions[2][1], ["-p", "2222"])
    assert resolvable == ["192.0.2.10"]


def test_host_identifiers_exclude_link_local_addresses_from_the_scan(
        stub_project, fake_tools, monkeypatch):
    """A link-local address without the interface scope cannot be
    scanned; it stays a removal identifier. An address with the scope
    stays scannable."""
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})
    parameters = {"destination": "metronom"}

    def fake_getaddrinfo(name, *args, **kwargs):
        if name == "metronom":
            return [(2, 1, 6, "", ("fe80::e079:c1ff:fee5:fd61", 0)),
                    (2, 1, 6, "", ("2001:db8::1", 0))]
        raise AssertionError("unexpected name " + name)

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    assert host_identifiers(project, "metronom", parameters) == \
        [("fe80::e079:c1ff:fee5:fd61", False), ("2001:db8::1", True),
         ("metronom", True)]

    def fake_getaddrinfo_link_local_only(name, *args, **kwargs):
        if name == "metronom":
            return [(2, 1, 6, "", ("fe80::e079:c1ff:fee5:fd61", 0))]
        raise AssertionError("unexpected name " + name)

    monkeypatch.setattr(socket, "getaddrinfo",
                        fake_getaddrinfo_link_local_only)

    assert host_identifiers(project, "metronom", parameters) == \
        [("fe80::e079:c1ff:fee5:fd61", False), ("metronom", False)]


def test_rescan_hosts_removes_and_scans_the_identifiers(
        stub_project, fake_tools, tmp_path):
    store = str(tmp_path / "store" / "known_hosts")
    os.makedirs(os.path.dirname(store))
    with open(store, "w") as handle:
        handle.write("# stale entries live here\n")

    results = rescan_hosts(stub_project(raw={"binaries": dict(fake_tools["binaries"])}),
                           ["web"], store=store, dns_mode='no-dns')

    assert results == [("web", True, "")]
    assert os.path.exists(store)
    with open(store) as handle:
        assert "ssh-ed25519 AAAAfakekey" in handle.read()
    assert (os.stat(store).st_mode & 0o777) == 0o600
    with open(fake_tools["log"]) as handle:
        removals = handle.read().splitlines()
    assert any("-R [web]:2222" in line for line in removals)
    assert any("-R [192.0.2.10]:2222" in line for line in removals)


def test_rescan_hosts_reports_a_host_without_keys(stub_project, fake_tools,
                                                  tmp_path):
    store = str(tmp_path / "known_hosts")

    results = rescan_hosts(stub_project(raw={"binaries": dict(fake_tools["binaries"])}),
                           ["web", "dark"], store=store, dns_mode='no-dns')

    assert results[0] == ("web", True, "")
    assert results[1][:2] == ("dark", False)
    assert "no resolvable identifiers" in results[1][2]
    assert "dark" not in open(store).read()


def test_rescan_hosts_requires_a_store_in_the_project_mode(stub_project,
                                                           fake_tools):
    project = stub_project(raw={
        "binaries": dict(fake_tools["binaries"]),
        "views": {"system": {"ssh": {"known_hosts": "project"}}}})

    with pytest.raises(ValueError, match="does not declare"):
        rescan_hosts(project, ["web"])


def test_render_config_snippet_in_the_user_mode(stub_project):
    lines = render_config_snippet(stub_project())

    assert lines[0].startswith("# BEGIN debops ssh")
    assert lines[-1].startswith("# END debops ssh")
    assert not any(line.startswith("Host ") for line in lines)


def test_render_config_snippet_in_the_project_mode(stub_project):
    """The store path of the block is written the way the Ansible
    configuration and the ssh suite write it: unexpanded."""
    project = stub_project(
        cfg_options={"ssh_args":
                     "-o UserKnownHostsFile=~/.ssh/project_store"},
        raw={"views": {"system": {"ssh": {"known_hosts":
                                          "project"}}}})

    lines = render_config_snippet(project)

    assert "Host *" in lines
    assert ('    UserKnownHostsFile ~/.ssh/known_hosts '
            '~/.ssh/project_store') in lines


def test_write_config_snippet_appends_and_replaces(stub_project, tmp_path):
    config = tmp_path / "ssh_config"
    config.write_text("Host bastion\n    ForwardAgent yes\n")

    assert write_config_snippet(stub_project(), str(config)) is True
    content = config.read_text()
    assert "ForwardAgent yes" in content
    assert content.count("# BEGIN debops ssh managed block") == 1

    assert write_config_snippet(stub_project(), str(config)) is False
    assert content == config.read_text()


def test_write_config_snippet_creates_a_private_file(stub_project, tmp_path):
    config = tmp_path / "ssh_config"

    write_config_snippet(stub_project(), str(config))

    assert (os.stat(config).st_mode & 0o777) == 0o600


def test_ensure_store_dir_creates_the_chain_private(tmp_path):
    """The store directory chain is created with the 0700 mode of the
    real '~/.ssh'."""
    store = (tmp_path / ".debops" / "ssh" / "views" / "system" /
             "known_hosts")

    store_dir = ensure_store_dir(str(store))

    assert store_dir == str(tmp_path / ".debops" / "ssh" / "views" /
                            "system")
    for directory in (tmp_path / ".debops" / "ssh",
                      tmp_path / ".debops" / "ssh" / "views",
                      tmp_path / ".debops" / "ssh" / "views" / "system"):
        assert (os.stat(directory).st_mode & 0o777) == 0o700


def test_ensure_store_dir_tightens_an_open_chain(tmp_path):
    """Directories of an existing store which are open to the group
    or the others are tightened to 0700."""
    ssh_dir = tmp_path / ".debops" / "ssh" / "views" / "system"
    ssh_dir.mkdir(parents=True)
    os.chmod(tmp_path / ".debops" / "ssh", 0o755)
    os.chmod(tmp_path / ".debops" / "ssh" / "views", 0o755)
    os.chmod(ssh_dir, 0o755)

    ensure_store_dir(str(ssh_dir / "known_hosts"))

    for directory in (tmp_path / ".debops" / "ssh",
                      tmp_path / ".debops" / "ssh" / "views", ssh_dir):
        assert (os.stat(directory).st_mode & 0o777) == 0o700


def test_ensure_store_dir_keeps_stricter_modes(tmp_path):
    """A directory stricter than 0700 stays as the operator set it."""
    ssh_dir = tmp_path / ".debops" / "ssh" / "views" / "system"
    ssh_dir.mkdir(parents=True)
    os.chmod(ssh_dir, 0o500)

    ensure_store_dir(str(ssh_dir / "known_hosts"))

    assert (os.stat(ssh_dir).st_mode & 0o777) == 0o500


def test_ensure_store_dir_ensures_a_foreign_store_leaf(tmp_path):
    """A store outside of the '.debops/ssh' layout gets only its own
    directory ensured."""
    store = tmp_path / "elsewhere" / "known_hosts"

    ensure_store_dir(str(store))

    assert (os.stat(tmp_path / "elsewhere").st_mode & 0o777) == 0o700
    assert not (tmp_path / ".debops").exists()


def test_resolve_patterns_expands_the_inventory_patterns(stub_project,
                                                         fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    hosts, unmatched = resolve_patterns(project, ["multi"])

    assert hosts == ["web-1", "web-2"]
    assert unmatched == []


def test_resolve_patterns_unions_and_deduplicates(stub_project, fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    hosts, unmatched = resolve_patterns(project, ["multi", "solo", "multi"])

    assert hosts == ["web-1", "web-2", "web-3"]
    assert unmatched == []


def test_resolve_patterns_reports_the_unmatched(stub_project, fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    hosts, unmatched = resolve_patterns(project, ["none"])

    assert hosts == []
    assert unmatched == ["none"]


def test_resolve_patterns_reports_a_failing_expansion(stub_project,
                                                      fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    with pytest.raises(ValueError):
        resolve_patterns(project, ["broken"])


def test_resolve_destination_resolves_the_literal_host(stub_project,
                                                       fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    parameters = resolve_destination(project, "web")

    assert parameters["destination"] == "192.0.2.10"


def test_resolve_destination_rejects_the_pattern(stub_project, fake_tools):
    """'all' and the other patterns are not single-host destinations,
    even when they would match one host."""
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    with pytest.raises(ValueError) as error:
        resolve_destination(project, "solo")

    assert "inventory pattern" in str(error.value)


def test_resolve_destination_rejects_the_unknown_host(stub_project,
                                                      fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    with pytest.raises(ValueError) as error:
        resolve_destination(project, "no-such-host")

    assert "Cannot resolve the host" in str(error.value)


def test_split_options_operands_walk_the_options():
    options, operands, tail = split_options_operands(
        ["-o", "Foo=1", "-v", "host", "cmd"], SSH_OPTIONS_WITH_VALUE)

    assert options == ["-o", "Foo=1", "-v"]
    assert operands == ["host"]
    assert tail == ["cmd"]


def test_split_options_operands_handle_attached_values():
    options, operands, tail = split_options_operands(
        ["-oFoo=1", "host"], SSH_OPTIONS_WITH_VALUE)

    assert options == ["-oFoo=1"]
    assert operands == ["host"]
    assert tail == []


def test_split_options_operands_consume_the_cluster_values():
    """A cluster whose last letter takes a value consumes the next
    token; the letters after a value-taking letter are its attached
    value."""
    options, operands, _ = split_options_operands(
        ["-qL", "8080:host:port", "host"], SSH_OPTIONS_WITH_VALUE)

    assert options == ["-qL", "8080:host:port"]
    assert operands == ["host"]

    options, operands, _ = split_options_operands(
        ["-qL8080:host:port", "host"], SSH_OPTIONS_WITH_VALUE)

    assert options == ["-qL8080:host:port"]
    assert operands == ["host"]


def test_split_options_operands_end_the_options_at_the_marker():
    options, operands, tail = split_options_operands(
        ["--", "-weird", "rest"], SSH_OPTIONS_WITH_VALUE)

    assert options == []
    assert operands == ["-weird"]
    assert tail == ["rest"]


def test_split_options_operands_cover_all_the_operands():
    """Without 'stop_at_operand' the walk collects every operand, the
    way the multi-operand commands permute."""
    options, operands, tail = split_options_operands(
        ["src", "-O", "-P", "2222", "dst"], SCP_OPTIONS_WITH_VALUE,
        stop_at_operand=False)

    assert options == ["-O", "-P", "2222"]
    assert operands == ["src", "dst"]
    assert tail == []


def test_split_options_operands_consume_the_long_values():
    options, operands, _ = split_options_operands(
        ["--view", "system", "host"], SSH_OPTIONS_WITH_VALUE,
        ("--view",))

    assert options == ["--view", "system"]
    assert operands == ["host"]


def test_split_options_operands_leave_the_optional_value_alone():
    options, operands, _ = split_options_operands(
        ["-Q"], SSH_OPTIONS_WITH_VALUE)

    assert options == ["-Q"]
    assert operands == []


def test_split_options_operands_refuse_a_dangling_value():
    """An option which requires a value and finds none raises; left
    valueless, the command would consume an operand as the value."""
    with pytest.raises(ValueError, match="requires a value"):
        split_options_operands(["-o"], SSH_OPTIONS_WITH_VALUE)

    with pytest.raises(ValueError, match="requires a value"):
        split_options_operands(["src", "-F"], SCP_OPTIONS_WITH_VALUE,
                               stop_at_operand=False)


def test_split_options_operands_report_a_missing_operand():
    options, operands, tail = split_options_operands(
        ["-v"], SSH_OPTIONS_WITH_VALUE)

    assert options == ["-v"]
    assert operands == []
    assert tail == []


def test_split_options_operands_keep_the_sftp_batch_value():
    """The '-b' option of sftp takes a value; the batch file is not
    mistaken for the destination."""
    options, operands, tail = split_options_operands(
        ["-b", "/tmp/batch", "host"], SFTP_OPTIONS_WITH_VALUE)

    assert options == ["-b", "/tmp/batch"]
    assert operands == ["host"]
    assert tail == []


def test_build_handoff_command_passes_the_arguments(stub_project,
                                                    fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    command = build_handoff_command(project, "ssh", ["--help"])

    assert command == ["/usr/bin/ssh", "--help"]


def test_build_handoff_command_applies_the_own_options(stub_project,
                                                       fake_tools):
    """The identity and the accept-new option are the only options
    DebOps applies to the handoff invocation."""
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    command = build_handoff_command(project, "sftp",
                                    ["-b", "batch", "host"],
                                    identity="/keys/id", accept=True)

    assert command == ["/usr/bin/sftp", "-i", "/keys/id",
                       "-o", "StrictHostKeyChecking=accept-new",
                       "-b", "batch", "host"]


def test_build_ssh_command_adds_the_accept_option(stub_project,
                                                  fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})
    parameters = {"destination": "192.0.2.10"}

    command = build_ssh_command(project, "web", parameters, accept=True)

    assert "StrictHostKeyChecking=accept-new" in command
    assert command[-1] == "192.0.2.10"


def test_translate_ssh_args_drops_a_valueless_jump():
    """A '-J' at the end of the list has no destination to translate."""
    translated, dropped = translate_ssh_args(["-J"])

    assert translated == []
    assert dropped == ["-J"]


def test_resolve_host_reports_an_unrunnable_binary(stub_project):
    project = stub_project(raw={"binaries": {
        "ansible-inventory": "/nonexistent/inventory"}})

    with pytest.raises(ChildProcessError):
        resolve_host(project, "web")


def test_resolve_host_rejects_an_unusable_answer(stub_project, fake_binary):
    binary = fake_binary(
        "garbage-inventory", "#!/bin/sh\nprintf 'not json\\n'\n")
    project = stub_project(raw={"binaries": {"ansible-inventory": binary}})

    with pytest.raises(ValueError) as error:
        resolve_host(project, "web")

    assert "no usable host variables" in str(error.value)


def test_resolve_patterns_reports_an_unrunnable_binary(stub_project):
    project = stub_project(raw={"binaries": {
        "ansible": "/nonexistent/ansible"}})

    with pytest.raises(ChildProcessError):
        resolve_patterns(project, ["all"])


def test_resolve_patterns_skips_the_noise(stub_project, fake_tools,
                                          fake_binary):
    """Warning lines, blank lines and a trailing non-indented line do
    not become host names."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible"] = fake_binary(
        "noisy-ansible",
        "#!/bin/sh\n"
        "printf '[NOTE: cached]\\n'\n"
        "printf '\\n'\n"
        "printf 'hosts (2):\\n'\n"
        "printf '\\n'\n"
        "printf '    web-1\\n'\n"
        "printf '  web-2\\n'\n"
        "printf 'unrelated tail\\n'\n")
    project = stub_project(raw={"binaries": binaries})

    hosts, unmatched = resolve_patterns(project, ["group"])

    assert hosts == ["web-1", "web-2"]
    assert unmatched == []


def test_resolve_destination_rejects_the_multi_match(stub_project,
                                                     fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    with pytest.raises(ValueError) as error:
        resolve_destination(project, "multi")

    assert "matches 2 inventory hosts" in str(error.value)


def test_build_handoff_command_uses_the_configured_executable(
        stub_project, fake_tools):
    project = stub_project(
        cfg_options={"inventory": "ansible/inventory",
                     "ssh_executable": "/custom/ssh"},
        raw={"binaries": dict(fake_tools["binaries"])})

    command = build_handoff_command(project, "ssh", ["--help"])

    assert command == ["/custom/ssh", "--help"]


def test_rescan_hosts_reports_the_keygen_failure(stub_project, fake_tools,
                                                 fake_binary, tmp_path):
    binaries = dict(fake_tools["binaries"])
    binaries["ssh-keygen"] = fake_binary(
        "failing-keygen", "#!/bin/sh\necho 'boom' >&2\nexit 3\n")
    project = stub_project(raw={"binaries": binaries})
    store = tmp_path / "store"
    store.write_text("stale\n")

    results = rescan_hosts(project, ["web"], store=str(store),
                           phases=("remove",))

    host, succeeded, message = results[0]
    assert not succeeded
    assert "cannot remove" in message


def test_rescan_hosts_reports_the_scan_timeout(stub_project, fake_tools,
                                               fake_binary, tmp_path):
    binaries = dict(fake_tools["binaries"])
    binaries["ssh-keyscan"] = fake_binary(
        "slow-keyscan", "#!/bin/sh\nsleep 5\n")
    project = stub_project(raw={"binaries": binaries})
    store = tmp_path / "store"

    results = rescan_hosts(project, ["web"], store=str(store),
                           timeout=-5, phases=("scan",))

    host, succeeded, message = results[0]
    assert not succeeded
    assert "timed out" in message


def test_ensure_store_dir_refuses_to_escape_the_project(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    store = (project / ".debops" / "ssh" / "views" / "system"
             / ".." / ".." / ".." / ".." / ".." / ".." / "evil"
             / "known_hosts")

    with pytest.raises(ValueError) as error:
        ensure_store_dir(str(store), str(project))

    assert "outside of the project" in str(error.value)
    assert not (tmp_path / "evil").exists()


def test_ensure_store_dir_leaves_a_foreign_directory_alone(tmp_path):
    """A store outside of the project layout gets created if missing,
    but an existing directory keeps the permissions its owner set."""
    foreign = tmp_path / "elsewhere"
    foreign.mkdir()
    os.chmod(foreign, 0o755)

    ensure_store_dir(str(foreign / "known_hosts"))

    assert (os.stat(foreign).st_mode & 0o777) == 0o755


def test_render_config_snippet_rejects_a_multiline_store(stub_project):
    """The store value is written into '~/.ssh/config'; a value with
    embedded newlines could inject SSH directives into the operator's
    configuration."""
    project = stub_project(
        cfg_options={"ssh_args":
                     "-o 'UserKnownHostsFile=~/.ssh/store\n"
                     "ProxyCommand=evil'"},
        raw={"views": {"system": {"ssh": {"known_hosts":
                                          "project"}}}})

    with pytest.raises(ValueError):
        render_config_snippet(project)


FQDN = 'web.example.org'
FQDN_KEY_BLOB = base64.b64encode(b'\x21' * 32).decode('ascii')
FQDN_KEY_LINE = FQDN + ' ssh-ed25519 ' + FQDN_KEY_BLOB
FQDN_FINGERPRINT = hashlib.sha256(b'\x21' * 32).hexdigest()


def fqdn_project(stub_project, fake_tools, fake_binary):
    """A project whose inventory host has an FQDN address, so the DNS
    verification tier has a name to look up."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "fqdn-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"" + FQDN + "\","
        " \"ansible_ssh_private_key_file\": \"/keys/web\"}'\n")
    binaries["ssh-keyscan"] = fake_binary(
        "fqdn-keyscan",
        "#!/bin/sh\nprintf '%s\\n' \"$4 ssh-ed25519 "
        + FQDN_KEY_BLOB + "\"\n")
    return stub_project(raw={"binaries": binaries})


def stub_dns(monkeypatch, records, authenticated=True):
    """Make the rescan DNS lookups answer with the given records."""
    monkeypatch.setattr('socket.getaddrinfo',
                        lambda host, *args, **kwargs: [
                            (2, 1, 6, '', ('192.0.2.10', 0))])
    monkeypatch.setattr(ssh_module.ssh, 'lookup_sshfp',
                        lambda hostname: (authenticated, records))


def test_rescan_hosts_stores_keys_matching_sshfp(monkeypatch,
                                                 stub_project, fake_tools,
                                                 fake_binary, tmp_path):
    """Keys whose fingerprints match the SSHFP records are stored
    without confirmation."""
    project = fqdn_project(stub_project, fake_tools, fake_binary)
    stub_dns(monkeypatch, {(4, 2, FQDN_FINGERPRINT)}, authenticated=True)
    store = tmp_path / "store"

    results = rescan_hosts(project, ["web"], store=str(store),
                           phases=("scan",))

    host, succeeded, message = results[0]
    assert succeeded
    assert "SSHFP" in message
    assert FQDN_KEY_LINE in store.read_text()


def test_rescan_hosts_refuses_keys_contradicting_sshfp(monkeypatch,
                                                       stub_project,
                                                       fake_tools,
                                                       fake_binary,
                                                       tmp_path):
    """Keys which contradict the DNS answer are not stored, and the
    stored entries of the host stay untouched."""
    project = fqdn_project(stub_project, fake_tools, fake_binary)
    stub_dns(monkeypatch, {(4, 2, 'ff' * 32)}, authenticated=True)
    store = tmp_path / "store"
    store.write_text("old\n")

    results = rescan_hosts(project, ["web"], store=str(store),
                           phases=("scan",))

    host, succeeded, message = results[0]
    assert not succeeded
    assert "do not match the SSHFP records" in message
    assert store.read_text() == "old\n"


def test_rescan_hosts_falls_back_without_dns_records(monkeypatch,
                                                     stub_project,
                                                     fake_tools,
                                                     fake_binary,
                                                     tmp_path):
    """Without SSHFP records the keys are stored as scanned."""
    project = fqdn_project(stub_project, fake_tools, fake_binary)
    stub_dns(monkeypatch, set(), authenticated=True)
    store = tmp_path / "store"

    results = rescan_hosts(project, ["web"], store=str(store),
                           phases=("scan",))

    host, succeeded, message = results[0]
    assert succeeded
    assert "no SSHFP records" in message
    assert FQDN_KEY_LINE in store.read_text()


def test_rescan_hosts_asks_for_confirmation_when_configured(
        monkeypatch, stub_project, fake_tools, fake_binary, tmp_path):
    """The confirm callback sees the fingerprints in the ssh display
    form and decides whether the keys are stored."""
    project = fqdn_project(stub_project, fake_tools, fake_binary)
    stub_dns(monkeypatch, set(), authenticated=True)
    store = tmp_path / "store"
    calls = []

    def confirm(host, offered):
        calls.append((host, offered))
        return True

    results = rescan_hosts(project, ["web"], store=str(store),
                           phases=("scan",), confirm=confirm)

    assert results[0][1]
    assert calls == [("web", [("SHA256:" + base64.b64encode(
        bytes.fromhex(FQDN_FINGERPRINT)).decode('ascii').rstrip('='),
        'ssh-ed25519')])]
    assert FQDN_KEY_LINE in store.read_text()

    decline = rescan_hosts(project, ["web"], store=str(store),
                           phases=("scan",),
                           confirm=lambda host, offered: False)
    assert not decline[0][1]
    assert FQDN_KEY_LINE in store.read_text()


def test_rescan_hosts_dns_verify_requires_authentication(monkeypatch,
                                                         stub_project,
                                                         fake_tools,
                                                         fake_binary,
                                                         tmp_path):
    """The strict mode does not store keys from DNS answers which a
    DNSSEC-validating resolver did not authenticate."""
    project = fqdn_project(stub_project, fake_tools, fake_binary)
    stub_dns(monkeypatch, {(4, 2, FQDN_FINGERPRINT)}, authenticated=False)
    store = tmp_path / "store"
    store.write_text("old\n")

    results = rescan_hosts(project, ["web"], store=str(store),
                           phases=("scan",), dns_mode='dns-verify')

    host, succeeded, message = results[0]
    assert not succeeded
    assert "could not be verified through DNS" in message
    assert store.read_text() == "old\n"


def test_rescan_hosts_dns_verify_stores_authenticated_keys(
        monkeypatch, stub_project, fake_tools, fake_binary, tmp_path):
    project = fqdn_project(stub_project, fake_tools, fake_binary)
    stub_dns(monkeypatch, {(4, 2, FQDN_FINGERPRINT)}, authenticated=True)
    store = tmp_path / "store"

    results = rescan_hosts(project, ["web"], store=str(store),
                           phases=("scan",), dns_mode='dns-verify')

    assert results[0][1]
    assert FQDN_KEY_LINE in store.read_text()


def test_rescan_hosts_matches_sha1_records(monkeypatch, stub_project,
                                           fake_tools, fake_binary,
                                           tmp_path):
    """Zones which publish the SHA-1 fingerprint type verify against
    the SHA-1 digest of the scanned keys, the way ssh verifies
    SSHFP records."""
    project = fqdn_project(stub_project, fake_tools, fake_binary)
    sha1 = hashlib.sha1(b'\x21' * 32).hexdigest()
    stub_dns(monkeypatch, {(4, 1, sha1)}, authenticated=True)
    store = tmp_path / "store"

    results = rescan_hosts(project, ["web"], store=str(store),
                           phases=("scan",))

    host, succeeded, message = results[0]
    assert succeeded
    assert "SSHFP" in message
    assert FQDN_KEY_LINE in store.read_text()


def test_rescan_hosts_keeps_the_old_trust_when_the_operator_declines(
        monkeypatch, stub_project, fake_tools, fake_binary, tmp_path):
    """In the default phases the removal requires keys to store:
    declined keys keep the old trust instead of leaving the host
    without entries."""
    project = fqdn_project(stub_project, fake_tools, fake_binary)
    stub_dns(monkeypatch, set(), authenticated=True)
    store = tmp_path / "store"
    store.write_text("old\n")

    results = rescan_hosts(project, ["web"], store=str(store),
                           confirm=lambda host, offered: False)

    host, succeeded, message = results[0]
    assert not succeeded
    assert store.read_text() == "old\n"


def test_rescan_hosts_keeps_the_old_trust_when_sshfp_contradicts(
        monkeypatch, stub_project, fake_tools, fake_binary, tmp_path):
    """A contradicting DNS answer refuses the host and keeps its
    stored entries in the default phases."""
    project = fqdn_project(stub_project, fake_tools, fake_binary)
    stub_dns(monkeypatch, {(4, 2, 'ff' * 32)}, authenticated=True)
    store = tmp_path / "store"
    store.write_text("old\n")

    results = rescan_hosts(project, ["web"], store=str(store))

    host, succeeded, message = results[0]
    assert not succeeded
    assert store.read_text() == "old\n"


def test_rescan_hosts_keeps_the_old_trust_for_unfingerprintable_keys(
        stub_project, fake_tools, fake_binary, tmp_path):
    """Keys of the types without SSHFP algorithm numbers -- the FIDO
    key types among them -- refuse the host instead of replacing its
    trust with nothing."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "sk-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"192.0.2.10\"}'\n")
    binaries["ssh-keyscan"] = fake_binary(
        "sk-keyscan",
        "#!/bin/sh\n"
        "printf '%s\\n' '192.0.2.10 sk-ssh-ed25519@openssh.com "
        "AAAAfakekey'\n")
    project = stub_project(raw={"binaries": binaries})
    store = tmp_path / "store"
    store.write_text("old\n")

    results = rescan_hosts(project, ["web"], store=str(store))

    host, succeeded, message = results[0]
    assert not succeeded
    assert 'could not be fingerprinted' in message
    assert store.read_text() == "old\n"


def test_rescan_host_port_follows_the_resolution_chain(
        stub_project, fake_tools, fake_binary, monkeypatch):
    """The port follows the ssh connection plugin's 'port' option: the
    inventory variables over the 'ANSIBLE_REMOTE_PORT' environment
    over the 'remote_port' configuration option."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "portless-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"192.0.2.10\"}'\n")

    monkeypatch.delenv("ANSIBLE_REMOTE_PORT", raising=False)
    project = stub_project(raw={"binaries": binaries})
    assert resolve_host(project, "web")["port"] is None

    project = stub_project(raw={"binaries": binaries},
                           cfg_options={"remote_port": "2200"})
    assert resolve_host(project, "web")["port"] == "2200"

    monkeypatch.setenv("ANSIBLE_REMOTE_PORT", "2300")
    assert resolve_host(project, "web")["port"] == "2300"

    binaries["ansible-inventory"] = fake_binary(
        "ported-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"192.0.2.10\","
        " \"ansible_port\": 2222}'\n")
    project = stub_project(raw={"binaries": binaries})
    assert resolve_host(project, "web")["port"] == 2222


def test_rescan_hosts_stores_into_the_user_store(monkeypatch,
                                                 stub_project, fake_tools,
                                                 fake_binary, tmp_path):
    """In the user mode the store is '~/.ssh/known_hosts', outside of
    the project directory by design; the containment must not refuse
    it."""
    monkeypatch.setenv('HOME', str(tmp_path))
    binaries = dict(fake_tools["binaries"])
    binaries["ssh-keyscan"] = fake_binary(
        "user-keyscan",
        "#!/bin/sh\nprintf '%s\\n' '192.0.2.10 ssh-ed25519 "
        + FQDN_KEY_BLOB + "'\n")
    project = stub_project(raw={"binaries": binaries})

    results = rescan_hosts(project, ["web"], phases=("scan",),
                           dns_mode='no-dns')

    assert results[0][1]
    assert (tmp_path / ".ssh" / "known_hosts").read_text().strip()


def test_resolve_host_falls_back_to_the_remote_user_config(
        monkeypatch, stub_project, fake_tools, fake_binary):
    """With no user in the inventory, the remote_user option of the
    project configuration applies, matching Ansible's precedence."""
    monkeypatch.delenv('ANSIBLE_REMOTE_USER', raising=False)
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "userless-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"192.0.2.10\"}'\n")
    project = stub_project(
        cfg_options={"inventory": "ansible/inventory",
                     "remote_user": "configuser"},
        raw={"binaries": binaries})

    parameters = resolve_host(project, "web")

    assert parameters["user"] == "configuser"


def test_resolve_host_prefers_the_remote_user_environment(
        monkeypatch, stub_project, fake_tools, fake_binary):
    """ANSIBLE_REMOTE_USER overrides the remote_user configuration, as
    it does for Ansible itself."""
    monkeypatch.setenv('ANSIBLE_REMOTE_USER', 'envuser')
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "userless-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"192.0.2.10\"}'\n")
    project = stub_project(
        cfg_options={"inventory": "ansible/inventory",
                     "remote_user": "configuser"},
        raw={"binaries": binaries})

    parameters = resolve_host(project, "web")

    assert parameters["user"] == "envuser"


def test_resolve_host_prefers_the_inventory_user(monkeypatch,
                                                 stub_project, fake_tools):
    """The inventory's ansible_user wins over the configuration, the
    same way Ansible resolves it."""
    monkeypatch.setenv('ANSIBLE_REMOTE_USER', 'envuser')
    project = stub_project(
        cfg_options={"inventory": "ansible/inventory",
                     "remote_user": "configuser"},
        raw={"binaries": dict(fake_tools["binaries"])})

    parameters = resolve_host(project, "web")

    assert parameters["user"] == "admin"


def test_resolve_host_rejects_option_like_destinations(
        monkeypatch, stub_project, fake_tools, fake_binary):
    """An ansible_host which begins with a dash would be parsed by ssh
    as an option instead of a host; the resolution refuses it."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "option-host-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"-oProxyCommand=evil\"}'\n")
    project = stub_project(raw={"binaries": binaries})

    with pytest.raises(ValueError) as error:
        resolve_host(project, "web")

    assert "looks like an SSH option" in str(error.value)


def test_build_ssh_command_refuses_an_undeclared_store(stub_project):
    """In project mode the connect command refuses to run when the
    view does not declare a store, like the transfers and rescan."""
    project = stub_project(raw={
        "binaries": {"ssh": "/usr/bin/ssh"},
        "views": {"system": {"ssh": {"known_hosts": "project"}}}})
    parameters = {"destination": "192.0.2.10"}

    with pytest.raises(ValueError) as error:
        build_ssh_command(project, "web", parameters)

    assert "does not declare a known_hosts store" in str(error.value)


def test_value_options_of_derives_the_value_taking_options():
    """The walk's option sets are derived from the parser itself, so
    adding a value option to the parser teaches the walk without
    hand-maintained sets."""
    import argparse

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-V', '--view', help='the view')
    parser.add_argument('-a', '--accept', action='store_true')
    parser.add_argument('-v', '--verbose', action='count')
    parser.add_argument('--project-dir', nargs='?')

    shorts, longs = value_options_of(parser, passthrough={'o'})

    assert shorts == {'o', 'V'}
    assert longs == ['--view', '--project-dir']


def test_write_config_snippet_amends_the_store_list(stub_project,
                                                    fake_tools, tmp_path):
    """Writing from a second project appends its store to the list
    instead of overwriting the first project's entry, and the user's
    own store stays the first entry."""
    config = tmp_path / "ssh_config"
    project_a = stub_project(
        cfg_options={"ssh_args":
                     "-o UserKnownHostsFile="
                     "~/src/a/.debops/ssh/views/system/"
                     "known_hosts"},
        raw={"views": {"system": {"ssh": {"known_hosts": "project"}}}})
    project_b = stub_project(
        cfg_options={"ssh_args":
                     "-o UserKnownHostsFile="
                     "~/src/b/.debops/ssh/views/system/"
                     "known_hosts"},
        raw={"views": {"system": {"ssh": {"known_hosts": "project"}}}})

    write_config_snippet(project_a, str(config))
    write_config_snippet(project_b, str(config))

    content = config.read_text()
    store_line = [line for line in content.splitlines()
                  if line.strip().startswith('UserKnownHostsFile')][0]
    stores = store_line.split()[1:]
    assert stores[0] == '~/.ssh/known_hosts'
    assert stores == sorted(stores)
    assert '~/src/a/.debops/ssh/views/system/known_hosts' in stores
    assert '~/src/b/.debops/ssh/views/system/known_hosts' in stores


def test_write_config_snippet_is_deterministic_across_projects(
        stub_project, tmp_path):
    """Two operators writing from different projects in different
    order end with the identical managed block."""
    project_a = stub_project(
        cfg_options={"ssh_args":
                     "-o UserKnownHostsFile="
                     "~/src/a/.debops/ssh/views/system/"
                     "known_hosts"},
        raw={"views": {"system": {"ssh": {"known_hosts": "project"}}}})
    project_b = stub_project(
        cfg_options={"ssh_args":
                     "-o UserKnownHostsFile="
                     "~/src/b/.debops/ssh/views/system/"
                     "known_hosts"},
        raw={"views": {"system": {"ssh": {"known_hosts": "project"}}}})
    config_a = tmp_path / "config-a"
    config_b = tmp_path / "config-b"

    write_config_snippet(project_a, str(config_a))
    write_config_snippet(project_b, str(config_a))
    write_config_snippet(project_b, str(config_b))
    write_config_snippet(project_a, str(config_b))

    assert config_a.read_text() == config_b.read_text()


def test_write_config_snippet_replaces_atomically(stub_project, tmp_path):
    """The new content is written to a temporary file and renamed, so
    no partial configuration is left behind."""
    config = tmp_path / "ssh_config"
    config.write_text("Host bastion\n    ForwardAgent yes\n")

    write_config_snippet(stub_project(), str(config))

    assert config.read_text().strip()
    leftovers = [entry.name for entry in tmp_path.iterdir()
                 if entry.name != 'ssh_config']
    assert leftovers == []


def test_resolve_host_honors_the_legacy_ssh_variables(
        stub_project, fake_tools, fake_binary):
    """The pre-2.0 variable names Ansible still honors work as
    fallbacks."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "legacy-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_ssh_host\": \"192.0.2.10\","
        " \"ansible_ssh_user\": \"legacyuser\","
        " \"ansible_ssh_port\": \"2222\"}'\n")
    project = stub_project(raw={"binaries": binaries})

    parameters = resolve_host(project, "web")

    assert parameters["destination"] == "192.0.2.10"
    assert parameters["user"] == "legacyuser"
    assert parameters["port"] == "2222"


def test_resolve_host_reads_the_per_host_ssh_args(
        stub_project, fake_tools, fake_binary):
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "ssh-args-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"192.0.2.10\","
        " \"ansible_ssh_args\": \"-o BatchMode=yes\"}'\n")
    project = stub_project(raw={"binaries": binaries})

    parameters = resolve_host(project, "web")

    assert parameters["ssh_args"] == "-o BatchMode=yes"


def test_without_known_hosts_options_drops_the_declarations():
    """The store options appear as an '-o' pair, attached to '-o', or
    bare; the rest of the arguments keep their order."""
    tokens = without_known_hosts_options(
        ["-o", "ControlMaster=auto", "-o", "UserKnownHostsFile=/store",
         "-oUserKnownHostsFile=/other", "UserKnownHostsFile=/third",
         "-o", "BatchMode=yes"])

    assert tokens == ["-o", "ControlMaster=auto", "-o", "BatchMode=yes"]


def test_build_ssh_command_injects_the_store_first(stub_project,
                                                   fake_tools,
                                                   fake_binary):
    """In the project mode the store of the view leads the command and
    the resolved arguments cannot bypass it: the 'UserKnownHostsFile'
    options of the host and of the configuration are dropped, the rest
    of the arguments stay."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "store-bypass-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"192.0.2.10\","
        " \"ansible_ssh_args\": \"-o UserKnownHostsFile=/tmp/evil"
        " -o BatchMode=yes\"}'\n")
    project = stub_project(
        raw={"binaries": binaries,
             "views": {"system": {"ssh": {"known_hosts": "project"}}}},
        cfg_options={"ssh_args": "-o UserKnownHostsFile=/cfg-store"
                                 " -o ControlMaster=auto"})
    parameters = resolve_host(project, "web")

    command = build_ssh_command(project, "web", parameters)

    assert command[1:3] == ["-o", "UserKnownHostsFile=/cfg-store"]
    assert "UserKnownHostsFile=/tmp/evil" not in command
    assert command.count("UserKnownHostsFile=/cfg-store") == 1
    assert "BatchMode=yes" in command


def test_resolve_host_follows_the_connection_chains(
        stub_project, fake_tools, fake_binary, monkeypatch):
    """Each connection option follows the resolution of the ssh
    connection plugin: the inventory variables over the environment
    over the configuration option. The tiers do not merge: a host
    variable replaces the lower tiers entirely."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "chain-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"192.0.2.10\","
        " \"ansible_private_key_file\": \"/keys/modern\"}'\n")
    project = stub_project(
        raw={"binaries": binaries},
        cfg_options={"private_key_file": "/keys/ini",
                     "ssh_common_args": "-o Common=ini",
                     "timeout": "30"})
    monkeypatch.setenv("ANSIBLE_PRIVATE_KEY_FILE", "/keys/env")
    monkeypatch.delenv("ANSIBLE_TIMEOUT", raising=False)

    parameters = resolve_host(project, "web")

    assert parameters["identity"] == "/keys/modern"
    assert parameters["common_args"] == "-o Common=ini"
    assert parameters["timeout"] == "30"

    monkeypatch.setenv("ANSIBLE_TIMEOUT", "45")
    binaries["ansible-inventory"] = fake_binary(
        "keyless-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"192.0.2.10\"}'\n")
    project = stub_project(raw={"binaries": binaries},
                           cfg_options={"private_key_file": "/keys/ini"})
    parameters = resolve_host(project, "web")

    assert parameters["identity"] == "/keys/env"
    assert parameters["timeout"] == "45"

    monkeypatch.delenv("ANSIBLE_PRIVATE_KEY_FILE", raising=False)
    parameters = resolve_host(project, "web")

    assert parameters["identity"] == "/keys/ini"

    binaries["ansible-inventory"] = fake_binary(
        "legacy-key-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"192.0.2.10\","
        " \"ansible_ssh_private_key_file\": \"/keys/legacy\"}'\n")
    project = stub_project(raw={"binaries": binaries},
                           cfg_options={"private_key_file": "/keys/ini"})
    parameters = resolve_host(project, "web")

    assert parameters["identity"] == "/keys/legacy"


def test_resolve_host_resolves_the_executables_through_the_chains(
        stub_project, fake_tools, monkeypatch):
    for name in ("ANSIBLE_SSH_EXECUTABLE", "ANSIBLE_SCP_EXECUTABLE",
                 "ANSIBLE_SFTP_EXECUTABLE"):
        monkeypatch.delenv(name, raising=False)
    project = stub_project(
        raw={"binaries": dict(fake_tools["binaries"])},
        cfg_options={"ssh_executable": "/bin/ssh-ini",
                     "scp_executable": "/bin/scp-ini",
                     "sftp_executable": "/bin/sftp-ini"})

    parameters = resolve_host(project, "web")

    assert parameters["ssh_executable"] == "/bin/ssh-ini"
    assert parameters["scp_executable"] == "/bin/scp-ini"
    assert parameters["sftp_executable"] == "/bin/sftp-ini"

    monkeypatch.setenv("ANSIBLE_SCP_EXECUTABLE", "/bin/scp-env")
    parameters = resolve_host(project, "web")

    assert parameters["scp_executable"] == "/bin/scp-env"


def test_build_ssh_command_uses_the_resolved_executable_and_yields(
        stub_project, fake_tools, monkeypatch):
    """The resolved ssh executable builds the command, and an explicit
    '-o ConnectTimeout' of the options wins over the resolved
    timeout."""
    for name in ("ANSIBLE_SSH_EXECUTABLE", "ANSIBLE_TIMEOUT"):
        monkeypatch.delenv(name, raising=False)
    project = stub_project(
        raw={"binaries": dict(fake_tools["binaries"])},
        cfg_options={"ssh_executable": "/bin/ssh-ini",
                     "timeout": "30"})
    parameters = resolve_host(project, "web")

    command = build_ssh_command(project, "web", parameters,
                                options=["-o", "ConnectTimeout=60"])

    assert command[0] == "/bin/ssh-ini"
    assert "ConnectTimeout=60" in command
    assert "ConnectTimeout=30" not in command


def test_known_hosts_option_quotes_the_spaced_paths():
    """A store path which carries whitespace would be split into
    fragment paths by the option parsing of ssh; the double-quoted
    form survives it."""
    assert known_hosts_option('/plain/store') == \
        'UserKnownHostsFile=/plain/store'
    assert known_hosts_option('/a b/store') == \
        'UserKnownHostsFile="/a b/store"'


def test_known_hosts_option_refuses_the_unrepresentable_paths():
    for store in ('/q"uote', '/back\\slash', '/new\nline', '/carriage\r'):
        with pytest.raises(ValueError):
            known_hosts_option(store)


def test_render_config_snippet_quotes_the_spaced_store(stub_project,
                                                       tmp_path):
    """The managed block quotes a store path which carries whitespace,
    and the parse reads it back as one token."""
    store = str(tmp_path / "a b" / ".debops" / "ssh" / "views" /
                "system" / "known_hosts")
    project = stub_project(
        cfg_options={"ssh_args":
                     "-o 'UserKnownHostsFile=\"" + store + "\"'"},
        raw={"views": {"system": {"ssh": {"known_hosts": "project"}}}})

    lines = render_config_snippet(project)
    store_line = [line for line in lines
                  if line.strip().startswith('UserKnownHostsFile')][0]
    assert '"' + store + '"' in store_line
    assert parse_config_stores('\n'.join(lines) + '\n') == [store]


def test_split_destination_splits_the_user_at_the_last_at():
    """ssh parses 'a@b@c' as the user 'a@b' and the host 'c', the way
    'ssh -G' reports it."""
    assert split_destination('a@b@c') == ('a@b', 'c', None)
    assert split_destination('ssh://a@b@c:22') == ('a@b', 'c', '22')


def test_split_operand_splits_the_user_at_the_last_at():
    assert split_operand('a@b@c:/path') == ('a@b', 'c', '/path')


def test_write_config_snippet_warns_about_a_shadowing_directive(
        stub_project, tmp_path, caplog):
    """A 'UserKnownHostsFile' directive outside of the managed block
    shadows it: ssh applies the first obtained value of an option."""
    config = tmp_path / "ssh_config"
    config.write_text("Host *\n    UserKnownHostsFile /own/store\n")

    with caplog.at_level(logging.NOTICE):
        write_config_snippet(stub_project(), str(config))

    assert "may not apply" in caplog.text


def test_write_config_snippet_does_not_warn_about_its_own_block(
        stub_project, tmp_path, caplog):
    config = tmp_path / "ssh_config"

    with caplog.at_level(logging.NOTICE):
        write_config_snippet(stub_project(), str(config))
        write_config_snippet(stub_project(), str(config))

    assert "may not apply" not in caplog.text


def test_rescan_creates_the_store_with_the_private_mode(
        stub_project, fake_tools, tmp_path):
    """The store is created with the '0600' permissions from the
    start, without the world-readable window of an afterwards chmod;
    an existing store is tightened as before."""
    store = tmp_path / "fresh" / "known_hosts"
    os.makedirs(os.path.dirname(store))
    os.chmod(os.path.dirname(store), 0o755)

    rescan_hosts(stub_project(raw={"binaries":
                                   dict(fake_tools["binaries"])}),
                 ["web"], store=str(store), dns_mode='no-dns')

    assert (os.stat(store).st_mode & 0o777) == 0o600

    existing = tmp_path / "existing"
    existing.write_text("old\n")
    os.chmod(existing, 0o644)
    rescan_hosts(stub_project(raw={"binaries":
                                   dict(fake_tools["binaries"])}),
                 ["web"], store=str(existing), dns_mode='no-dns')

    assert (os.stat(existing).st_mode & 0o777) == 0o600


def test_resolve_host_refuses_non_scalar_numeric_options(
        stub_project, fake_tools, fake_binary):
    """A list-valued port would compose into garbage argv."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "list-port-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"192.0.2.10\","
        " \"ansible_port\": [\"22\"]}'\n")
    project = stub_project(raw={"binaries": binaries})

    with pytest.raises(ValueError, match="not a usable value"):
        resolve_host(project, "web")


def test_require_store_resolves_the_mode_and_the_injection(stub_project):
    """The user mode needs no injection; the project mode injects the
    declared store and refuses a view without one."""
    assert require_store(stub_project()) == \
        (os.path.expanduser("~/.ssh/known_hosts"), False)

    project = stub_project(
        cfg_options={"ssh_args": "-o UserKnownHostsFile=/store"},
        raw={"views": {"system": {"ssh": {"known_hosts": "project"}}}})
    assert require_store(project) == ("/store", True)

    dormant = stub_project(raw={"views": {"system": {"ssh": {
        "known_hosts": "project"}}}})
    with pytest.raises(ValueError, match="does not declare a known_hosts"):
        require_store(dormant)
