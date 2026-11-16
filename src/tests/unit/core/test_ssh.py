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
import shlex
import socket
from unittest import mock

import pytest

import debops.core.ssh as ssh_module
from debops.core.ssh import (SCP_OPTIONS_WITH_VALUE, SFTP_OPTIONS_WITH_VALUE,
                             SSH_OPTIONS_WITH_VALUE,
                             JumpRewriter, build_handoff_command,
                             build_ssh_command,
                             ensure_store_dir, host_identifiers,
                             known_hosts_mode, known_hosts_option,
                             known_hosts_store,
                             parse_config_stores, proxy_jump_command,
                             quote_store_path, remove_command,
                             render_config_snippet,
                             rescan_actions, resolve_destination,
                             build_scp_command, build_sftp_command,
                             connection_jump_names,
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


@pytest.mark.parametrize("variables,key", [
    ('{"ansible_host": "{{ real_addr }}"}', "destination"),
    ('{"ansible_host": "192.0.2.10",'
     ' "ansible_ssh_common_args": "-J {{ bastion }}"}', "common_args"),
])
def test_resolve_host_refuses_unrendered_templates(
        stub_project, fake_tools, fake_binary, variables, key):
    """The '--host' dump of 'ansible-inventory' does not render the
    templates of the inventory variables; a value which still carries
    the delimiters is refused instead of reaching the command line."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "templated-inventory",
        "#!/bin/sh\n"
        "printf '%s' '" + variables + "'\n")
    project = stub_project(raw={"binaries": binaries})

    with pytest.raises(ValueError) as error:
        resolve_host(project, "web")
    message = str(error.value)
    assert "unrendered Ansible template" in message
    assert '"' + key + '" connection parameter' in message


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
        "-o", "ProxyCommand=ssh -o ConnectTimeout=10 "
              "-W '[%h]:%p' jump@bastion",
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
    assert in_sequence(command, ["-o", "ProxyCommand=ssh "
                                 "-o ConnectTimeout=10 -W '[%h]:%p' "
                                 "jump@bastion"])
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
        stub_project, fake_tools, monkeypatch, tmp_path):
    store = str(tmp_path / "store" / "known_hosts")
    os.makedirs(os.path.dirname(store))
    with open(store, "w") as handle:
        handle.write("# stale entries live here\n")

    def fake_getaddrinfo(name, *args, **kwargs):
        if name in ("web", "192.0.2.10"):
            return [(2, 1, 6, "", ("192.0.2.10", 0))]
        raise socket.gaierror("no DNS")

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

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

    hosts, unmatched, variables = resolve_patterns(project, ["multi"])

    assert hosts == ["web-1", "web-2"]
    assert unmatched == []
    assert set(variables) == {"web-1", "web-2"}


def test_resolve_patterns_unions_and_deduplicates(stub_project, fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    hosts, unmatched, variables = resolve_patterns(
        project, ["multi", "solo", "multi"])

    assert hosts == ["web-1", "web-2", "web-3"]
    assert unmatched == []
    assert set(variables) == {"web-1", "web-2", "web-3"}


def test_resolve_patterns_reports_the_unmatched(stub_project, fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    hosts, unmatched, variables = resolve_patterns(project, ["none"])

    assert hosts == []
    assert unmatched == ["none"]
    assert variables == {}


def test_resolve_patterns_reports_a_failing_expansion(stub_project,
                                                      fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    with pytest.raises(ValueError):
        resolve_patterns(project, ["broken"])


def test_resolve_patterns_covers_the_hosts_without_variables(
        stub_project, fake_tools, fake_binary):
    """A host which defines no variables of its own appears in the
    group structure of the '--list' dump but not in its hostvars; the
    expansion covers it and the destination resolves it to its own
    name."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "bare-host-inventory",
        "#!/bin/sh\n"
        'if [ "$1" = "--list" ]; then\n'
        "    printf '%s' '{\"db\": {\"hosts\": [\"barehost\"]}, "
        "\"_meta\": {\"hostvars\": {}}}'\n"
        "else\n"
        "    printf '%s' '{}'\n"
        "fi\n")
    project = stub_project(raw={"binaries": binaries})

    hosts, unmatched, variables = resolve_patterns(project, ["db"])

    assert hosts == ["barehost"]
    assert unmatched == []
    assert variables == {"barehost": {}}

    parameters = resolve_destination(project, "barehost")

    assert parameters["destination"] == "barehost"


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
    """The identity and the accept-new option are options DebOps
    applies to the handoff invocation."""
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    command = build_handoff_command(project, "sftp",
                                    ["-b", "batch", "host"],
                                    identity="/keys/id", accept=True)

    assert command == ["/usr/bin/sftp",
                       "-o", "StrictHostKeyChecking=accept-new",
                       "-i", "/keys/id",
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
        "ansible-inventory": "/nonexistent/ansible-inventory"}})

    with pytest.raises(ChildProcessError):
        resolve_patterns(project, ["all"])


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
    assert "not DNSSEC-validated" in message
    assert "--confirm" in message
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


