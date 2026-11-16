# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Fixtures for the integration tests.

The tests drive the real ``debops`` command line in temporary directories.
``XDG_CONFIG_HOME`` is pointed at an empty directory so that the
configuration and the hook scripts of the machine running the tests cannot
leak in; ``HOME`` is left alone so that the Python user site packages stay
importable.
"""

import os
import shutil
import socket
import subprocess
import time

import pytest


@pytest.fixture
def debops_env(tmp_path):
    """Environment overrides which keep the debops subprocess hermetic.

    The git identity used for the commits made by the project initialization
    is provided through the environment, which keeps the tests independent
    of the git configuration of the machine running them; the global and the
    system git configuration are disabled entirely, so that settings such as
    commit signing cannot break the commits made by git-crypt.
    """
    config_home = tmp_path / "config"
    config_home.mkdir()
    return {
        "XDG_CONFIG_HOME": str(config_home),
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_AUTHOR_NAME": "DebOps Tests",
        "GIT_AUTHOR_EMAIL": "debops-tests@example.org",
        "GIT_COMMITTER_NAME": "DebOps Tests",
        "GIT_COMMITTER_EMAIL": "debops-tests@example.org",
    }


@pytest.fixture
def gpg_env(debops_env, tmp_path):
    """A hermetic GnuPG home directory with a single test key.

    Secret encryption needs a key to encrypt to; generating one for each test
    keeps the machine keyring untouched.
    """
    if shutil.which("gpg") is None:
        pytest.skip("gpg is not installed")

    gnupg = tmp_path / "gnupg"
    gnupg.mkdir(mode=0o700)
    env = dict(debops_env, GNUPGHOME=str(gnupg))
    subprocess.run(
        ["gpg", "--batch", "--pinentry-mode", "loopback", "--passphrase", "",
         "--quick-gen-key", "DebOps Tests <debops-tests@example.org>",
         "default", "default", "never"],
        env={**os.environ, **env}, check=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return env


@pytest.fixture
def localhost_ssh():
    """Skip unless ssh authenticates to localhost without a prompt.

    The file-transfer and session tests drive real connections to
    127.0.0.1; they need an ssh daemon and a public key the daemon
    accepts, which not every host that runs the suite has.
    """
    try:
        result = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=3",
             "127.0.0.1", "true"], capture_output=True, timeout=10)
        if result.returncode != 0:
            pytest.skip("ssh does not authenticate to localhost")
    except (OSError, subprocess.SubprocessError):
        pytest.skip("ssh does not authenticate to localhost")


class JumpPair:
    """The two spawned ssh daemons of the jump-host tests.

    'bastion_port' is the port of the jump host, 'target_port' the
    port of the host behind it, and 'throwaway' the path of an empty
    known_hosts file for connections which must not establish trust.
    """

    def __init__(self, bastion_port, target_port, throwaway):
        self.bastion_port = bastion_port
        self.target_port = target_port
        self.throwaway = str(throwaway)


def _sshd_binary():
    for candidate in (shutil.which("sshd"), "/usr/sbin/sshd",
                      "/usr/local/sbin/sshd"):
        if candidate and os.path.isfile(candidate):
            return candidate
    return None


def _free_port():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _spawn_sshd(tmp_path, tag, port, allow_forwarding):
    """Spawn one unprivileged ssh daemon on the given loopback port.

    The daemon runs as the account running the tests, with a fresh
    host key and a private copy of the authorized keys of the
    operator's own account, so the connections authenticate the way
    the localhost tests do without following the live auth state of
    the operator's own daemon. The fresh host key is trusted by
    neither the operator's own known_hosts file nor any store of the
    tests. TTY allocation is disabled, which the tests do not need;
    the forwarding is disabled on the target daemon only -- the
    bastion's job is the stdio forwarding the jump connections use.
    """
    host_key = tmp_path / ("sshd-" + tag + "-hostkey")
    subprocess.run(
        ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(host_key)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    keys_copy = tmp_path / ("authorized-keys-" + tag)
    shutil.copyfile(os.path.expanduser("~/.ssh/authorized_keys"), keys_copy)
    os.chmod(keys_copy, 0o600)
    config = tmp_path / ("sshd-" + tag + ".conf")
    config.write_text(
        "Port {port}\n"
        "ListenAddress 127.0.0.1\n"
        "HostKey {host_key}\n"
        "PidFile {pid}\n"
        "AuthorizedKeysFile {keys}\n"
        "PasswordAuthentication no\n"
        "KbdInteractiveAuthentication no\n"
        "PubkeyAuthentication yes\n"
        "{forwarding}"
        "PermitTTY no\n"
        # The authorized keys live under the pytest temporary
        # directory, whose ancestors carry the sticky bit of /tmp; the
        # strict ownership walk of sshd would refuse the keys there.
        # The daemon is ours, listens on the loopback alone and
        # carries a key no store trusts, so the strictness has
        # nothing to enforce
        "StrictModes no\n"
        "UsePAM no\n"
        "LogLevel ERROR\n"
        "Subsystem sftp internal-sftp\n".format(
            port=port, host_key=host_key,
            pid=tmp_path / ("sshd-" + tag + ".pid"),
            keys=keys_copy,
            forwarding="" if allow_forwarding
            else "DisableForwarding yes\n"))
    log = tmp_path / ("sshd-" + tag + ".log")
    return subprocess.Popen(
        [_sshd_binary(), "-D", "-f", str(config), "-E", str(log)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _await_daemon(process, port, throwaway, deadline=15.0):
    """Return when the daemon authenticates a public key connection.

    The probe carries a throwaway known_hosts file and disables the
    strict checking, so the readiness check itself establishes no
    trust anywhere.
    """
    limit = time.monotonic() + deadline
    command = ["ssh", "-o", "BatchMode=yes",
               "-o", "StrictHostKeyChecking=no",
               "-o", "UserKnownHostsFile=" + str(throwaway),
               "-o", "ConnectTimeout=1", "-p", str(port),
               "127.0.0.1", "true"]
    while time.monotonic() < limit:
        if process.poll() is not None:
            raise RuntimeError("the ssh daemon exited with status "
                               + str(process.returncode))
        probe = subprocess.run(command, capture_output=True, timeout=5)
        if probe.returncode == 0:
            return
        time.sleep(0.25)
    raise RuntimeError("the ssh daemon on port " + str(port)
                       + " did not accept connections")


def _start_daemon(tmp_path, tag, throwaway):
    """Start one daemon, retrying the transient port collisions.

    Every attempt regenerates the daemon's files under a unique tag,
    so a retry never collides with the files of the attempt before it.
    """
    last_error = None
    for attempt in range(3):
        port = _free_port()
        process = None
        try:
            process = _spawn_sshd(tmp_path, tag + "-" + str(attempt), port,
                                  allow_forwarding=(tag == "bastion"))
            _await_daemon(process, port, throwaway)
        except subprocess.SubprocessError as error:
            # The daemon could not be spawned; an environment problem
            raise
        except RuntimeError as error:
            last_error = error
            if process.poll() is None:
                process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            if process.poll() is not None:
                # The daemon exited on its own; a likely collision with
                # another listener -- the next attempt may win the port
                continue
            raise
        return process, port
    raise RuntimeError("the ssh daemon of the jump pair did not come up: "
                       + str(last_error))


@pytest.fixture
def jump_pair(tmp_path, localhost_ssh):
    """Two ssh daemons on distinct loopback ports with fresh host keys.

    The first daemon plays the jump host, the second the host behind
    it. The fixture requires the same public key setup as the
    'localhost_ssh' fixture: the daemons authorize the keys of the
    account running the tests.
    """
    sshd = _sshd_binary()
    keys_file = os.path.expanduser("~/.ssh/authorized_keys")
    if sshd is None:
        pytest.skip("no ssh daemon binary for the jump pair")
    if not os.path.exists(keys_file):
        pytest.skip("no authorized keys for the jump pair")
    throwaway = tmp_path / "throwaway-known-hosts"
    throwaway.write_text("")
    daemons = []
    try:
        ports = []
        try:
            for tag in ("bastion", "target"):
                process, port = _start_daemon(tmp_path, tag, throwaway)
                daemons.append(process)
                ports.append(port)
        except (RuntimeError, subprocess.SubprocessError):
            pytest.skip("the ssh daemons of the jump pair did not come up")
        yield JumpPair(ports[0], ports[1], throwaway)
    finally:
        for process in daemons:
            process.terminate()
        for process in daemons:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
