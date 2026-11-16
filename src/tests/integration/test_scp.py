# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""End-to-end tests for the 'debops scp' subcommand.

The tests which copy files need an ssh daemon on localhost and a
working public key authentication to it; they skip otherwise. The
'--eval' tests only compose the command and run everywhere.
"""

import shlex
import socket
import subprocess

import pytest

pytestmark = pytest.mark.integration


def add_inventory_host(project_dir, name="testhost"):
    hosts = (project_dir / "ansible" / "views" / "system" / "inventory" /
             "hosts")
    hosts.write_text(
        hosts.read_text() + "\n" + name
        + " ansible_host=127.0.0.1\n")


def make_project(run_debops, tmp_path, debops_env, name="example-scp"):
    project_dir = tmp_path / name
    run_debops("project", "init", "-t", "modern", "--no-requirements",
               str(project_dir), env=debops_env, check=True)
    add_inventory_host(project_dir)
    return project_dir


def test_scp_help_carries_the_connection_note(run_debops, tmp_path,
                                              debops_env):
    project_dir = make_project(run_debops, tmp_path, debops_env)

    result = run_debops("scp", "--help", cwd=str(project_dir),
                        env=debops_env)

    assert result.returncode == 0
    assert "apply to both connections" in result.stdout
    assert "~/.ssh/config" in result.stdout


def test_scp_eval_prints_the_resolved_command(run_debops, tmp_path,
                                              debops_env):
    project_dir = make_project(run_debops, tmp_path, debops_env)

    result = run_debops("scp", "--eval", "/tmp/local-file",
                        "testhost:/tmp/remote-file",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    assert "127.0.0.1:/tmp/remote-file" in result.stdout


def test_scp_eval_keeps_the_operand_user(run_debops, tmp_path, debops_env):
    project_dir = make_project(run_debops, tmp_path, debops_env)

    result = run_debops("scp", "--eval", "/tmp/local-file",
                        "operator@testhost:/tmp/remote-file",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    assert "operator@127.0.0.1:/tmp/remote-file" in result.stdout


def test_scp_eval_translates_the_jump(run_debops, tmp_path, debops_env):
    project_dir = make_project(run_debops, tmp_path, debops_env)
    hosts = (project_dir / "ansible" / "views" / "system" / "inventory" /
             "hosts")
    hosts.write_text(
        hosts.read_text()
        + "testhost ansible_host=127.0.0.1 "
          "ansible_ssh_common_args='-J operator@incus.example.org'\n")

    result = run_debops("scp", "--eval", "/tmp/local-file",
                        "testhost:/tmp/remote-file",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    command = shlex.split(result.stdout)
    assert "ProxyCommand=ssh -W '[%h]:%p' operator@incus.example.org" \
        in command


def test_scp_copies_a_file_to_the_host(run_debops, tmp_path, debops_env,
                                       localhost_ssh):
    project_dir = make_project(run_debops, tmp_path, debops_env)
    local_file = tmp_path / "source.txt"
    local_file.write_text("copy me\n")

    result = run_debops("scp", str(local_file), "testhost:/tmp/remote-copy",
                        cwd=str(project_dir), env=debops_env)
    assert result.returncode == 0

    back = run_debops("ssh", "testhost", "cat", "/tmp/remote-copy",
                      cwd=str(project_dir), env=debops_env)
    assert back.stdout == "copy me\n"


def test_scp_fetches_a_file_from_the_host(run_debops, tmp_path,
                                          debops_env, localhost_ssh):
    project_dir = make_project(run_debops, tmp_path, debops_env)
    local_file = tmp_path / "source.txt"
    local_file.write_text("fetch me\n")
    run_debops("scp", str(local_file), "testhost:/tmp/remote-fetch",
               cwd=str(project_dir), env=debops_env, check=True)

    fetched = tmp_path / "fetched.txt"
    result = run_debops("scp", "testhost:/tmp/remote-fetch", str(fetched),
                        cwd=str(project_dir), env=debops_env)
    assert result.returncode == 0
    assert fetched.read_text() == "fetch me\n"


def test_scp_accepts_unseen_host_keys(run_debops, tmp_path, debops_env,
                                      localhost_ssh):
    """The '-a/--accept' option lets the copy through on the first
    contact with a fresh known_hosts store."""
    project_dir = tmp_path / "example-accept"
    run_debops("project", "init", "-t", "modern", "--no-requirements",
               "--ssh", str(project_dir), env=debops_env, check=True)
    add_inventory_host(project_dir)
    local_file = tmp_path / "source.txt"
    local_file.write_text("first contact\n")

    result = run_debops("scp", "--accept", str(local_file),
                        "testhost:/tmp/remote-first",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    store = (project_dir / ".debops" / "ssh" / "views" / "system" /
             "known_hosts")
    assert store.read_text().strip()


def test_scp_copies_multiple_files_to_the_host(run_debops, tmp_path,
                                               debops_env, localhost_ssh):
    """Several local sources copy to the host in one command."""
    project_dir = make_project(run_debops, tmp_path, debops_env)
    first = tmp_path / "scp-multi-first.txt"
    first.write_text("one\n")
    second = tmp_path / "scp-multi-second.txt"
    second.write_text("two\n")

    result = run_debops("scp", str(first), str(second), "testhost:/tmp/",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0

    back = run_debops("ssh", "testhost", "cat", "/tmp/scp-multi-first.txt",
                      cwd=str(project_dir), env=debops_env)
    assert back.stdout == "one\n"
    back = run_debops("ssh", "testhost", "cat", "/tmp/scp-multi-second.txt",
                      cwd=str(project_dir), env=debops_env)
    assert back.stdout == "two\n"