def test_rescan_hosts_stores_unsigned_matches_by_default(
        monkeypatch, stub_project, fake_tools, fake_binary, tmp_path):
    """An SSHFP match which the resolver did not authenticate grants
    no trust: the keys are handled like the keys of a host without
    SSHFP records, and the report says so."""
    project = fqdn_project(stub_project, fake_tools, fake_binary)
    stub_dns(monkeypatch, {(4, 2, FQDN_FINGERPRINT)}, authenticated=False)
    store = tmp_path / "store"

    results = rescan_hosts(project, ["web"], store=str(store),
                           phases=("scan",))

    host, succeeded, message = results[0]
    assert succeeded
    assert "not DNSSEC-validated" in message
    assert FQDN_KEY_LINE in store.read_text()


def test_rescan_hosts_asks_for_confirmation_on_unsigned_matches(
        monkeypatch, stub_project, fake_tools, fake_binary, tmp_path):
    """With '--confirm', the unsigned match is offered like the hosts
    without records; a decline keeps the old trust."""
    project = fqdn_project(stub_project, fake_tools, fake_binary)
    stub_dns(monkeypatch, {(4, 2, FQDN_FINGERPRINT)}, authenticated=False)
    store = tmp_path / "store"
    store.write_text("old\n")

    results = rescan_hosts(project, ["web"], store=str(store),
                           confirm=lambda host, offered: False)

    assert not results[0][1]
    assert store.read_text() == "old\n"

    results = rescan_hosts(project, ["web"], store=str(store),
                           confirm=lambda host, offered: True)

    assert results[0][1]
    assert FQDN_KEY_LINE in store.read_text()


def test_rescan_hosts_refuses_unsigned_matches_when_configured(
        monkeypatch, stub_project, fake_tools, fake_binary, tmp_path):
    """The 'ssh.rescan.trust_unsigned_records' option set to 'false'
    refuses the hosts whose SSHFP match the resolver did not
    authenticate; '--confirm' accepts them after the check."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "fqdn-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"" + FQDN + "\"}'\n")
    binaries["ssh-keyscan"] = fake_binary(
        "fqdn-keyscan",
        "#!/bin/sh\nprintf '%s\\n' \"$4 ssh-ed25519 "
        + FQDN_KEY_BLOB + "\"\n")
    project = stub_project(raw={
        "binaries": binaries,
        "ssh": {"rescan": {"trust_unsigned_records": False}}})
    stub_dns(monkeypatch, {(4, 2, FQDN_FINGERPRINT)}, authenticated=False)
    store = tmp_path / "store"
    store.write_text("old\n")

    results = rescan_hosts(project, ["web"], store=str(store),
                           phases=("scan",))

    host, succeeded, message = results[0]
    assert not succeeded
    assert "not DNSSEC-validated" in message
    assert store.read_text() == "old\n"

    results = rescan_hosts(project, ["web"], store=str(store),
                           confirm=lambda host, offered: True)

    assert results[0][1]
    assert FQDN_KEY_LINE in store.read_text()


def test_rescan_hosts_no_dns_asks_for_confirmation(
        monkeypatch, stub_project, fake_tools, fake_binary, tmp_path):
    """With '--no-dns --confirm', every store is gated on the
    operator's decision, and a confirmation stores the keys as
    scanned -- the types without SSHFP algorithm numbers among them."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "fqdn-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"" + FQDN + "\"}'\n")
    binaries["ssh-keyscan"] = fake_binary(
        "mixed-keyscan",
        "#!/bin/sh\n"
        "printf '%s\\n' \"$4 ssh-ed25519 " + FQDN_KEY_BLOB + "\"\n"
        "printf '%s\\n' \"$4 sk-ssh-ed25519@openssh.com "
        + base64.b64encode(b'\x22' * 32).decode('ascii') + "\"\n")
    project = stub_project(raw={"binaries": binaries})
    # The no-dns mode does not consult DNS; the identifiers still
    # resolve through the stubbed getaddrinfo
    monkeypatch.setattr('socket.getaddrinfo',
                        lambda host, *args, **kwargs: [
                            (2, 1, 6, '', ('192.0.2.10', 0))])
    store = tmp_path / "store"
    offered_seen = []

    def confirm(host, offered):
        offered_seen.append(offered)
        return True

    results = rescan_hosts(project, ["web"], store=str(store),
                           phases=("scan",), dns_mode='no-dns',
                           confirm=confirm)

    assert results[0][1]
    content = store.read_text()
    assert FQDN_KEY_LINE in content
    assert 'sk-ssh-ed25519@openssh.com' in content
    # The offer carries the fingerprints of all the scanned keys, the
    # FIDO type among them
    offered = offered_seen[0]
    assert ('SHA256:' + base64.b64encode(bytes.fromhex(FQDN_FINGERPRINT))
            .decode('ascii').rstrip('='), 'ssh-ed25519') in offered
    assert any(key_type == 'sk-ssh-ed25519@openssh.com'
               for fingerprint, key_type in offered
               if fingerprint.startswith('SHA256:'))

    declined = rescan_hosts(project, ["web"], store=str(store),
                            phases=("scan",), dns_mode='no-dns',
                            confirm=lambda host, offered: False)

    assert not declined[0][1]
    assert 'rejected by the operator' in declined[0][2]


