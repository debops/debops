# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""End-to-end tests for the project directory lifecycle."""

import re
import shutil
import socket
import subprocess

import pytest


pytestmark = pytest.mark.integration


ansible_inventory = pytest.mark.skipif(
    shutil.which("ansible-inventory") is None,
    reason="ansible-inventory is not installed")


def _has_network():
    try:
        socket.create_connection(("pypi.org", 443), timeout=5).close()
        return True
    except OSError:
        return False


network = pytest.mark.skipif(not _has_network(),
                             reason="network is not available")


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

    # The PATH entry of the project virtual environment is commented out,
    # as a hint that the environment can be enabled
    environment = (project_dir / ".debops" / "environment").read_text()
    assert "#PATH=${DEBOPS_PROJECT_PATH}/.debops/venv/bin" in environment
    assert not re.search(r"^PATH=", environment, re.MULTILINE)
    assert not environment.endswith("\n\n")


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


def test_init_with_venv_creates_the_venv_files(run_debops, tmp_path,
                                               debops_env):
    project_dir = tmp_path / "example-venv"

    result = run_debops("project", "init", "-t", "modern", "--venv",
                        "--no-requirements", str(project_dir), env=debops_env)

    assert result.returncode == 0
    assert (project_dir / ".debops" / "conf.d" / "venv.yml").exists()
    assert (project_dir / ".debops" / "requirements.txt").exists()
    assert not (project_dir / ".debops" / "venv").exists()

    # The Ansible binaries are pointed at the virtual environment at
    # runtime, based on the configured path
    config = run_debops("config", "get", "binaries.ansible-playbook",
                        cwd=str(project_dir), env=debops_env)
    assert config.stdout.strip() == str(
            project_dir / ".debops" / "venv" / "bin" / "ansible-playbook")

    environment = (project_dir / ".debops" / "environment").read_text()
    assert "#PATH=${DEBOPS_PROJECT_PATH}/.debops/venv/bin" in environment
    assert not re.search(r"^PATH=", environment, re.MULTILINE)
    assert not environment.endswith("\n\n")

    gitignore = (project_dir / ".gitignore").read_text()
    assert "/.debops/venv/" in gitignore

    requirements = (project_dir / "ansible" / "collections"
                    / "requirements.yml").read_text()
    assert "- name: 'debops.debops'" in requirements

    # Packages with missing external build dependencies are commented out
    # with an explanation of what to install (python-ldap on a host without
    # the Python and LDAP development files)
    seed = (project_dir / ".debops" / "requirements.txt").read_text()
    active = re.search(r"^python-ldap$", seed, re.MULTILINE) is not None
    commented = "#python-ldap" in seed
    assert active != commented
    if commented:
        assert "# Skipped: python-ldap" in seed
        assert "install" in seed.split("#python-ldap")[0]

    ansible_cfg = (project_dir / "ansible" / "views" / "system"
                   / "ansible.cfg").read_text()
    assert "collections_path = {}/ansible/collections\n".format(
        project_dir) in ansible_cfg


def test_init_with_venv_rejects_a_legacy_project(run_debops, tmp_path,
                                                 debops_env):
    project_dir = tmp_path / "example-legacy"

    result = run_debops("project", "init", "--venv", str(project_dir),
                        env=debops_env)

    assert result.returncode == 1
    assert "modern" in result.stdout
    assert not project_dir.exists()


