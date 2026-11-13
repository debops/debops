# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""End-to-end tests for the 'debops sftp' subcommand.

The tests which run a real sftp session need an ssh daemon on
localhost and a working public key authentication to it; they skip
otherwise. The '--eval' tests only compose the command and run
everywhere.
"""

import getpass

import pytest

pytestmark = pytest.mark.integration


def add_inventory_host(project_dir, name="testhost"):
    hosts = (project_dir / "ansible" / "views" / "system" / "inventory" /
             "hosts")
    hosts.write_text(
        hosts.read_text() + "\n" + name
        + " ansible_host=127.0.0.1\n")


def add_ported_inventory_host(project_dir, name="ported"):
    """Add a host on a non-default ssh port with its own user, for the
    '--eval' tests."""
    hosts = (project_dir / "ansible" / "views" / "system" / "inventory" /
             "hosts")
    hosts.write_text(
        hosts.read_text() + "\n" + name
        + " ansible_host=127.0.0.1 ansible_port=2222"
          " ansible_user=operator\n")


def make_project(run_debops, tmp_path, debops_env, name="example-sftp"):
    project_dir = tmp_path / name
    run_debops("project", "init", "-t", "modern", "--no-requirements",
               str(project_dir), env=debops_env, check=True)
    add_inventory_host(project_dir)
    return project_dir


def test_sftp_eval_prints_the_resolved_command(run_debops, tmp_path,
                                               debops_env):
    project_dir = make_project(run_debops, tmp_path, debops_env)
    add_ported_inventory_host(project_dir)

    result = run_debops("sftp", "--eval", "ported",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    assert "operator@127.0.0.1" in result.stdout
    assert "-P" in result.stdout and "2222" in result.stdout


def test_sftp_eval_keeps_the_start_path(run_debops, tmp_path, debops_env):
    project_dir = make_project(run_debops, tmp_path, debops_env)
    add_ported_inventory_host(project_dir)

    result = run_debops("sftp", "--eval", "root@ported:/upload",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    assert "root@127.0.0.1:/upload" in result.stdout


def test_sftp_eval_translates_the_jump(run_debops, tmp_path, debops_env):
    project_dir = make_project(run_debops, tmp_path, debops_env)
    hosts = (project_dir / "ansible" / "views" / "system" / "inventory" /
             "hosts")
    hosts.write_text(
        hosts.read_text()
        + "jumped ansible_host=127.0.0.1 "
          "ansible_ssh_common_args='-J operator@incus.example.org'\n")

    result = run_debops("sftp", "--eval", "jumped",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    assert "-o ProxyJump=operator@incus.example.org" in result.stdout


def test_sftp_batch_session_transfers_a_file(run_debops, tmp_path,
                                             debops_env,
                                             localhost_ssh):
    """A scripted sftp session through the '-b' batch file uploads a
    file to the host, driven by the composed command."""
    project_dir = make_project(run_debops, tmp_path, debops_env)
    local_file = tmp_path / "source.txt"
    local_file.write_text("sftp batch\n")
    batch = tmp_path / "batch"
    batch.write_text("put " + str(local_file) + " /tmp/remote-sftp\n")

    result = run_debops("sftp", "-b", str(batch), "testhost",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0

    back = run_debops("ssh", "testhost", "cat", "/tmp/remote-sftp",
                      cwd=str(project_dir), env=debops_env)
    assert back.stdout == "sftp batch\n"


def test_sftp_accepts_unseen_host_keys(run_debops, tmp_path, debops_env,
                                       localhost_ssh):
    """The '-a/--accept' option lets the first session through against
    a fresh known_hosts store."""
    project_dir = tmp_path / "example-accept"
    run_debops("project", "init", "-t", "modern", "--no-requirements",
               "--ssh", str(project_dir), env=debops_env, check=True)
    add_inventory_host(project_dir)
    batch = tmp_path / "batch"
    batch.write_text("ls /tmp\n")

    result = run_debops("sftp", "-a", "-b", str(batch), "testhost",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    store = (project_dir / ".debops" / "ssh" / "views" / "system" /
             "known_hosts")
    assert store.read_text().strip()