def test_rescan_hosts_dns_verify_asks_for_confirmation_on_unsigned(
        monkeypatch, stub_project, fake_tools, fake_binary, tmp_path):
    """In the strict mode, an unauthenticated match is offered through
    the 'confirm' callback; a decline keeps the host unstored."""
    project = fqdn_project(stub_project, fake_tools, fake_binary)
    stub_dns(monkeypatch, {(4, 2, FQDN_FINGERPRINT)}, authenticated=False)
    store = tmp_path / "store"
    store.write_text("old\n")

    results = rescan_hosts(project, ["web"], store=str(store),
                           phases=("scan",), dns_mode='dns-verify',
                           confirm=lambda host, offered: False)

    host, succeeded, message = results[0]
    assert not succeeded
    assert "rejected by the operator" in message
    assert store.read_text() == "old\n"

    results = rescan_hosts(project, ["web"], store=str(store),
                           phases=("scan",), dns_mode='dns-verify',
                           confirm=lambda host, offered: True)

    host, succeeded, message = results[0]
    assert succeeded
    assert "not DNSSEC-validated" in message
    assert "by the operator's decision" in message
    assert FQDN_KEY_LINE in store.read_text()


def test_rescan_hosts_dns_verify_asks_for_confirmation_without_records(
        monkeypatch, stub_project, fake_tools, fake_binary, tmp_path):
    """In the strict mode, a host without verified records is offered
    through the 'confirm' callback as well."""
    project = fqdn_project(stub_project, fake_tools, fake_binary)
    stub_dns(monkeypatch, set(), authenticated=True)
    store = tmp_path / "store"
    store.write_text("old\n")

    results = rescan_hosts(project, ["web"], store=str(store),
                           phases=("scan",), dns_mode='dns-verify',
                           confirm=lambda host, offered: False)

    host, succeeded, message = results[0]
    assert not succeeded
    assert store.read_text() == "old\n"

    results = rescan_hosts(project, ["web"], store=str(store),
                           phases=("scan",), dns_mode='dns-verify',
                           confirm=lambda host, offered: True)

    host, succeeded, message = results[0]
    assert succeeded
    assert "by the operator's decision" in message
    assert FQDN_KEY_LINE in store.read_text()


def test_rescan_hosts_confirmation_cannot_override_a_contradiction(
        monkeypatch, stub_project, fake_tools, fake_binary, tmp_path):
    """Keys which contradict the published records are refused with
    and without the 'confirm' callback."""
    project = fqdn_project(stub_project, fake_tools, fake_binary)
    stub_dns(monkeypatch, {(4, 2, 'ab' * 32)}, authenticated=True)
    store = tmp_path / "store"
    store.write_text("old\n")

    results = rescan_hosts(project, ["web"], store=str(store),
                           phases=("scan",),
                           confirm=lambda host, offered: True)

    host, succeeded, message = results[0]
    assert not succeeded
    assert "do not match the SSHFP records" in message
    assert store.read_text() == "old\n"


def test_rescan_hosts_refuses_when_the_lookup_fails(
        monkeypatch, stub_project, fake_tools, fake_binary, tmp_path):
    """A resolver which cannot answer -- SERVFAIL of a validating
    resolver, a timeout, a broken installation -- refuses the host;
    only the absence of records falls back to the operator's
    decision."""
    project = fqdn_project(stub_project, fake_tools, fake_binary)
    monkeypatch.setattr('socket.getaddrinfo',
                        lambda host, *args, **kwargs: [
                            (2, 1, 6, '', ('192.0.2.10', 0))])

    def failing_lookup(hostname):
        raise RuntimeError('all nameservers failed')

    monkeypatch.setattr(ssh_module.ssh, 'lookup_sshfp', failing_lookup)
    store = tmp_path / "store"
    store.write_text("old\n")

    results = rescan_hosts(project, ["web"], store=str(store),
                           phases=("scan",))

    host, succeeded, message = results[0]
    assert not succeeded
    assert "the SSHFP lookup of web failed" in message
    assert "all nameservers failed" in message
    assert store.read_text() == "old\n"

    results = rescan_hosts(project, ["web"], store=str(store),
                           phases=("scan",),
                           confirm=lambda host, offered: True)

    host, succeeded, message = results[0]
    assert not succeeded
    assert "the SSHFP lookup" in message
    assert store.read_text() == "old\n"


def test_resolve_host_refuses_a_dash_leading_user(
        stub_project, fake_tools, fake_binary):
    """A user which carries an ssh option would be parsed as one by
    sftp, and its value executed through the user's shell."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "option-user-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"192.0.2.10\","
        " \"ansible_user\": \"-oProxyCommand=evil\"}'\n")
    project = stub_project(raw={"binaries": binaries})

    with pytest.raises(ValueError, match="looks like an SSH option"):
        resolve_host(project, "web")


def test_sftp_command_refuses_the_option_shaped_destination(
        stub_project, fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    with pytest.raises(ValueError, match="looks like an SSH option"):
        build_sftp_command(project, "-oProxyCommand=evil@web:/tmp")


def test_scp_and_sftp_bracket_the_ipv6_destinations(
        stub_project, fake_tools, inventory_fake):
    """The transfer grammars read the colons of an IPv6 literal as the
    host and path separator; the bracketed form survives them."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = inventory_fake(
        "ipv6-inventory", '{"ansible_host": "2001:db8::1"}')
    project = stub_project(raw={"binaries": binaries})

    command = build_scp_command(project, ["/etc/hostname"],
                                "web:/tmp/x")

    assert "[2001:db8::1]:/tmp/x" in command

    command = build_sftp_command(project, "web:/srv")

    assert any(token.endswith("[2001:db8::1]:/srv")
               for token in command)


