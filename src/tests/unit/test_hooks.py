# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the hook script runner in ``debops.hooks``.

Hooks are executable shell scripts, so the tests create real scripts in
temporary directories and let ``run_hooks`` execute them; that exercises the
discovery, ordering, environment and failure handling exactly the way they
happen on the command line.
"""

import os

import pytest

import debops.hooks as hooks_module
from debops.hooks import run_hooks


def make_hook(directory, name, body="exit 0"):
    """Write an executable hook script into a hook directory."""
    script = directory / name
    script.write_text("#!/bin/sh\n" + body + "\n")
    script.chmod(0o755)
    return script


@pytest.fixture
def hook_dirs(tmp_path, monkeypatch):
    """Project-local and user-global hook directories in a tmp tree.

    ``run_hooks`` looks up the user-global hooks under ``xdg_config_home``,
    which is imported into the module, so it has to be replaced there.
    """
    project = tmp_path / "project"
    project.mkdir()
    user_config = tmp_path / "config"
    user_config.mkdir()
    monkeypatch.setattr(hooks_module, "xdg_config_home", str(user_config))
    return project, user_config


def project_hooks(project, name):
    hook_dir = project / ".debops" / "hooks" / name
    hook_dir.mkdir(parents=True)
    return hook_dir


def user_hooks(user_config, name):
    hook_dir = user_config / "debops" / "hooks" / name
    hook_dir.mkdir(parents=True)
    return hook_dir


def test_run_hooks_is_a_noop_without_hooks(hook_dirs):
    project, user_config = hook_dirs

    assert run_hooks(str(project), "pre-run") is True


def test_run_hooks_executes_a_project_hook(hook_dirs, tmp_path):
    project, user_config = hook_dirs
    marker = tmp_path / "marker"
    make_hook(project_hooks(project, "pre-run"), "10-test",
              'touch "{}"'.format(marker))

    assert run_hooks(str(project), "pre-run") is True
    assert marker.exists()


def test_run_hooks_executes_a_user_hook(hook_dirs, tmp_path):
    project, user_config = hook_dirs
    marker = tmp_path / "marker"
    make_hook(user_hooks(user_config, "pre-run"), "10-test",
              'touch "{}"'.format(marker))

    assert run_hooks(str(project), "pre-run") is True
    assert marker.exists()


def test_run_hooks_runs_project_hooks_before_user_hooks(hook_dirs, tmp_path):
    project, user_config = hook_dirs
    order = tmp_path / "order"
    make_hook(project_hooks(project, "pre-run"), "10-test",
              'echo project >> "{}"'.format(order))
    make_hook(user_hooks(user_config, "pre-run"), "10-test",
              'echo user >> "{}"'.format(order))

    assert run_hooks(str(project), "pre-run") is True
    assert order.read_text().splitlines() == ["project", "user"]


def test_run_hooks_runs_scripts_in_sorted_order(hook_dirs, tmp_path):
    project, user_config = hook_dirs
    order = tmp_path / "order"
    hooks = project_hooks(project, "pre-run")
    make_hook(hooks, "20-last", 'echo last >> "{}"'.format(order))
    make_hook(hooks, "00-first", 'echo first >> "{}"'.format(order))
    make_hook(hooks, "10-middle", 'echo middle >> "{}"'.format(order))

    assert run_hooks(str(project), "pre-run") is True
    assert order.read_text().splitlines() == ["first", "middle", "last"]


def test_run_hooks_skips_non_executable_files(hook_dirs, tmp_path):
    project, user_config = hook_dirs
    marker = tmp_path / "marker"
    hook_dir = project_hooks(project, "pre-run")
    script = hook_dir / "10-not-executable"
    script.write_text('#!/bin/sh\ntouch "{}"\n'.format(marker))
    script.chmod(0o644)

    assert run_hooks(str(project), "pre-run") is True
    assert not marker.exists()


def test_run_hooks_skips_directories(hook_dirs, tmp_path):
    project, user_config = hook_dirs
    (project_hooks(project, "pre-run") / "10-directory").mkdir()

    assert run_hooks(str(project), "pre-run") is True


def test_run_hooks_returns_false_when_a_script_fails(hook_dirs):
    project, user_config = hook_dirs
    make_hook(project_hooks(project, "pre-run"), "10-failing", "exit 1")

    assert run_hooks(str(project), "pre-run") is False


def test_run_hooks_stops_after_a_failure(hook_dirs, tmp_path):
    project, user_config = hook_dirs
    marker = tmp_path / "marker"
    hooks = project_hooks(project, "pre-run")
    make_hook(hooks, "00-failing", "exit 1")
    make_hook(hooks, "10-never-run", 'touch "{}"'.format(marker))

    assert run_hooks(str(project), "pre-run") is False
    assert not marker.exists()


def test_run_hooks_times_out(hook_dirs):
    project, user_config = hook_dirs
    make_hook(project_hooks(project, "pre-run"), "10-slow", "sleep 10")

    assert run_hooks(str(project), "pre-run", timeout=0.2) is False


def test_run_hooks_passes_the_hook_environment(hook_dirs, tmp_path):
    project, user_config = hook_dirs
    output = tmp_path / "environment"
    make_hook(project_hooks(project, "pre-run"), "10-env",
              'printf "%s\\n%s\\n%s\\n" "$DEBOPS_HOOK_NAME" '
              '"$DEBOPS_PROJECT_PATH" "$TEST_EXTRA" > "{}"'
              .format(output))

    result = run_hooks(str(project), "pre-run",
                       extra_env={"TEST_EXTRA": "extra-value"})

    assert result is True
    assert output.read_text().splitlines() == ["pre-run",
                                               os.path.abspath(str(project)),
                                               "extra-value"]


def test_run_hooks_runs_scripts_in_the_project_directory(hook_dirs,
                                                         tmp_path):
    project, user_config = hook_dirs
    output = tmp_path / "cwd"
    make_hook(project_hooks(project, "pre-run"), "10-cwd",
              'pwd > "{}"'.format(output))

    assert run_hooks(str(project), "pre-run") is True
    assert output.read_text().strip() == os.path.abspath(str(project))


def test_discover_hooks_returns_sorted_absolute_paths(hook_dirs):
    project, user_config = hook_dirs
    hooks = project_hooks(project, "pre-run")
    make_hook(hooks, "20-b")
    first = make_hook(hooks, "00-a")

    found = hooks_module._discover_hooks(str(hooks))

    assert found == sorted([str(first), str(hooks / "20-b")])
    assert all(os.path.isabs(path) for path in found)


def test_discover_hooks_is_empty_for_a_missing_directory(tmp_path):
    assert hooks_module._discover_hooks(str(tmp_path / "nope")) == []
