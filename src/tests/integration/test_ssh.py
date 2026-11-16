# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""End-to-end tests for the 'debops ssh' subcommand.

The tests drive the real command line in temporary project
directories. The '--write' test replaces the HOME of the debops
subprocess with a temporary one; the Python user site-packages
directory is re-added through PYTHONPATH, because a changed HOME hides
it and the package dependencies of the debops command live there.
"""

import os
import shlex
import shutil
import site
import socket
import subprocess
import types

import pytest

pytestmark = pytest.mark.integration


def add_inventory_host(project_dir, name="testhost"):
    """Add one inventory host to the default view of the project."""
    hosts = (project_dir / "ansible" / "views" / "system" / "inventory" /
             "hosts")
    hosts.write_text(
        hosts.read_text() + "\n" + name
        + " ansible_host=127.0.0.1\n")


def sshd_listens():
    """Whether an ssh daemon accepts connections on localhost."""
    try:
        socket.create_connection(("127.0.0.1", 22), timeout=2).close()
        return True
    except OSError:
        return False


def make_project(run_debops, tmp_path, debops_env, name="example-ssh"):
    project_dir = tmp_path / name
    run_debops("project", "init", "-t", "modern", "--no-requirements",
               str(project_dir), env=debops_env, check=True)
    add_inventory_host(project_dir)
    return project_dir


def test_ssh_help_lists_the_subcommands(run_debops, tmp_path, debops_env):
    project_dir = make_project(run_debops, tmp_path, debops_env)

    result = run_debops("ssh", "--help", cwd=str(project_dir),
                        env=debops_env)

    assert result.returncode == 0
    assert "rescan" in result.stdout
    assert "config" in result.stdout
    # The invocation forms of the options are rendered differently by
    # different Python versions; the long names are stable
    assert "--user" in result.stdout
    assert "--port" in result.stdout
    assert "--identity" in result.stdout
    assert "--accept" in result.stdout
    assert "--eval" in result.stdout
    assert "--verbose" in result.stdout
    assert "--project-dir" in result.stdout
    assert "--view" in result.stdout


def test_ssh_without_arguments_shows_the_commands(run_debops, tmp_path,
                                                  debops_env):
    project_dir = make_project(run_debops, tmp_path, debops_env)

    result = run_debops("ssh", cwd=str(project_dir), env=debops_env)

    assert result.returncode == 2
    assert "rescan" in result.stdout
    assert "config" in result.stdout


def test_ssh_eval_prints_the_resolved_command(run_debops, tmp_path,
                                              debops_env):
    project_dir = make_project(run_debops, tmp_path, debops_env)

    result = run_debops("ssh", "--eval", "testhost",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    command = shlex.split(result.stdout)
    assert command[0] == "ssh"
    assert command[-1] == "127.0.0.1"
    # The inventory defines no user; ssh picks one from the operator's
    # SSH client configuration, the way plain ssh does
    assert "-l" not in command
    assert "ConnectTimeout=10" in command


def test_ssh_eval_places_the_remote_command_like_ssh(run_debops, tmp_path,
                                                     debops_env):
    """The arguments after the host follow the destination, the way ssh
    itself places the remote command."""
    project_dir = make_project(run_debops, tmp_path, debops_env)

    result = run_debops("ssh", "--eval", "testhost", "ls", "-l", "/",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    command = shlex.split(result.stdout)
    assert command[command.index("127.0.0.1"):] == \
        ["127.0.0.1", "ls", "-l", "/"]


def test_ssh_eval_splits_the_user_at_destination(run_debops, tmp_path,
                                                 debops_env):
    """The 'user@host' destination form overrides the inventory's
    ansible_user, the way the destination overrides -l in ssh."""
    project_dir = make_project(run_debops, tmp_path, debops_env)

    result = run_debops("ssh", "--eval", "operator@testhost",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    command = shlex.split(result.stdout)
    assert command[command.index("-l") + 1] == "operator"
    assert command[-1] == "127.0.0.1"


def test_ssh_unknown_host_fails(run_debops, tmp_path, debops_env):
    project_dir = make_project(run_debops, tmp_path, debops_env)

    result = run_debops("ssh", "no-such-host",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 1
    assert "Cannot resolve the host" in result.stderr


def test_ssh_rescan_eval_prints_the_actions(run_debops, tmp_path,
                                            debops_env):
    project_dir = make_project(run_debops, tmp_path, debops_env)
    store = tmp_path / "known_hosts"

    result = run_debops("ssh", "rescan", "--eval", "-f", str(store),
                        "testhost", cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    lines = result.stdout.splitlines()
    assert any(line.startswith("ssh-keygen") and "-R testhost" in line
               for line in lines)
    assert any(line.startswith("ssh-keygen") and "-R 127.0.0.1" in line
               for line in lines)
    # The key scan targets the resolvable identifier; the literal name
    # does not resolve and there is nothing to connect to
    assert any(line.startswith("ssh-keyscan") and line.endswith("127.0.0.1")
               for line in lines)
    assert not store.exists(), \
        "the --eval option created the known_hosts store"


def test_ssh_rescan_writes_the_local_host_keys(run_debops, tmp_path,
                                               debops_env):
    if not sshd_listens():
        pytest.skip("no sshd listening on localhost")
    project_dir = make_project(run_debops, tmp_path, debops_env)
    store = tmp_path / "known_hosts"

    result = run_debops("ssh", "rescan", "-f", str(store), "testhost",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    content = store.read_text()
    assert content.strip()
    assert " ssh-" in content, "the store holds no SSH host key"


def test_ssh_config_prints_the_managed_block(run_debops, tmp_path,
                                             debops_env):
    project_dir = make_project(run_debops, tmp_path, debops_env)

    result = run_debops("ssh", "config", cwd=str(project_dir),
                        env=debops_env)

    assert result.returncode == 0
    assert "# BEGIN debops ssh managed block" in result.stdout
    assert "# END debops ssh managed block" in result.stdout


def test_ssh_config_write_manages_the_block(run_debops, tmp_path,
                                            debops_env):
    project_dir = make_project(run_debops, tmp_path, debops_env)
    home = tmp_path / "home"
    home.mkdir()
    env = dict(debops_env, HOME=str(home),
               PYTHONPATH=site.getusersitepackages())

    result = run_debops("ssh", "config", "--write", cwd=str(project_dir),
                        env=env)
    assert result.returncode == 0

    config = home / ".ssh" / "config"
    content = config.read_text()
    assert "# BEGIN debops ssh managed block" in content
    assert "# END debops ssh managed block" in content
    assert "ForwardAgent" not in content  # nothing foreign is touched

    result = run_debops("ssh", "config", "--write", cwd=str(project_dir),
                        env=env)
    assert result.returncode == 0
    assert config.read_text().count(
        "# BEGIN debops ssh managed block") == 1


def test_ssh_project_mode_uses_the_declared_store(run_debops, tmp_path,
                                                  debops_env):
    """In the project known_hosts mode, the store declared in the view's
    configuration is the one the commands operate on."""
    project_dir = make_project(run_debops, tmp_path, debops_env)
    store = (project_dir / ".debops" / "ssh" / "views" / "system" /
             "known_hosts")
    drop_in = project_dir / ".debops" / "conf.d" / "view-system-ssh.toml"
    drop_in.write_text(
        "[views.system.ssh]\n"
        "known_hosts = 'project'\n"
        "\n"
        "[views.system.ansible.ssh_connection]\n"
        "ssh_args = ['-o UserKnownHostsFile=${DEBOPS_PROJECT_PATH}/"
        ".debops/ssh/views/system/known_hosts']\n")
    # The drop-in reaches the generated 'ansible.cfg' when the project
    # configuration is applied again
    run_debops("project", "refresh", cwd=str(project_dir), env=debops_env,
               check=True)

    result = run_debops("ssh", "--eval", "testhost",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    assert "-o UserKnownHostsFile=" + str(store) in result.stdout

    result = run_debops("ssh", "rescan", "--eval", "testhost",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    assert any("-f " + str(store) in line
               for line in result.stdout.splitlines())


def test_init_ssh_activates_the_project_mode(run_debops, tmp_path,
                                             debops_env):
    """'project init --ssh' writes the drop-in before the project
    configuration is merged, so the generated 'ansible.cfg' carries the
    declared store without a refresh."""
    project_dir = tmp_path / "example-ssh-init"
    run_debops("project", "init", "-t", "modern", "--no-requirements",
               "--ssh", str(project_dir), env=debops_env, check=True)
    add_inventory_host(project_dir)
    store = (project_dir / ".debops" / "ssh" / "views" / "system" /
             "known_hosts")

    result = run_debops("ssh", "rescan", "--eval", "testhost",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    assert any("-f " + str(store) in line
               for line in result.stdout.splitlines())


def test_exec_accept_recreates_the_store(run_debops, tmp_path, debops_env,
                                         localhost_ssh):
    """The ansible runners ensure the declared store directory: after
    the store tree is removed, an accepted connection persists the
    host key again."""
    project_dir = tmp_path / "example-recreate"
    run_debops("project", "init", "-t", "modern", "--no-requirements",
               "--ssh", str(project_dir), env=debops_env, check=True)
    add_inventory_host(project_dir)
    shutil.rmtree(project_dir / ".debops" / "ssh")

    result = run_debops("exec", "--accept", "testhost", "-m", "ping",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    store = (project_dir / ".debops" / "ssh" / "views" / "system" /
             "known_hosts")
    assert store.read_text().strip()
    ssh_dir = project_dir / ".debops" / "ssh"
    assert (os.stat(ssh_dir).st_mode & 0o777) == 0o700


def test_ssh_rescan_eval_expands_the_patterns(run_debops, tmp_path,
                                              debops_env):
    """The rescan patterns expand through the inventory: 'all' drives
    the same actions as the explicit host."""
    project_dir = make_project(run_debops, tmp_path, debops_env)
    store = tmp_path / "known_hosts"

    result = run_debops("ssh", "rescan", "--eval", "-f", str(store),
                        "all", cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    lines = result.stdout.splitlines()
    assert any(line.startswith("ssh-keygen") and "-R testhost" in line
               for line in lines)
    assert any(line.startswith("ssh-keyscan")
               and line.endswith("127.0.0.1") for line in lines)


def test_ssh_rejects_the_pattern_destination(run_debops, tmp_path,
                                             debops_env):
    """'all' is not a single-host destination, even on a one-host
    view."""
    project_dir = make_project(run_debops, tmp_path, debops_env)

    result = run_debops("ssh", "all", cwd=str(project_dir),
                        env=debops_env)

    assert result.returncode == 1
    assert "inventory pattern" in result.stderr


def test_ssh_eval_carries_the_options_before_the_host(run_debops, tmp_path,
                                                      debops_env):
    """The ssh options before the destination pass through to ssh in
    front of it."""
    project_dir = make_project(run_debops, tmp_path, debops_env)

    result = run_debops("ssh", "-o", "Foo=1", "--eval", "testhost",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    command = shlex.split(result.stdout)
    assert command[command.index("-o") + 1] == "Foo=1"
    assert command[-1] == "127.0.0.1"


def test_ssh_handoff_passes_the_arguments_to_ssh(run_debops, tmp_path,
                                                 debops_env):
    """The '--' marker hands the rest of the arguments to ssh
    verbatim; the inventory is not consulted."""
    project_dir = make_project(run_debops, tmp_path, debops_env)

    result = run_debops("ssh", "--eval", "--", "--help",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    assert result.stdout.strip() == "ssh --help"


def test_ssh_eval_drops_the_marker_before_the_remote_command(
        run_debops, tmp_path, debops_env):
    """The '--' marker before the remote command separates the
    arguments; the command itself does not carry it."""
    project_dir = make_project(run_debops, tmp_path, debops_env)

    result = run_debops("ssh", "--eval", "testhost", "--", "ls", "-l",
                        "/", cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    command = shlex.split(result.stdout)
    assert command[command.index("127.0.0.1"):] == \
        ["127.0.0.1", "ls", "-l", "/"]


def make_jump_project(run_debops, tmp_path, debops_env, jump_port,
                      target_port):
    """A project in the project known_hosts mode with a jump setup.

    The 'bastion' host listens on the jump port, the 'behind' host on
    the target port; the connection to 'behind' is declared to
    traverse the bastion through the '-J' option of the inventory.
    Both daemons run on 127.0.0.1 of the machine running the tests.
    """
    project_dir = tmp_path / "example-jump"
    run_debops("project", "init", "-t", "modern", "--no-requirements",
               "--ssh", str(project_dir), env=debops_env, check=True)
    hosts = (project_dir / "ansible" / "views" / "system" / "inventory" /
             "hosts")
    hosts.write_text(
        "[debops_all_hosts]\n"
        "bastion ansible_host=127.0.0.1 ansible_port="
        + str(jump_port) + "\n"
        "behind ansible_host=127.0.0.1 ansible_port=" + str(target_port)
        + " ansible_ssh_common_args='-J 127.0.0.1:" + str(jump_port)
        + "'\n")
    return project_dir


def jump_store(project_dir):
    """The project known_hosts store of the jump project."""
    return (project_dir / ".debops" / "ssh" / "views" / "system" /
            "known_hosts")


def user_known_hosts_snapshot():
    """The bytes of the operator's own known_hosts file, for the tests
    which assert that nothing writes into it."""
    path = os.path.expanduser("~/.ssh/known_hosts")
    try:
        with open(path, "rb") as handle:
            return handle.read()
    except FileNotFoundError:
        return b""


def store_has_entry(store, identifier):
    """Whether the store holds an entry for the given identifier.

    The store entries carry hashed host names, so the presence of an
    entry is probed the way the suite itself probes it, with
    'ssh-keygen -F'.
    """
    probe = subprocess.run(
        ["ssh-keygen", "-F", identifier, "-f", str(store)],
        capture_output=True, text=True)
    return probe.returncode == 0 and bool(probe.stdout.strip())


def test_jump_pair_daemons_authenticate(jump_pair):
    """The spawned daemons of the jump pair accept the public key of
    the account running the tests."""
    for port in (jump_pair.bastion_port, jump_pair.target_port):
        subprocess.run(
            ["ssh", "-o", "BatchMode=yes",
             "-o", "UserKnownHostsFile=" + jump_pair.throwaway,
             "-o", "StrictHostKeyChecking=no",
             "-p", str(port), "127.0.0.1", "true"], check=True)


def test_ssh_session_through_the_jump_verifies_against_the_store(
        run_debops, tmp_path, debops_env, jump_pair):
    """A session behind a jump host verifies the jump host against the
    store of the view, not against the operator's own known_hosts."""
    project_dir = make_jump_project(run_debops, tmp_path, debops_env,
                                    jump_pair.bastion_port,
                                    jump_pair.target_port)
    store = jump_store(project_dir)
    before = user_known_hosts_snapshot()

    result = run_debops("ssh", "rescan", "all", cwd=str(project_dir),
                        env=debops_env)
    assert result.returncode == 0, result.stderr

    assert store_has_entry(store, "[127.0.0.1]:"
                           + str(jump_pair.bastion_port)), \
        "the store holds no key of the jump host"
    assert store_has_entry(store, "[127.0.0.1]:"
                           + str(jump_pair.target_port)), \
        "the store holds no key of the host behind the jump"
    assert user_known_hosts_snapshot() == before, \
        "the rescan wrote into the operator's own known_hosts file"

    result = run_debops("ssh", "behind", "--", "true",
                        cwd=str(project_dir), env=debops_env)
    assert result.returncode == 0, result.stderr
    assert user_known_hosts_snapshot() == before, \
        "the session wrote into the operator's own known_hosts file"