def test_handoff_command_applies_the_interpreted_options(stub_project,
                                                         fake_tools):
    """The user, the port and the identity which the walk collected
    before the '--' marker reach the composed handoff command."""
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    command = build_handoff_command(
        project, 'ssh', ["web-1"], identity="/keys/x", user="alice",
        port=2222, passthrough=["-L", "8080:localhost:80"])

    assert in_sequence(command, ["-i", "/keys/x"])
    assert in_sequence(command, ["-l", "alice"])
    assert in_sequence(command, ["-p", "2222"])
    assert command[-3:] == ["-L", "8080:localhost:80", "web-1"]


def test_handoff_command_injects_the_store_with_accept(stub_project,
                                                       fake_tools):
    """The '--accept' option stores unseen host keys; in the project
    mode the store of the view is injected with it, so the keys land
    in the store of the view. Without '--accept' no store is
    applied."""
    binaries = dict(fake_tools["binaries"])
    project = stub_project(
        raw={"binaries": binaries,
             "views": {"system": {"ssh": {"known_hosts": "project"}}}},
        cfg_options={"ssh_args": "-o UserKnownHostsFile=/store"})

    command = build_handoff_command(project, 'ssh', ["web-1"],
                                    accept=True)

    assert in_sequence(command, ["-o", "UserKnownHostsFile=/store"])
    assert in_sequence(command, ["-o",
                                 "StrictHostKeyChecking=accept-new"])

    command = build_handoff_command(project, 'ssh', ["web-1"])

    assert "UserKnownHostsFile" not in command


def test_rescan_hosts_keeps_the_entries_of_the_silent_identifiers(
        stub_project, fake_tools, monkeypatch, tmp_path):
    """An identifier which does not answer the scan keeps its stored
    entries: only the identifiers which contributed keys have their
    trust replaced."""
    store = str(tmp_path / "store" / "known_hosts")
    os.makedirs(os.path.dirname(store))
    with open(store, "w") as handle:
        handle.write("# the entries of both identifiers\n")

    def fake_getaddrinfo(name, *args, **kwargs):
        if name == "192.0.2.10":
            return [(2, 1, 6, "", ("192.0.2.10", 0))]
        raise socket.gaierror("no DNS")

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    results = rescan_hosts(stub_project(raw={
        "binaries": dict(fake_tools["binaries"])}),
        ["web"], store=store, dns_mode='no-dns')

    # The scan of the address succeeded; the host is refreshed through
    # it, while the silent name keeps its stored entries
    assert results[0][1]
    with open(fake_tools["log"]) as handle:
        removals = handle.read().splitlines()
    assert any("-R [192.0.2.10]:2222" in line for line in removals)
    assert not any("-R [web]:2222" in line for line in removals)


def test_translate_ssh_args_drops_a_trailing_value_option():
    """A value option without its value is dropped, not crashed on."""
    translated, dropped = translate_ssh_args("-J 1234:localhost:22 -F")

    assert translated == [("-o", "ProxyJump=1234:localhost:22")]
    assert dropped == ["-F"]


@pytest.mark.parametrize("store", [
    '/store/with"quote',
    "/store/with'apostrophe",
    '/store/with\\backslash',
    '/store/with\nnewline',
    '/store/with\rcarriage',
])
def test_quote_store_path_refuses_the_unrepresentable(store):
    """A store path which cannot be represented inside the ssh option
    values and the shell-executed contexts is refused."""
    with pytest.raises(ValueError):
        quote_store_path(store)


def test_quote_store_path_quotes_the_whitespace():
    assert quote_store_path('/store/with space') == '"/store/with space"'
    assert quote_store_path('/plain/store') == '/plain/store'


def test_proxy_jump_command_carries_the_options_and_the_port():
    """The ProxyCommand value runs the jump connection with the given
    option pairs of the parent, and the port of the hop is carried as
    the '-p' option, the way the implicit ProxyJump command of ssh
    carries it."""
    value = proxy_jump_command(
        "jump@bastion:2222",
        [("-o", "UserKnownHostsFile=/store"), ("-o", "BatchMode=yes")])

    assert value == ("ProxyCommand=ssh -p 2222 "
                     "-o UserKnownHostsFile=/store -o BatchMode=yes "
                     "-W '[%h]:%p' jump@bastion")


def test_proxy_jump_command_quotes_the_shell_syntax():
    """The value is executed by the shell: the IPv6 brackets and the
    spaces of a destination are quoted, so they survive the shell."""
    value = proxy_jump_command("[2001:db8::1]:2222", [])

    assert "-p 2222" in value
    assert "'[2001:db8::1]'" in value


def test_jump_rewriter_rewrites_the_option_forms():
    """The four option forms of a single hop are rewritten alike."""
    for tokens in (["-J", "hop"], ["-Jhop"],
                   ["-o", "ProxyJump=hop"], ["-oProxyJump=hop"]):
        rewriter = JumpRewriter([("-o", "UserKnownHostsFile=/s")])
        rewritten = rewriter.rewrite_tokens(list(tokens))
        assert rewritten == ["-o", "ProxyCommand=ssh "
                             "-o UserKnownHostsFile=/s "
                             "-W '[%h]:%p' hop"], tokens


def test_jump_rewriter_consumes_the_option_values_as_pairs():
    """The '-o' options are consumed with their value tokens, so a
    store path or another option value is never inspected as a jump
    option on its own."""
    rewriter = JumpRewriter([])
    rewritten = rewriter.rewrite_tokens(
        ["-o", "UserKnownHostsFile=x", "-J", "hop"])

    assert rewritten == ["-o", "UserKnownHostsFile=x",
                         "-o", "ProxyCommand=ssh -W '[%h]:%p' hop"]