def test_venv_enable_activates_an_existing_project(run_debops, tmp_path,
                                                   debops_env):
    project_dir = tmp_path / "example-modern"
    run_debops("project", "init", "-t", "modern", "--no-requirements",
               str(project_dir), env=debops_env, check=True)

    result = run_debops("project", "venv", "install", str(project_dir),
                        env=debops_env)
    assert result.returncode == 1
    assert "not enabled" in result.stdout

    result = run_debops("project", "venv", "enable", str(project_dir),
                        env=debops_env)

    assert result.returncode == 0
    assert "debops project venv install" in result.stdout
    assert (project_dir / ".debops" / "conf.d" / "venv.yml").exists()
    assert (project_dir / ".debops" / "requirements.txt").exists()
    assert not (project_dir / ".debops" / "venv").exists()

    # The Ansible binaries are pointed at the virtual environment at
    # runtime, based on the configured path
    config = run_debops("config", "get", "binaries.ansible-playbook",
                        cwd=str(project_dir), env=debops_env)
    assert config.stdout.strip() == str(
            project_dir / ".debops" / "venv" / "bin" / "ansible-playbook")
    assert "/.debops/venv/" in (project_dir / ".gitignore").read_text()

    # The environment file is not modified; PATH is prepended at runtime
    environment = (project_dir / ".debops" / "environment").read_text()
    assert "#PATH=${DEBOPS_PROJECT_PATH}/.debops/venv/bin" in environment
    assert not re.search(r"^PATH=", environment, re.MULTILINE)

    # The views were switched to project-local Ansible Collections
    view_yml = (project_dir / ".debops" / "conf.d"
                / "view-system.yml").read_text()
    assert ("collections_path: '${DEBOPS_PROJECT_PATH}/ansible/collections'"
            in view_yml)
    ansible_cfg = (project_dir / "ansible" / "views" / "system"
                   / "ansible.cfg").read_text()
    assert "collections_path = {}/ansible/collections\n".format(
        project_dir) in ansible_cfg

    # The pinned 'debops.debops' entry is active in the requirements
    requirements = (project_dir / "ansible" / "collections"
                    / "requirements.yml").read_text()
    assert re.search(r"^  - name: 'debops\.debops'$", requirements,
                     re.MULTILINE)

    # The changes are committed automatically
    log = subprocess.run(["git", "-C", str(project_dir), "status",
                          "--porcelain"], capture_output=True, text=True,
                         check=True)
    assert log.stdout == ""

    # Enabling it again is an idempotent no-op
    result = run_debops("project", "venv", "enable", str(project_dir),
                        env=debops_env)
    assert result.returncode == 0
    assert "already enabled" in result.stdout


@network
def test_venv_install_creates_the_environment(run_debops, tmp_path,
                                              debops_env):
    project_dir = tmp_path / "example-venv"
    run_debops("project", "init", "-t", "modern", "--venv",
               "--no-requirements", str(project_dir), env=debops_env,
               check=True)

    # Install a single small package to keep the test fast
    requirements = project_dir / ".debops" / "requirements.txt"
    requirements.write_text("toml\n")

    result = run_debops("project", "venv", "install", "--python",
                        str(project_dir), env=debops_env)

    assert result.returncode == 0
    assert (project_dir / ".debops" / "venv" / "bin" / "python").exists()
    assert "toml==" in requirements.read_text()

    # The frozen lockfile is committed automatically (git auto-commit)
    status = subprocess.run(["git", "-C", str(project_dir), "status",
                             "--porcelain"], capture_output=True, text=True,
                            check=True)
    assert status.stdout == ""


def _env_var(output, name):
    for line in output.splitlines():
        if line.startswith(name + "="):
            return line.split("=", 1)[1]
    return None


def test_venv_path_is_prepended_at_runtime(run_debops, tmp_path, debops_env):
    project_dir = tmp_path / "example-venv"
    run_debops("project", "init", "-t", "modern", "--venv",
               "--no-requirements", str(project_dir), env=debops_env,
               check=True)

    result = run_debops("env", cwd=str(project_dir), env=debops_env)

    venv_bin = str(project_dir / ".debops" / "venv" / "bin")
    path = _env_var(result.stdout, "PATH")
    assert result.returncode == 0
    assert path is not None
    assert path.split(":")[0] == venv_bin


def test_venv_path_not_prepended_without_venv(run_debops, tmp_path,
                                              debops_env):
    project_dir = tmp_path / "example-plain"
    run_debops("project", "init", "-t", "modern", "--no-requirements",
               str(project_dir), env=debops_env, check=True)

    result = run_debops("env", cwd=str(project_dir), env=debops_env)

    assert result.returncode == 0
    assert _env_var(result.stdout, "PATH") is None


