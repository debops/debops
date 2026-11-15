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
import getpass
import hashlib
import os
import socket
from unittest import mock

import pytest

import debops.core.ssh as ssh_module
from debops.core.ssh import (SFTP_OPTIONS_WITH_VALUE, SSH_OPTIONS_WITH_VALUE,
                             build_handoff_command, build_ssh_command,
                             ensure_store_dir, host_identifiers,
                             known_hosts_mode, known_hosts_store,
                             render_config_snippet, resolve_destination,
                             resolve_host, resolve_patterns, rescan_hosts,
                             split_destination, split_options_operand,
                             translate_ssh_args, value_options_of,
                             write_config_snippet)


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

    command = build_ssh_command(project, "plain", user="operator",
                                port=2200)

    assert command == ["/usr/bin/ssh", "-l", "operator", "-p", "2200",
                       "plain"]


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
    ssh itself places the remote command and its arguments."""
    project = stub_project(raw={"binaries": dict(fake_tools["binaries"])})

    command = build_ssh_command(project, "web",
                                ssh_args=["uptime"])

    assert command == ["/usr/bin/ssh", "-l", getpass.getuser(),
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
    assert any("-R web" in line for line in removals)
    assert any("-R 192.0.2.10" in line for line in removals)


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


def test_split_options_operand_walks_the_options():
    head, operand, tail = split_options_operand(
        ["-o", "Foo=1", "-v", "host", "cmd"], SSH_OPTIONS_WITH_VALUE)

    assert head == ["-o", "Foo=1", "-v"]
    assert operand == "host"
    assert tail == ["cmd"]


def test_split_options_operand_handles_attached_values():
    head, operand, tail = split_options_operand(
        ["-oFoo=1", "host"], SSH_OPTIONS_WITH_VALUE)

    assert head == ["-oFoo=1"]
    assert operand == "host"
    assert tail == []


def test_split_options_operand_ends_the_options_at_the_marker():
    head, operand, tail = split_options_operand(
        ["--", "-weird", "rest"], SSH_OPTIONS_WITH_VALUE)

    assert head == []
    assert operand == "-weird"
    assert tail == ["rest"]


def test_split_options_operand_consumes_the_long_values():
    head, operand, tail = split_options_operand(
        ["--view", "system", "host"], SSH_OPTIONS_WITH_VALUE,
        ("--view",))

    assert head == ["--view", "system"]
    assert operand == "host"


def test_split_options_operand_reports_a_missing_operand():
    head, operand, tail = split_options_operand(["-v"], SSH_OPTIONS_WITH_VALUE)

    assert head == ["-v"]
    assert operand is None
    assert tail == []


def test_split_options_operand_keeps_the_sftp_batch_value():
    """The '-b' option of sftp takes a value; the batch file is not
    mistaken for the destination."""
    head, operand, tail = split_options_operand(
        ["-b", "/tmp/batch", "host"], SFTP_OPTIONS_WITH_VALUE)

    assert head == ["-b", "/tmp/batch"]
    assert operand == "host"
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
    stub_dns(monkeypatch, {(4, FQDN_FINGERPRINT)}, authenticated=True)
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
    stub_dns(monkeypatch, {(4, 'ff' * 32)}, authenticated=True)
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
    stub_dns(monkeypatch, {(4, FQDN_FINGERPRINT)}, authenticated=False)
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
    stub_dns(monkeypatch, {(4, FQDN_FINGERPRINT)}, authenticated=True)
    store = tmp_path / "store"

    results = rescan_hosts(project, ["web"], store=str(store),
                           phases=("scan",), dns_mode='dns-verify')

    assert results[0][1]
    assert FQDN_KEY_LINE in store.read_text()


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