def test_jump_rewriter_leaves_the_chains():
    """A comma-separated hop list stays unchanged; the chains are a
    documented limitation of the suite."""
    rewriter = JumpRewriter([])

    assert rewriter.rewrite_tokens(["-J", "a,b"]) == ["-J", "a,b"]
    assert rewriter.rewrite_tokens(["-o", "ProxyJump=a,b"]) == \
        ["-o", "ProxyJump=a,b"]
    assert rewriter.rewrite_pairs([("-o", "ProxyJump=a,b")]) == \
        [("-o", "ProxyJump=a,b")]


def test_jump_rewriter_refuses_the_proxycommand_mix():
    """A ProxyCommand of the operator and a structured jump of the
    same connection are refused: the ProxyCommand would shadow the
    jump handling of DebOps."""
    rewriter = JumpRewriter([])
    rewriter.rewrite_tokens(["-o", "ProxyCommand=nc x", "-J", "hop"])

    with pytest.raises(ValueError):
        rewriter.check()


def test_jump_rewriter_recognizes_the_mix_across_the_groups():
    """The conflict state accumulates across the argument groups of
    one command."""
    rewriter = JumpRewriter([])
    rewriter.rewrite_tokens(["-o", "ProxyCommand=nc x"])
    rewriter.rewrite_tokens(["-J", "hop"])

    with pytest.raises(ValueError):
        rewriter.check()


def test_jump_rewriter_rewrites_the_pairs():
    """The pair form of the file-transfer builders is rewritten
    alike."""
    rewriter = JumpRewriter([("-o", "BatchMode=yes")])
    rewritten = rewriter.rewrite_pairs([("-o", "ProxyJump=hop")])

    assert rewritten == [("-o", "ProxyCommand=ssh -o BatchMode=yes "
                          "-W '[%h]:%p' hop")]


def test_write_config_snippet_writes_through_a_symlink(stub_project,
                                                       tmp_path):
    """A dotfile-managed configuration is a symlink; the managed block
    is written through it, so the target keeps receiving it."""
    target = tmp_path / "dotfiles" / "ssh_config"
    target.parent.mkdir()
    target.write_text("Host bastion\n    ForwardAgent yes\n")
    config = tmp_path / ".ssh" / "config"
    config.parent.mkdir()
    config.symlink_to(target)

    write_config_snippet(stub_project(), str(config))

    assert config.is_symlink()
    assert "BEGIN debops ssh managed block" in target.read_text()
    assert "ForwardAgent yes" in target.read_text()


def test_build_ssh_command_yields_to_the_attached_timeout_form(
        stub_project, fake_tools):
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})
    parameters = resolve_host(project, "web")

    command = build_ssh_command(project, "web", parameters,
                                options=["-oConnectTimeout=5"])

    assert "ConnectTimeout=5" not in command
    assert "-oConnectTimeout=5" in command


def test_rescan_expands_the_tilde_of_the_explicit_store(
        stub_project, fake_tools, monkeypatch, tmp_path):
    """The '--known-hosts-file' value is tilde-expanded, like the store
    paths of the configuration are."""
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    os.makedirs(str(tmp_path / "home"))

    results = rescan_hosts(stub_project(raw={
        "binaries": dict(fake_tools["binaries"])}),
        ["web"], store="~/known_hosts", dns_mode='no-dns')

    assert results == [("web", True, "")]
    assert (tmp_path / "home" / "known_hosts").exists()


def test_rescan_reports_the_unsigned_keys_of_the_fallback(
        monkeypatch, stub_project, fake_tools, fake_binary, tmp_path):
    """The unsigned-match fallback stores every fingerprintable key;
    the report does not claim the keys without records were
    skipped."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "fqdn-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"" + FQDN + "\"}'\n")
    binaries["ssh-keyscan"] = fake_binary(
        "two-key-keyscan",
        "#!/bin/sh\n"
        "printf '%s\n' \"$4 ssh-ed25519 " + FQDN_KEY_BLOB + "\"\n"
        "printf '%s\n' \"$4 ssh-rsa AAAArfakekey\"\n")
    project = stub_project(raw={"binaries": binaries})
    stub_dns(monkeypatch, {(4, 2, FQDN_FINGERPRINT)}, authenticated=False)
    store = tmp_path / "store"

    results = rescan_hosts(project, ["web"], store=str(store),
                           phases=("scan",))

    host, succeeded, message = results[0]
    assert succeeded
    assert "were not stored" not in message
    assert "stored as scanned" in message
    content = store.read_text()
    assert "ssh-ed25519" in content
    assert "ssh-rsa" in content


def test_write_config_snippet_refuses_a_corrupted_block(
        stub_project, tmp_path):
    """A managed block without its end marker is refused: its content
    would win over the fresh block, and the next write would treat
    the span between the markers as its own and drop it."""
    config = tmp_path / "ssh_config"
    config.write_text("# BEGIN debops ssh managed block\n"
                      "Host *\n"
                      "    UserKnownHostsFile /stale/store\n")

    with pytest.raises(ValueError, match="without its end marker"):
        write_config_snippet(stub_project(), str(config))
    assert "UserKnownHostsFile /stale/store" in config.read_text()


def test_build_ssh_command_lets_the_operator_options_win(
        stub_project, fake_tools, fake_binary):
    """The options the operator typed directly precede the resolved
    arguments: ssh applies the first obtained value, and the
    operator's own '-o' must not be defeated by the view's."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "master-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"192.0.2.10\","
        " \"ansible_ssh_args\": \"-o ControlMaster=auto\"}'\n")
    project = stub_project(raw={"binaries": binaries})

    command = build_ssh_command(
        project, "web", resolve_host(project, "web"),
        options=["-o", "ControlMaster=no"])

    assert command.index("ControlMaster=no") \
        < command.index("ControlMaster=auto")


