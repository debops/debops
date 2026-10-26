# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""End-to-end tests for the project directory lifecycle."""

import json
import os
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


def test_init_installs_collections_with_a_stub_galaxy(run_debops, tmp_path,
                                                      debops_env):
    log = tmp_path / "galaxy.log"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stub = bin_dir / "ansible-galaxy"
    stub.write_text('#!/bin/sh\necho "$PWD" "$@" >> "{}"\n'.format(log))
    stub.chmod(0o755)
    env = dict(debops_env,
               PATH=os.pathsep.join([str(bin_dir), os.environ["PATH"]]))
    project_dir = tmp_path / "example"

    result = run_debops("project", "init", str(project_dir), env=env)

    assert result.returncode == 0
    invocation = log.read_text()
    assert "collection install -r" in invocation
    assert "ansible/collections/requirements.yml" in invocation


def test_init_reports_a_missing_galaxy_binary(run_debops, tmp_path,
                                              debops_env):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "git").symlink_to(shutil.which("git"))
    env = dict(debops_env, PATH=str(bin_dir))
    project_dir = tmp_path / "example"

    result = run_debops("project", "init", "-v", str(project_dir), env=env)

    assert result.returncode == 0
    assert "ansible-galaxy not available in $PATH" in error_message(result)


def test_init_git_crypt_without_keys_reports_an_error(run_debops, tmp_path,
                                                      debops_env):
    project_dir = tmp_path / "example"

    result = run_debops("project", "init", "--encrypt", "git-crypt",
                        "--no-requirements", str(project_dir),
                        env=debops_env)

    assert result.returncode == 1
    assert "GPG recipients" in error_message(result)


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


def test_init_with_template_reports_created_paths(run_debops, tmp_path,
                                                  debops_env):
    project_dir = tmp_path / "example-modern"

    result = run_debops("project", "init", "-t", "modern", "-v",
                        "--no-requirements", "--template", "hosts",
                        str(project_dir), env=debops_env)

    assert result.returncode == 0
    output = error_message(result)
    assert "Created hosts" in output
    assert "Created group_vars/webservers" in output
    assert "Applied the inventory specification." in result.stdout
    hosts = (project_dir / "ansible" / "views" / "system" / "inventory"
             / "hosts")
    assert "[webservers]" in hosts.read_text()


def test_refresh_with_template_reports_skipped_paths(run_debops, tmp_path,
                                                     debops_env):
    project_dir = tmp_path / "example-modern"
    run_debops("project", "init", "-t", "modern", "--no-requirements",
               "--template", "hosts", str(project_dir), env=debops_env,
               check=True)
    hosts = (project_dir / "ansible" / "views" / "system" / "inventory"
             / "hosts")
    before = hosts.read_text()

    result = run_debops("project", "refresh", "-v", "--template", "hosts",
                        str(project_dir), env=debops_env)

    assert result.returncode == 0
    assert "Skipped existing hosts" in error_message(result)
    assert ("Use '--force' to overwrite or remove paths which already exist."
            in result.stdout)
    assert hosts.read_text() == before


def test_refresh_dry_run_reports_planned_paths(run_debops, tmp_path,
                                               debops_env):
    project_dir = tmp_path / "example-modern"
    run_debops("project", "init", "-t", "modern", "--no-requirements",
               str(project_dir), env=debops_env, check=True)
    spec = tmp_path / "dry-run.yml"
    spec.write_text("version: 0\n"
                    "files:\n"
                    "  group_vars/dryrun/: ''\n"
                    "  hosts_dryrun: |\n"
                    "    [dryrun]\n"
                    "    dry1\n")

    result = run_debops("project", "refresh", "-n", "-vv", "--template",
                        str(spec), str(project_dir), env=debops_env)

    assert result.returncode == 0
    output = error_message(result)
    assert "Would create group_vars/dryrun" in output
    assert "Would create hosts_dryrun" in output
    assert "Inventory specification will not be written to disk" in output
    assert "Applied the inventory specification." not in result.stdout
    inventory = (project_dir / "ansible" / "views" / "system" / "inventory")
    assert not (inventory / "group_vars" / "dryrun").exists()
    assert not (inventory / "hosts_dryrun").exists()


def test_refresh_force_reports_removals_and_kept_paths(run_debops, tmp_path,
                                                       debops_env):
    project_dir = tmp_path / "example-modern"
    run_debops("project", "init", "-t", "modern", "--no-requirements",
               "--template", "hosts", str(project_dir), env=debops_env,
               check=True)

    result = run_debops("project", "refresh", "--force", "-v", "--template",
                        "clear", str(project_dir), env=debops_env)

    assert result.returncode == 0
    output = error_message(result)
    assert "Removed group_vars/all/sshd.yml" in output
    assert "Created host_vars" in output
    assert "Kept group_vars/all/keyring.yml" in output
    assert "Applied the inventory specification." in result.stdout