def test_ssh_accept_through_the_jump_stores_both_keys(
        run_debops, tmp_path, debops_env, jump_pair):
    """'--accept' covers the jump host as well: the first contact
    through an untrusted bastion stores the keys of both legs of the
    connection in the store of the view."""
    project_dir = make_jump_project(run_debops, tmp_path, debops_env,
                                    jump_pair.bastion_port,
                                    jump_pair.target_port)
    store = jump_store(project_dir)
    before = user_known_hosts_snapshot()

    result = run_debops("ssh", "--accept", "behind", "--", "true",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0, result.stderr
    assert store_has_entry(store, "[127.0.0.1]:"
                           + str(jump_pair.bastion_port)), \
        "the accepted connection stored no key of the jump host"
    assert store_has_entry(store, "[127.0.0.1]:"
                           + str(jump_pair.target_port)), \
        "the accepted connection stored no key of the host behind it"
    assert user_known_hosts_snapshot() == before, \
        "the accepted connection wrote into the operator's known_hosts"


def test_connection_scan_through_the_jump_collects_the_target_key(
        run_debops, tmp_path, debops_env, jump_pair, monkeypatch):
    """The connection-based scan behind a jump host verifies the jump
    against the entries it carries and completes without a prompt.

    The direct keyscan of the hermetic pair always answers, so the
    fallback of the rescan cannot be driven through the command line;
    the scan function itself runs against the real daemons and the
    real ssh client instead.
    """
    import debops.core.ssh.ssh as ssh_module

    project_dir = make_jump_project(run_debops, tmp_path, debops_env,
                                    jump_pair.bastion_port,
                                    jump_pair.target_port)
    store = jump_store(project_dir)

    result = run_debops("ssh", "rescan", "bastion", cwd=str(project_dir),
                        env=debops_env)
    assert result.returncode == 0, result.stderr
    assert store_has_entry(store, "[127.0.0.1]:"
                           + str(jump_pair.bastion_port))

    monkeypatch.setattr(ssh_module, "ssh_executable", lambda project: None)
    binaries = {name: shutil.which(name)
                for name in ("ssh", "ssh-keygen", "ssh-keyscan")}
    project_stub = types.SimpleNamespace(config=types.SimpleNamespace(
        raw={"binaries": binaries}))
    parameters = {
        "destination": "127.0.0.1",
        "port": str(jump_pair.target_port),
        "ssh_args": "-J 127.0.0.1:" + str(jump_pair.bastion_port),
        "common_args": None,
        "extra_args": None,
    }
    details = []
    keys = ssh_module._collect_through_connection(
        project_stub, parameters, str(store), 5, details)

    assert keys, details
    # The accepted entries are hashed by the client configuration, so
    # the identity of the collected key is probed the way the suite
    # probes stores, with 'ssh-keygen -F'
    scanned = tmp_path / "scanned-keys"
    scanned.write_text("\n".join(keys) + "\n")
    probe = subprocess.run(
        ["ssh-keygen", "-F", "[127.0.0.1]:" + str(jump_pair.target_port),
         "-f", str(scanned)], capture_output=True, text=True)
    assert probe.returncode == 0 and probe.stdout.strip(), \
        "the collected keys carry no entry of the host behind the jump"