def test_rescan_hosts_refuses_the_mixed_unfingerprintable_scan(
        monkeypatch, stub_project, fake_tools, fake_binary, tmp_path):
    """A scan which offers unverifiable keys alongside a verified one
    refuses the host: the key offer of a connection carries public
    keys their holder does not need to own."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "fqdn-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"" + FQDN + "\"}'\n")
    binaries["ssh-keyscan"] = fake_binary(
        "mixed-keyscan",
        "#!/bin/sh\n"
        "printf '%s\\n' \"$4 ssh-ed25519 " + FQDN_KEY_BLOB + "\"\n"
        "printf '%s\\n' \"$4 sk-ssh-ed25519@openssh.com AAAAskkey\"\n")
    project = stub_project(raw={"binaries": binaries})
    stub_dns(monkeypatch, {(4, 2, FQDN_FINGERPRINT)}, authenticated=True)
    store = tmp_path / "store"
    store.write_text("old\n")

    import debops.core.ssh.ssh as ssh_module
    original = ssh_module._classify_scanned_keys

    def spy(host, keys, resolvable, dns_mode, confirm, details,
            trust_unsigned=True):
        print('SPY keys:', keys)
        print('SPY resolvable:', resolvable)
        result = original(host, keys, resolvable, dns_mode, confirm,
                          details, trust_unsigned)
        print('SPY result:', result[0], result[1])
        return result

    monkeypatch.setattr(ssh_module, '_classify_scanned_keys', spy)

    results = rescan_hosts(project, ["web"], store=str(store))

    host, succeeded, message = results[0]
    assert not succeeded
    assert "without SSHFP algorithm numbers" in message
    assert "sk-ssh-ed25519@openssh.com" in message
    assert store.read_text() == "old\n"
    # The refusal happens before any removal runs
    log = fake_tools["log"]
    removals = open(log).read() if os.path.exists(log) else ""
    assert " -R " not in removals


def test_rescan_hosts_reports_the_operator_decision_on_unsigned(
        monkeypatch, stub_project, fake_tools, fake_binary, tmp_path):
    """With the refusal policy and '--confirm', an acceptance stores
    every scanned key and the report says the operator decided; a
    decline stores nothing and says the unverified keys were not
    stored."""
    project = fqdn_project(stub_project, fake_tools, fake_binary)
    project.config.raw['ssh'] = {'rescan': {
        'trust_unsigned_records': False}}
    stub_dns(monkeypatch, {(4, 2, FQDN_FINGERPRINT)}, authenticated=False)
    store = tmp_path / "store"

    results = rescan_hosts(project, ["web"], store=str(store),
                           confirm=lambda host, offered: True)

    host, succeeded, message = results[0]
    assert succeeded
    assert "were not stored" not in message
    assert "by the operator's decision" in message
    assert FQDN_KEY_LINE in store.read_text()

    after_accept = store.read_text()

    results = rescan_hosts(project, ["web"], store=str(store),
                           confirm=lambda host, offered: False)

    host, succeeded, message = results[0]
    assert not succeeded
    # The decline stores nothing: the store keeps the state the
    # acceptance left
    assert store.read_text() == after_accept


def test_rescan_hosts_keeps_the_store_on_a_removal_failure(
        stub_project, fake_tools, fake_binary, monkeypatch, tmp_path):
    """The removals and the append happen on a copy of the store: a
    removal which fails is reported and the store is still replaced
    with the state the cycle reached."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "dual-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"192.0.2.10\"}'\n")
    binaries["ssh-keygen"] = fake_binary(
        "failing-keygen",
        "#!/bin/sh\n"
        'for name in "$@"; do\n'
        '    if [ "$name" = "192.0.2.10" ]; then\n'
        "        echo 'cannot remove' >&2\n"
        "        exit 1\n"
        "    fi\n"
        "done\n"
        "printf '%s\\n' \"$*\" >> "
        + shlex.quote(str(tmp_path / "keygen.log")) + "\n")
    project = stub_project(raw={"binaries": binaries})

    def fake_getaddrinfo(name, *args, **kwargs):
        if name == "192.0.2.10":
            return [(2, 1, 6, "", ("192.0.2.10", 0))]
        raise socket.gaierror("no DNS")

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    store = tmp_path / "store" / "known_hosts"
    os.makedirs(os.path.dirname(store))
    with open(store, "w") as handle:
        handle.write("old entry of web\n")
        handle.write("old entry of the address\n")

    results = rescan_hosts(project, ["web"], store=str(store),
                           dns_mode='no-dns')

    host, succeeded, message = results[0]
    assert not succeeded
    assert "cannot remove the entries of 192.0.2.10" in message
    content = store.read_text()
    # The failed removal kept the address entry, the unanswered name
    # keeps its entry, and the scanned keys were appended
    assert "old entry of the address" in content
    assert "old entry of web" in content
    assert "AAAAfakekey" in content
    assert not (tmp_path / "store" / "known_hosts.old").exists()