def test_refresh_dry_run_reports_planned_removals(run_debops, tmp_path,
                                                  debops_env):
    project_dir = tmp_path / "example-modern"
    run_debops("project", "init", "-t", "modern", "--no-requirements",
               "--template", "hosts", str(project_dir), env=debops_env,
               check=True)
    inventory = (project_dir / "ansible" / "views" / "system" / "inventory")
    hosts = inventory / "hosts"
    before = hosts.read_text()

    result = run_debops("project", "refresh", "-n", "--force", "-v",
                        "--template", "clear", str(project_dir),
                        env=debops_env)

    assert result.returncode == 0
    assert "Would remove group_vars/all/sshd.yml" in error_message(result)
    assert "Applied the inventory specification." not in result.stdout
    assert hosts.read_text() == before


@ansible_inventory
def test_refresh_inspects_inventory_as_list(run_debops, tmp_path, debops_env):
    project_dir = tmp_path / "example-modern"
    run_debops("project", "init", "-t", "modern", "--no-requirements",
               "--template", "hosts", str(project_dir), env=debops_env,
               check=True)

    result = run_debops("project", "refresh", "--list", str(project_dir),
                        env=debops_env)

    assert result.returncode == 0
    inventory = json.loads(result.stdout)
    assert inventory["webservers"]["hosts"] == ["web1", "web2"]
    assert "web1" in inventory["_meta"]["hostvars"]


@ansible_inventory
def test_refresh_inspects_one_host(run_debops, tmp_path, debops_env):
    project_dir = tmp_path / "example-modern"
    run_debops("project", "init", "-t", "modern", "--no-requirements",
               "--template", "hosts", str(project_dir), env=debops_env,
               check=True)

    result = run_debops("project", "refresh", "--host", "web1",
                        str(project_dir), env=debops_env)

    assert result.returncode == 0
    variables = json.loads(result.stdout)
    assert variables["ansible_host"] == "web1.example.org"
    assert "nginx__hostname_domains" in variables


@ansible_inventory
def test_refresh_dry_run_inspects_a_copy(run_debops, tmp_path, debops_env):
    project_dir = tmp_path / "example-modern"
    run_debops("project", "init", "-t", "modern", "--no-requirements",
               str(project_dir), env=debops_env, check=True)
    spec = tmp_path / "probe.yml"
    spec.write_text("version: 0\n"
                    "files:\n"
                    "  hosts_probe: |\n"
                    "    [probe]\n"
                    "    probe1 ansible_host=192.0.2.99\n")

    result = run_debops("project", "refresh", "-n", "--template", str(spec),
                        "--list", str(project_dir), env=debops_env)

    assert result.returncode == 0
    inventory = json.loads(result.stdout)
    assert inventory["probe"]["hosts"] == ["probe1"]
    real = (project_dir / "ansible" / "views" / "system" / "inventory"
            / "hosts_probe")
    assert not real.exists()


def test_refresh_applies_a_spec_to_the_selected_view(run_debops, tmp_path,
                                                     debops_env):
    project_dir = tmp_path / "example-modern"
    run_debops("project", "init", "-t", "modern", "-V", "system",
               "--no-requirements", str(project_dir), env=debops_env,
               check=True)
    run_debops("project", "mkview", "test", cwd=str(project_dir),
               env=debops_env, check=True)
    spec = tmp_path / "view.yml"
    spec.write_text("version: 0\n"
                    "files:\n"
                    "  view_marker.yml: |\n"
                    "    selected: true\n")

    result = run_debops("project", "refresh", "-V", "test", "--template",
                        str(spec), str(project_dir), env=debops_env)

    assert result.returncode == 0
    views = project_dir / "ansible" / "views"
    assert (views / "test" / "inventory" / "view_marker.yml").exists()
    assert not (views / "system" / "inventory" / "view_marker.yml").exists()


def test_refresh_aborts_on_a_failing_pre_refresh_hook(run_debops, tmp_path,
                                                      debops_env):
    project_dir = tmp_path / "example-modern"
    run_debops("project", "init", "-t", "modern", "--no-requirements",
               str(project_dir), env=debops_env, check=True)
    hook_dir = project_dir / ".debops" / "hooks" / "pre-refresh"
    hook_dir.mkdir(parents=True)
    hook = hook_dir / "00-fail"
    hook.write_text("#!/bin/sh\nexit 1\n")
    hook.chmod(0o755)
    inventory = (project_dir / "ansible" / "views" / "system" / "inventory")
    hosts = inventory / "hosts"
    before = hosts.read_text()

    result = run_debops("project", "refresh", str(project_dir),
                        env=debops_env)

    assert result.returncode == 0
    assert "Hook pre-refresh aborted" in result.stdout
    assert hosts.read_text() == before


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


