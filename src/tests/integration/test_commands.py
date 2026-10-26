# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""End-to-end tests for the command sections which run Ansible.

``ansible-playbook`` is normally replaced by a stub on ``PATH`` which records
its invocation, so the tests can check the command DebOps built without
running any real playbook. One smoke test uses the real binary when it is
installed, to verify the configuration and environment end to end.
"""

import os
import shutil

import pytest


pytestmark = pytest.mark.integration


ansible_playbook = pytest.mark.skipif(
    shutil.which("ansible-playbook") is None,
    reason="ansible-playbook is not installed")


def make_stub(directory, name, log):
    """Write an executable which logs its working directory and arguments."""
    stub = directory / name
    stub.write_text('#!/bin/sh\necho "$PWD" "$@" >> "{}"\n'.format(log))
    stub.chmod(0o755)
    return stub


@pytest.fixture
def legacy_project(run_debops, tmp_path, debops_env):
    project_dir = tmp_path / "example-legacy"
    run_debops("project", "init", "--no-requirements", str(project_dir),
               env=debops_env, check=True)
    return project_dir


def test_exec_eval_prints_the_ansible_command(run_debops, debops_env,
                                              legacy_project):
    result = run_debops("exec", "--eval", "all", "-m", "ping",
                        cwd=str(legacy_project), env=debops_env)

    assert result.returncode == 0
    assert "export ANSIBLE_CONFIG=" in result.stdout
    assert "ansible all -m ping" in result.stdout


def test_run_executes_the_playbook(run_debops, tmp_path, debops_env,
                                   legacy_project):
    log = tmp_path / "ansible-playbook.log"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    make_stub(bin_dir, "ansible-playbook", log)
    env = dict(debops_env,
               PATH=os.pathsep.join([str(bin_dir), os.environ["PATH"]]))

    result = run_debops("run", "site.yml", cwd=str(legacy_project), env=env)

    assert result.returncode == 0
    invocation = log.read_text()
    assert str(legacy_project) in invocation
    assert "site.yml" in invocation


def test_check_runs_the_playbook_in_check_mode(run_debops, tmp_path,
                                               debops_env, legacy_project):
    log = tmp_path / "ansible-playbook.log"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    make_stub(bin_dir, "ansible-playbook", log)
    env = dict(debops_env,
               PATH=os.pathsep.join([str(bin_dir), os.environ["PATH"]]))

    result = run_debops("check", "site.yml", cwd=str(legacy_project), env=env)

    assert result.returncode == 0
    invocation = log.read_text()
    assert "site.yml" in invocation
    assert "--diff" in invocation
    assert "--check" in invocation


@ansible_playbook
def test_run_executes_a_real_local_playbook(run_debops, debops_env,
                                            legacy_project):
    playbook = legacy_project / "local.yml"
    playbook.write_text("---\n"
                        "- hosts: localhost\n"
                        "  connection: local\n"
                        "  gather_facts: false\n"
                        "  tasks:\n"
                        "    - name: Check the local connection\n"
                        "      command: /bin/true\n"
                        "      changed_when: false\n")

    result = run_debops("run", "local.yml", cwd=str(legacy_project),
                        env=debops_env)

    assert result.returncode == 0
    assert "ok=1" in result.stdout
    assert "failed=0" in result.stdout


def test_run_executes_the_project_hooks(run_debops, tmp_path, debops_env,
                                        legacy_project):
    markers = tmp_path / "hooks.log"
    for hook_name in ("pre-run", "post-run"):
        hook_dir = legacy_project / ".debops" / "hooks" / hook_name
        hook_dir.mkdir(parents=True)
        script = hook_dir / "00-marker"
        script.write_text(
            '#!/bin/sh\n'
            'echo "$DEBOPS_HOOK_NAME $DEBOPS_PROJECT_PATH '
            '${{DEBOPS_RETURN_CODE:-none}}" >> "{}"\n'.format(markers))
        script.chmod(0o755)

    log = tmp_path / "ansible-playbook.log"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    make_stub(bin_dir, "ansible-playbook", log)
    env = dict(debops_env,
               PATH=os.pathsep.join([str(bin_dir), os.environ["PATH"]]))

    result = run_debops("run", "site.yml", cwd=str(legacy_project), env=env)

    assert result.returncode == 0
    assert markers.read_text().splitlines() == [
        "pre-run {} none".format(legacy_project),
        "post-run {} 0".format(legacy_project)]


def test_env_runs_a_command_in_the_project_environment(run_debops, debops_env,
                                                       legacy_project):
    result = run_debops("env", "true", cwd=str(legacy_project),
                        env=debops_env)

    assert result.returncode == 0


def test_env_without_a_command_lists_the_environment(run_debops, debops_env,
                                                     legacy_project):
    result = run_debops("env", cwd=str(legacy_project), env=debops_env)

    assert result.returncode == 0
    assert "DEBOPS_ANSIBLE_COLLECTIONS_PATH=" in result.stdout


def test_config_get_reports_the_project_name(run_debops, debops_env,
                                             legacy_project):
    result = run_debops("config", "get", "project.name",
                        cwd=str(legacy_project), env=debops_env)

    assert result.returncode == 0
    assert result.stdout.strip() == "example-legacy"


def make_failing_hook(project_dir, hook_name):
    """Place a failing hook script in the project and return its directory."""
    hook_dir = project_dir / ".debops" / "hooks" / hook_name
    hook_dir.mkdir(parents=True)
    hook = hook_dir / "00-fail"
    hook.write_text("#!/bin/sh\nexit 1\n")
    hook.chmod(0o755)
    return hook


def error_message(result):
    """The error the command line printed, independent of the stream."""
    return result.stdout + result.stderr


def test_run_aborts_on_a_failing_pre_run_hook(run_debops, debops_env,
                                              legacy_project):
    (legacy_project / "site.yml").write_text("---\n")
    make_failing_hook(legacy_project, "pre-run")

    result = run_debops("run", "site.yml", cwd=str(legacy_project),
                        env=debops_env)

    assert result.returncode == 1
    assert "Hook pre-run aborted" in error_message(result)
    assert "Traceback" not in error_message(result)


def test_exec_aborts_on_a_failing_pre_exec_hook(run_debops, debops_env,
                                                legacy_project):
    make_failing_hook(legacy_project, "pre-exec")

    result = run_debops("exec", "all", "-m", "ping", cwd=str(legacy_project),
                        env=debops_env)

    assert result.returncode == 1
    assert "Hook pre-exec aborted" in error_message(result)
    assert "Traceback" not in error_message(result)


def test_env_aborts_on_a_failing_pre_env_hook(run_debops, debops_env,
                                              legacy_project):
    make_failing_hook(legacy_project, "pre-env")

    result = run_debops("env", "true", cwd=str(legacy_project),
                        env=debops_env)

    assert result.returncode == 1
    assert "Hook pre-env aborted" in error_message(result)
    assert "Traceback" not in error_message(result)