def test_rescan_hosts_normalizes_the_last_store_line(
        stub_project, fake_tools, monkeypatch, tmp_path):
    """A store whose last line lacks its newline does not merge the
    appended entry into it."""
    store = tmp_path / "known_hosts"
    with open(store, "w") as handle:
        handle.write("old entry without newline")

    def fake_getaddrinfo(name, *args, **kwargs):
        if name == "192.0.2.10":
            return [(2, 1, 6, "", ("192.0.2.10", 0))]
        raise socket.gaierror("no DNS")

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    rescan_hosts(stub_project(raw={
        "binaries": dict(fake_tools["binaries"])}),
        ["web"], store=str(store), dns_mode='no-dns')

    lines = store.read_text().splitlines()
    assert "old entry without newline" in lines
    assert any("ssh-ed25519" in line for line in lines)


def test_handoff_command_uses_the_configured_transfer_binary(
        stub_project):
    """The sftp handoff honors the executable the configuration names,
    like the sftp builder does."""
    project = stub_project(cfg_options={"sftp_executable": "/bin/sftp-x"})

    command = build_handoff_command(project, 'sftp', ["host"])

    assert command[0] == "/bin/sftp-x"


def test_handoff_command_applies_the_ssh_flags_to_ssh_only(stub_project):
    """The login user and the port are flags of ssh; sftp carries them
    in its destination, and its '-p' means something else."""
    project = stub_project(cfg_options={"sftp_executable": "/bin/sftp-x"})

    command = build_handoff_command(project, 'sftp', ["host"],
                                    user="alice", port=2222)

    assert "-l" not in command
    assert "2222" not in command


def test_without_known_hosts_options_covers_the_config_form():
    """The known_hosts declaration of the configuration grammar --
    the option word with a space instead of the equals sign -- is
    dropped like the option forms are."""
    tokens = without_known_hosts_options(
        ["-o", "ControlMaster=auto", "-o", "UserKnownHostsFile /own",
         "UserKnownHostsFile /bare", "-o", "BatchMode=yes"])

    assert tokens == ["-o", "ControlMaster=auto", "-o", "BatchMode=yes"]


def test_build_scp_command_keeps_the_operator_store_declaration(
        stub_project, fake_tools):
    """In the user mode nothing is injected, and the known_hosts file
    the operator declared in the ssh_args passes through, like it
    does for 'debops ssh'."""
    project = stub_project(
        raw={"binaries": dict(fake_tools["binaries"])},
        cfg_options={"ssh_args": "-o UserKnownHostsFile=/operator/store"})

    command = build_scp_command(project, ["/etc/hostname"], "web:/tmp/x")

    assert sum("UserKnownHostsFile=" in token
               for token in command) == 1


def test_build_ssh_command_lets_the_operator_flag_lead(stub_project,
                                                       fake_tools):
    """An '-l' the operator typed reaches the command ahead of the
    user the inventory defines: ssh applies the first obtained
    value."""
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})
    parameters = resolve_host(project, "web")

    command = build_ssh_command(project, "web", parameters,
                                options=["-l", "root"])

    assert command.index("root") < command.index("admin")


def test_rescan_hosts_reads_a_store_in_another_encoding(
        stub_project, fake_tools, monkeypatch, tmp_path):
    """The store copy runs in binary mode: an operator comment in an
    encoding the locale does not decode does not abort the rescan."""
    store = tmp_path / "known_hosts"
    with open(store, "wb") as handle:
        handle.write("# komment \xff\n".encode('latin-1'))
        handle.write(b"old entry\n")

    def fake_getaddrinfo(name, *args, **kwargs):
        if name == "192.0.2.10":
            return [(2, 1, 6, "", ("192.0.2.10", 0))]
        raise socket.gaierror("no DNS")

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    results = rescan_hosts(stub_project(raw={
        "binaries": dict(fake_tools["binaries"])}),
        ["web"], store=str(store), dns_mode='no-dns')

    assert results == [("web", True, "")]
    content = store.read_bytes()
    assert "komment".encode('latin-1') in content
    assert "old entry".encode() in content
    assert b"ssh-ed25519" in content


def test_rescan_hosts_writes_through_a_symlinked_store(
        stub_project, fake_tools, monkeypatch, tmp_path):
    """A store which is a symlink into a dotfiles tree receives the
    entries through the link; the link itself survives."""
    target = tmp_path / "dotfiles" / "known_hosts"
    target.parent.mkdir()
    target.write_text("old entry\n")
    store = tmp_path / ".ssh" / "known_hosts"
    store.parent.mkdir()
    store.symlink_to(target)

    def fake_getaddrinfo(name, *args, **kwargs):
        if name == "192.0.2.10":
            return [(2, 1, 6, "", ("192.0.2.10", 0))]
        raise socket.gaierror("no DNS")

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    rescan_hosts(stub_project(raw={
        "binaries": dict(fake_tools["binaries"])}),
        ["web"], store=str(store), dns_mode='no-dns')

    assert store.is_symlink()
    assert "ssh-ed25519" in target.read_text()
    assert "old entry" in target.read_text()