def error_message(result):
    """The error line the command line printed, independent of the stream."""
    return result.stdout + result.stderr


def test_init_refuses_the_own_home_directory(run_debops, tmp_path, debops_env,
                                             debops_source_dir):
    """A project cannot live in the user home directory itself.

    The swapping of $HOME for the test directory also removes the user's
    Python site-packages from import reach; the real user site is appended
    so the command line starts, and the home-detection guard can fire.
    """
    import site

    env = dict(debops_env, HOME=str(tmp_path),
               PYTHONPATH=os.pathsep.join(
                   [debops_source_dir, site.getusersitepackages()]))

    result = run_debops("project", "init", str(tmp_path), env=env)

    assert result.returncode == 1
    assert "home directory" in error_message(result)


def test_mkview_refuses_an_unspecified_name(run_debops, tmp_path, debops_env):
    project_dir = tmp_path / "example-modern"
    run_debops("project", "init", "-t", "modern", "-V", "system",
               "--no-requirements", str(project_dir), env=debops_env,
               check=True)

    result = run_debops("project", "mkview", cwd=str(project_dir),
                        env=debops_env)
    assert result.returncode == 1
    assert "New view name not specified" in error_message(result)


def test_mkview_refuses_a_view_inside_another_view(run_debops, tmp_path,
                                                   debops_env):
    project_dir = tmp_path / "example-modern"
    run_debops("project", "init", "-t", "modern", "-V", "system",
               "--no-requirements", str(project_dir), env=debops_env,
               check=True)
    run_debops("project", "mkview", "test", cwd=str(project_dir),
               env=debops_env, check=True)

    result = run_debops("project", "mkview", "test/inner",
                        cwd=str(project_dir), env=debops_env)
    assert result.returncode == 1
    assert "cannot be placed inside another view" in error_message(result)


def test_mkview_refuses_a_legacy_project(run_debops, tmp_path, debops_env):
    project_dir = tmp_path / "example-legacy"
    run_debops("project", "init", "--no-requirements", str(project_dir),
               env=debops_env, check=True)

    result = run_debops("project", "mkview", "test", cwd=str(project_dir),
                        env=debops_env)
    assert result.returncode == 1
    assert 'only works in "modern"' in error_message(result)


def test_commands_reject_an_unknown_view(run_debops, tmp_path, debops_env):
    """A view selected on the command line needs to exist."""
    project_dir = tmp_path / "example-modern"
    run_debops("project", "init", "-t", "modern", "-V", "system",
               "--no-requirements", str(project_dir), env=debops_env,
               check=True)

    result = run_debops("env", "-V", "unknown-view", "true",
                        cwd=str(project_dir), env=debops_env)
    assert result.returncode == 1
    assert 'view is not present in the "example-modern" project' \
        in error_message(result)


def test_the_view_is_deduced_from_the_current_directory(
        run_debops, tmp_path, debops_env):
    """Working inside a view directory selects that view."""
    project_dir = tmp_path / "example-modern"
    run_debops("project", "init", "-t", "modern", "-V", "system",
               "--no-requirements", str(project_dir), env=debops_env,
               check=True)
    run_debops("project", "mkview", "test", cwd=str(project_dir),
               env=debops_env, check=True)

    result = run_debops("config", "get", "project.view",
                        cwd=str(project_dir / "ansible" / "views" / "test"),
                        env=debops_env)
    assert result.returncode == 0
    assert result.stdout.strip() == "test"


def test_commit_refuses_a_plain_directory(run_debops, tmp_path, debops_env):
    project_dir = tmp_path

    result = run_debops("project", "commit", cwd=str(project_dir),
                        env=debops_env)
    assert result.returncode == 1
    assert "project directory not found" in error_message(result)


def test_project_commit_creates_a_commit(run_debops, tmp_path, debops_env):
    project_dir = tmp_path / "example-modern"
    run_debops("project", "init", "-t", "modern", "--no-requirements",
               str(project_dir), env=debops_env, check=True)
    config = project_dir / ".debops" / "conf.d" / "project.yml"
    config.write_text(config.read_text() + "\n# commit trigger\n")

    result = run_debops("project", "commit", cwd=str(project_dir),
                        env=debops_env)

    assert result.returncode == 0
    log = subprocess.run(["git", "-C", str(project_dir), "log", "-1",
                          "--format=%s"], capture_output=True, text=True,
                         check=True)
    assert log.stdout.strip() == "Changes committed automatically by DebOps"
    status = subprocess.run(["git", "-C", str(project_dir), "status",
                             "--porcelain"], capture_output=True, text=True,
                            check=True)
    assert status.stdout == ""