def test_venv_path_respects_a_user_defined_path(run_debops, tmp_path,
                                                debops_env):
    project_dir = tmp_path / "example-venv"
    run_debops("project", "init", "-t", "modern", "--venv",
               "--no-requirements", str(project_dir), env=debops_env,
               check=True)
    environment = project_dir / ".debops" / "environment"
    environment.write_text(environment.read_text()
                           + "\nPATH=/custom/bin:${PATH}\n")

    result = run_debops("env", cwd=str(project_dir), env=debops_env)

    path = _env_var(result.stdout, "PATH")
    assert result.returncode == 0
    assert path.split(":")[0] == "/custom/bin"
    assert ".debops/venv/bin" not in path


@network
def test_venv_can_be_shared_between_projects(run_debops, tmp_path,
                                             debops_env):
    """A venv with an absolute 'project.venv.path' outside of the project
    directory can be shared between multiple projects."""
    shared_venv = tmp_path / "shared-venv"
    projects = []
    for name in ("first", "second"):
        project_dir = tmp_path / name
        run_debops("project", "init", "-t", "modern", "--venv",
                   "--no-requirements", str(project_dir), env=debops_env,
                   check=True)

        # Point the virtual environment at the shared location
        venv_yml = project_dir / ".debops" / "conf.d" / "venv.yml"
        venv_yml.write_text(venv_yml.read_text().replace(
            "path: '.debops/venv'", "path: '{}'".format(shared_venv)))

        # Install a single small package to keep the test fast
        (project_dir / ".debops" / "requirements.txt").write_text("toml\n")
        projects.append(project_dir)

    # The second installation reuses the environment created by the first
    for project_dir in projects:
        result = run_debops("project", "venv", "install", "--python",
                            str(project_dir), env=debops_env)
        assert result.returncode == 0

    assert (shared_venv / "bin" / "python").exists()
    assert not (projects[0] / ".debops" / "venv").exists()

    for project_dir in projects:
        # The Ansible binaries resolve into the shared environment
        config = run_debops("config", "get", "binaries.ansible-playbook",
                            cwd=str(project_dir), env=debops_env)
        assert config.stdout.strip() == str(
                shared_venv / "bin" / "ansible-playbook")

        # The lockfile is pinned and committed (git auto-commit)
        requirements = project_dir / ".debops" / "requirements.txt"
        assert "toml==" in requirements.read_text()
        status = subprocess.run(["git", "-C", str(project_dir), "status",
                                 "--porcelain"], capture_output=True,
                                text=True, check=True)
        assert status.stdout == ""


@network
def test_venv_install_creates_a_collection_lockfile(run_debops, tmp_path,
                                                    debops_env):
    project_dir = tmp_path / "example-venv"
    run_debops("project", "init", "-t", "modern", "--venv",
               "--no-requirements", str(project_dir), env=debops_env,
               check=True)

    # Keep both sides small: ansible-core provides ansible-galaxy
    (project_dir / ".debops" / "requirements.txt").write_text("ansible-core\n")
    (project_dir / "ansible" / "collections" / "requirements.yml").write_text(
            "---\ncollections:\n\n  - name: 'ansible.posix'\n")

    result = run_debops("project", "venv", "install", str(project_dir),
                        env=debops_env)

    assert result.returncode == 0
    lock = project_dir / "ansible" / "collections" / "requirements.lock.yml"
    assert lock.exists()
    content = lock.read_text()
    assert "  - name: 'ansible.posix'" in content
    assert re.search(r"version: '\d+\.\d+\.\d+'", content)

    # The lock file is not ignored by git and is committed (auto-commit)
    ignored = subprocess.run(["git", "-C", str(project_dir), "check-ignore",
                              str(lock)], capture_output=True)
    assert ignored.returncode == 1
    status = subprocess.run(["git", "-C", str(project_dir), "status",
                             "--porcelain"], capture_output=True, text=True,
                            check=True)
    assert status.stdout == ""

    # A recreation reproduces the locked version
    result = run_debops("project", "venv", "recreate", "--collections",
                        str(project_dir), env=debops_env)
    assert result.returncode == 0
    assert lock.read_text() == content

    # A standalone scoped freeze works
    result = run_debops("project", "venv", "freeze", "--collections",
                        str(project_dir), env=debops_env)
    assert result.returncode == 0
    assert lock.read_text() == content