def test_connection_jump_names_extracts_the_hops(stub_project,
                                                 fake_tools,
                                                 fake_binary):
    """The jump hosts come from the '-J' and 'ProxyJump=' options of
    the resolved connection options, in traversal order."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "jumps-inventory",
        "#!/bin/sh\n"
        "printf '%s' '{\"ansible_host\": \"192.0.2.10\","
        " \"ansible_ssh_args\": \"-J bastion,bastion2\","
        " \"ansible_ssh_extra_args\": "
        "\"-o ProxyJump=third@bastion3:2222\"}'\n")
    project = stub_project(raw={"binaries": binaries})
    parameters = resolve_host(project, "web")

    assert connection_jump_names(parameters) == \
        ["bastion", "bastion2", "third@bastion3:2222"]


def test_rescan_hosts_scans_the_jump_before_its_dependents(
        monkeypatch, stub_project, fake_tools, fake_binary, tmp_path):
    """A host whose connection traverses a jump host of the run scans
    after the jump, whatever order the patterns named them in."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "jumped-inventory",
        "#!/bin/sh\n"
        'if [ "$2" = "web" ]; then\n'
        "    printf '%s' '{\"ansible_host\": \"192.0.2.10\","
        " \"ansible_ssh_args\": \"-J jump\"}'\n"
        "else\n"
        "    printf '%s' '{\"ansible_host\": \"192.0.2.20\"}'\n"
        "fi\n")
    binaries["ssh-keyscan"] = fake_binary(
        "jump-keyscan",
        "#!/bin/sh\n"
        'for name in "$@"; do\n'
        '    if [ "$name" = "192.0.2.20" ]; then\n'
        "        printf '%s\\n' '192.0.2.20 ssh-ed25519 AAAAjumpkey'\n"
        "    fi\n"
        "done\n")
    project = stub_project(raw={"binaries": binaries})

    def fake_getaddrinfo(name, *args, **kwargs):
        if name in ("192.0.2.10", "192.0.2.20", "jump"):
            return [(2, 1, 6, "", ("192.0.2.10", 0))]
        raise socket.gaierror("no DNS")

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    store = tmp_path / "store"

    results = rescan_hosts(project, ["web", "jump"], store=str(store),
                           dns_mode='no-dns')

    # The jump is scanned first, its dependents after it
    assert [host for host, _, _ in results] == ["jump", "web"]
    assert results[0][1]
    assert "AAAAjumpkey" in store.read_text()


def test_rescan_hosts_collects_the_keys_through_the_jump(
        monkeypatch, stub_project, fake_tools, fake_binary, tmp_path):
    """When the direct scan of a host behind a jump produces no keys,
    the keys are collected through the connection itself: a throwaway
    known_hosts file pre-seeded with the jump's entries receives the
    key of the negotiated exchange, and the classified keys enter the
    store."""
    binaries = dict(fake_tools["binaries"])
    binaries["ansible-inventory"] = fake_binary(
        "jumped-inventory",
        "#!/bin/sh\n"
        'if [ "$2" = "web" ]; then\n'
        "    printf '%s' '{\"ansible_host\": \"192.0.2.10\","
        " \"ansible_port\": 2222,"
        " \"ansible_ssh_args\": \"-J jump\"}'\n"
        "else\n"
        "    printf '%s' '{\"ansible_host\": \"192.0.2.20\"}'\n"
        "fi\n")
    # The keyscan answers for the jump only; the direct scan of the
    # destination finds nothing
    binaries["ssh-keyscan"] = fake_binary(
        "jump-keyscan",
        "#!/bin/sh\n"
        'for name in "$@"; do\n'
        '    if [ "$name" = "192.0.2.20" ]; then\n'
        "        printf '%s\\n' '192.0.2.20 ssh-ed25519 AAAAjumpkey'\n"
        "    fi\n"
        "done\n")
    # The keygen answers the '-F' lookup of the jump's entries
    binaries["ssh-keygen"] = fake_binary(
        "jump-keygen",
        "#!/bin/sh\n"
        'if [ "$1" = "-F" ]; then\n'
        "    printf '%s\\n' '[192.0.2.20]:2222 ssh-ed25519 AAAAjumpkey'\n"
        "    exit 0\n"
        "fi\n"
        "exit 0\n")
    # The ssh of the connection-scan writes the key of the negotiated
    # exchange into its throwaway known_hosts file and fails the
    # authentication, the way a pre-provisioned host behaves
    binaries["ssh"] = fake_binary(
        "collecting-ssh",
        "#!/bin/sh\n"
        'for name in "$@"; do\n'
        '    case "$name" in\n'
        '        UserKnownHostsFile=*)\n'
        '            printf "%s\\n" "192.0.2.10 ssh-ed25519 '
        'AAAAthroughkey" > "${name#UserKnownHostsFile=}" ;;\n'
        "    esac\n"
        "done\n"
        "exit 255\n")
    project = stub_project(raw={"binaries": binaries})

    def fake_getaddrinfo(name, *args, **kwargs):
        if name in ("192.0.2.10", "192.0.2.20", "jump"):
            return [(2, 1, 6, "", ("192.0.2.10", 0))]
        raise socket.gaierror("no DNS")

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    store = tmp_path / "store"

    results = rescan_hosts(project, ["web"], store=str(store),
                           dns_mode='no-dns')

    host, succeeded, message = results[0]
    assert succeeded
    assert "collected through the connection" in message
    content = store.read_text()
    assert "AAAAthroughkey" in content
    assert "AAAAjumpkey" not in content
