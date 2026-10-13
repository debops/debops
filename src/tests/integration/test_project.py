# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""End-to-end tests for the project directory lifecycle."""

import shutil
import subprocess

import pytest


pytestmark = pytest.mark.integration


ansible_inventory = pytest.mark.skipif(
    shutil.which("ansible-inventory") is None,
    reason="ansible-inventory is not installed")


def test_init_creates_a_legacy_project(run_debops, tmp_path, debops_env):
    project_dir = tmp_path / "example-legacy"

    result = run_debops("project", "init", "--no-requirements",
                        str(project_dir), env=debops_env)

    assert result.returncode == 0
    assert (project_dir / "ansible.cfg").exists()
    assert (project_dir / ".debops.cfg").exists()
    assert (project_dir / "ansible" / "inventory" / "hosts").exists()
    assert (project_dir / ".git").is_dir()

    log = subprocess.run(["git", "-C", str(project_dir), "log", "--oneline"],
                         capture_output=True, text=True, check=True)
    assert "Initialize new DebOps project" in log.stdout


def test_init_creates_a_modern_project(run_debops, tmp_path, debops_env):
    project_dir = tmp_path / "example-modern"

    result = run_debops("project", "init", "-t", "modern", "-V", "webservers",
                        "--no-requirements", str(project_dir), env=debops_env)

    assert result.returncode == 0
    assert (project_dir / ".debops" / "conf.d" / "project.yml").exists()
    assert (project_dir / ".debops" / "conf.d"
            / "view-webservers.yml").exists()
    assert (project_dir / "ansible" / "views" / "webservers"
            / "ansible.cfg").exists()
    assert (project_dir / "ansible" / "views" / "webservers" / "inventory"
            / "hosts").exists()
    assert (project_dir / ".git").is_dir()


def test_init_without_git_support(run_debops, tmp_path, debops_env):
    project_dir = tmp_path / "example-nogit"

    result = run_debops("project", "init", "--no-git", "--no-requirements",
                        str(project_dir), env=debops_env)

    assert result.returncode == 0
    assert (project_dir / "ansible.cfg").exists()
    assert not (project_dir / ".git").exists()


def test_init_refuses_a_directory_inside_a_project(run_debops, tmp_path,
                                                   debops_env):
    project_dir = tmp_path / "example"
    run_debops("project", "init", "--no-requirements", str(project_dir),
               env=debops_env, check=True)

    result = run_debops("project", "init", "--no-requirements",
                        str(project_dir / "nested"), env=debops_env)

    assert result.returncode == 1
    assert "inside another" in result.stdout


def test_mkview_creates_an_additional_view(run_debops, tmp_path, debops_env):
    project_dir = tmp_path / "example-modern"
    run_debops("project", "init", "-t", "modern", "--no-requirements",
               str(project_dir), env=debops_env, check=True)

    result = run_debops("project", "mkview", "databases",
                        cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    assert (project_dir / "ansible" / "views" / "databases" / "inventory"
            / "hosts").exists()


def test_refresh_updates_the_project(run_debops, tmp_path, debops_env):
    project_dir = tmp_path / "example"
    run_debops("project", "init", "--no-requirements", str(project_dir),
               env=debops_env, check=True)

    result = run_debops("project", "refresh", str(project_dir),
                        env=debops_env)

    assert result.returncode == 0
    assert "Refreshed DebOps project" in result.stdout


@ansible_inventory
def test_refresh_can_inspect_the_inventory_graph(run_debops, tmp_path,
                                                 debops_env):
    project_dir = tmp_path / "example"
    run_debops("project", "init", "--no-requirements", str(project_dir),
               env=debops_env, check=True)

    result = run_debops("project", "refresh", "--graph", str(project_dir),
                        env=debops_env)

    assert result.returncode == 0
    assert "@all" in result.stdout
    assert "@debops_all_hosts" in result.stdout
