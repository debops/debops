# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the self-contained helpers in ``debops.projectdir``.

``ProjectDir`` is constructed with a full project on disk and therefore
belongs to the integration tests; these cover the pure helpers that can be
exercised against small directory trees.
"""

import logging
import os
import re
import sys
from types import SimpleNamespace
from unittest import mock

import pytest

import debops.projectdir as projectdir_module
from debops.projectdir import ProjectDir


def make_project(raw, kwargs=None):
    project = ProjectDir.__new__(ProjectDir)
    project.config = SimpleNamespace(raw=raw)
    project.kwargs = kwargs if kwargs is not None else {}
    return project


def make_project_at(tmp_path, raw=None, project_type="modern"):
    """A mostly-stub project rooted in a real directory, for the helpers
    which read or write files in the project directory."""
    project = ProjectDir.__new__(ProjectDir)
    project.path = str(tmp_path)
    project.name = os.path.basename(project.path)
    project.project_type = project_type
    project.config = SimpleNamespace(
        raw=raw if raw is not None else {"views": {}})
    project.kwargs = {}
    return project


def test_find_up_dir_finds_a_marker_in_an_ancestor(tmp_path):
    project = make_project({})
    path = tmp_path / "a" / "b" / "c"
    path.mkdir(parents=True)
    (tmp_path / "marker").mkdir()
    (path / "marker").mkdir()

    found = project._find_up_dir(str(path), ("marker",))

    assert found == str(path / "marker")


def test_find_up_dir_skips_a_missing_marker_in_between(tmp_path):
    project = make_project({})
    path = tmp_path / "a" / "b" / "c"
    path.mkdir(parents=True)
    (tmp_path / "a" / "marker").mkdir()

    found = project._find_up_dir(str(path), ("marker",))

    assert found == str(tmp_path / "a" / "marker")


def test_find_up_dir_returns_none_without_a_marker(tmp_path):
    project = make_project({})

    assert project._find_up_dir(str(tmp_path), ("nope",)) is None


def test_is_git_repo_detects_a_repository(tmp_path):
    subprocess = __import__("subprocess")
    subprocess.check_call(["git", "init", "-q"], cwd=str(tmp_path))

    assert ProjectDir.__new__(ProjectDir)._is_git_repo(str(tmp_path)) is True


def test_is_git_repo_rejects_a_plain_directory(tmp_path):
    assert ProjectDir.__new__(ProjectDir)._is_git_repo(str(tmp_path)) is False


def test_report_unused_vars_warns_about_unknown_entries(tmp_path, capsys):
    project = make_project({})
    (tmp_path / "group_vars").mkdir()
    (tmp_path / "group_vars" / "web.yml").write_text("")
    (tmp_path / "group_vars" / "db.yml").write_text("")
    (tmp_path / "host_vars").mkdir()
    (tmp_path / "host_vars" / "extra.yml").write_text("")

    project._report_unused_vars(
        str(tmp_path), "@all:\n  |--@db:\n  |  |--db01\n")

    err = capsys.readouterr().err
    assert "group_vars/web" in err
    assert "group_vars/db" not in err
    assert "host_vars/extra" in err


def test_parse_graph_names_skips_empty_entries():
    groups, hosts = ProjectDir._parse_graph_names(
            "@all:\n\n  |--@web:\n  |  |--web1\n")

    assert groups == {"all", "web"}
    assert hosts == {"web1"}


def test_report_spec_result_covers_every_verb(tmp_path, capsys, caplog):
    project = make_project({})
    result = {
        "removed": [str(tmp_path / "removed")],
        "planned_removed": [str(tmp_path / "would-remove")],
        "written": [str(tmp_path / "written")],
        "planned": [str(tmp_path / "would-create")],
        "skipped": [str(tmp_path / "skipped")],
        "kept": [str(tmp_path / "kept")],
    }

    with caplog.at_level(logging.NOTICE, logger="debops.projectdir"):
        project._report_spec_result(result, str(tmp_path), dry_run=False)

    output = capsys.readouterr().out
    assert "Removed removed" in caplog.text
    assert "Would remove would-remove" in caplog.text
    assert "Created written" in caplog.text
    assert "Would create would-create" in caplog.text
    assert "Skipped existing skipped" in caplog.text
    assert "Kept kept" in caplog.text
    assert "Use '--force' to overwrite or remove paths which already exist." \
        in output
    assert "Applied the inventory specification." not in output

    result["skipped"] = []
    project._report_spec_result(result, str(tmp_path), dry_run=False)
    assert "Applied the inventory specification." in capsys.readouterr().out

    project._report_spec_result({"planned": [str(tmp_path / "x")]},
                                str(tmp_path), dry_run=True)
    assert "Applied the inventory specification." not in \
        capsys.readouterr().out


def test_venv_enabled_reads_the_configuration():
    assert make_project(
            {"project": {"venv": {"enabled": True}}})._venv_enabled() is True
    assert make_project(
            {"project": {"venv": {"enabled": False}}})._venv_enabled() is False
    assert make_project({"project": {}})._venv_enabled() is False
    assert make_project({})._venv_enabled() is False


def test_venv_enabled_accepts_string_values():
    assert make_project(
            {"project": {"venv": {"enabled": "yes"}}})._venv_enabled() is True
    assert make_project(
            {"project": {"venv": {"enabled": "no"}}})._venv_enabled() is False


def test_venv_enabled_tolerates_a_config_without_get():
    assert make_project(None)._venv_enabled() is False


def test_inventory_spec_config_tolerates_a_config_without_get():
    policy = make_project(None)._inventory_spec_config()

    assert policy == {"enabled": True,
                      "max_version": projectdir_module.SPEC_VERSION,
                      "allow_io": False}


def test_status_stream_uses_stderr_for_json_outputs():
    assert make_project({}, {"list": True})._status_stream() is sys.stderr
    assert make_project({}, {"host": "web01"})._status_stream() is sys.stderr


def test_status_stream_stays_on_stdout_for_a_graph():
    assert make_project({}, {"graph": True})._status_stream() is sys.stdout


def test_inventory_inspect_requires_the_binary(tmp_path):
    raw = {"binaries": {"ansible-inventory": "bogus-inventory-binary"}}

    with pytest.raises(ValueError):
        make_project(raw)._inventory_inspect(str(tmp_path), str(tmp_path),
                                             "graph")


def test_inventory_inspect_prints_the_graph(tmp_path, monkeypatch, capsys):
    raw = {"binaries": {"ansible-inventory": sys.executable}}
    project = make_project(raw)
    process = mock.Mock()
    process.communicate.return_value = (
        b"@all:\n  |--@ungrouped:\n  |  |--localhost\n", b"")
    process.returncode = 0
    popen = mock.Mock(return_value=process)
    monkeypatch.setattr(projectdir_module.subprocess, "Popen", popen)

    project._inventory_inspect(str(tmp_path), str(tmp_path), "graph")

    assert "@all:" in capsys.readouterr().out
    argv = popen.call_args.args[0]
    assert argv[:3] == [sys.executable, "-i", str(tmp_path)]
    assert "--graph" in argv
    assert "--vars" in argv


@pytest.mark.parametrize(("mode", "extra"), [
    ("list", ["--list"]),
    ("host", ["--host", "web01"]),
])
def test_inventory_inspect_selects_the_right_action(
        tmp_path, monkeypatch, mode, extra):
    raw = {"binaries": {"ansible-inventory": sys.executable}}
    project = make_project(raw)
    process = mock.Mock()
    process.communicate.return_value = (b"{}", b"")
    process.returncode = 0
    popen = mock.Mock(return_value=process)
    monkeypatch.setattr(projectdir_module.subprocess, "Popen", popen)

    project._inventory_inspect(str(tmp_path), str(tmp_path), mode,
                               host="web01")

    argv = popen.call_args.args[0]
    assert argv[:3] == [sys.executable, "-i", str(tmp_path)]
    assert argv[3:] == extra


def test_inventory_inspect_reports_a_failed_command(tmp_path, monkeypatch):
    raw = {"binaries": {"ansible-inventory": sys.executable}}
    project = make_project(raw)
    process = mock.Mock()
    process.communicate.return_value = (b"", b"")
    process.returncode = 2
    monkeypatch.setattr(projectdir_module.subprocess, "Popen",
                        mock.Mock(return_value=process))

    with pytest.raises(ChildProcessError):
        project._inventory_inspect(str(tmp_path), str(tmp_path), "graph")


def test_write_venv_config_creates_the_files(tmp_path, monkeypatch):
    monkeypatch.setattr(projectdir_module, "find_missing_external_deps",
                        lambda names: {})
    project = make_project_at(tmp_path)

    project._write_venv_config(str(tmp_path))

    venv_yml = (tmp_path / ".debops" / "conf.d" / "venv.yml").read_text()
    assert "venv:" in venv_yml
    assert "enabled: True" in venv_yml
    requirements = (tmp_path / ".debops" / "requirements.txt").read_text()
    assert "\npython-ldap\n" in requirements


def test_write_venv_config_does_not_overwrite_existing_files(tmp_path,
                                                             monkeypatch):
    monkeypatch.setattr(projectdir_module, "find_missing_external_deps",
                        lambda names: {})
    project = make_project_at(tmp_path)
    requirements = tmp_path / ".debops" / "requirements.txt"
    requirements.parent.mkdir(parents=True)
    requirements.write_text("custom\n")

    project._write_venv_config(str(tmp_path))

    assert requirements.read_text() == "custom\n"


COLLECTIONS_STUB = (
        "  # Uncomment this if you want to use DebOps Collection from "
        "Ansible Galaxy\n"
        "  # instead of the one included in the DebOps Python package.\n"
        "  #- name: 'debops.debops'\n"
        "  #  version: '*'\n")


def write_collections_requirements(tmp_path, content):
    requirements = tmp_path / "ansible" / "collections" / "requirements.yml"
    requirements.parent.mkdir(parents=True, exist_ok=True)
    requirements.write_text(content)
    return requirements


def test_enable_venv_collections_requirements_uncomments_the_stub(tmp_path):
    project = make_project_at(tmp_path)
    requirements = write_collections_requirements(
            tmp_path, "---\ncollections:\n\n" + COLLECTIONS_STUB)

    project._enable_venv_collections_requirements()

    content = requirements.read_text()
    assert "Uncomment this" not in content
    assert "  - name: 'debops.debops'\n" in content
    # The entry is static; the installed version is pinned in the lock file
    assert "    version: '*'\n" in content
    assert content.startswith("---\ncollections:\n")


def test_enable_venv_collections_requirements_keeps_an_active_entry(tmp_path):
    project = make_project_at(tmp_path)
    content = ("---\ncollections:\n\n"
               "  - name: 'debops.debops'\n    version: '1.2.3'\n")
    requirements = write_collections_requirements(tmp_path, content)

    project._enable_venv_collections_requirements()

    assert requirements.read_text() == content


def test_enable_venv_collections_requirements_appends_a_missing_entry(
        tmp_path):
    project = make_project_at(tmp_path)
    requirements = write_collections_requirements(
            tmp_path,
            "---\ncollections:\n\n  - name: 'ansible.posix'\n"
            "    version: '*'\n")

    project._enable_venv_collections_requirements()

    content = requirements.read_text()
    assert content.count("- name: 'debops.debops'") == 1
    assert content.index("ansible.posix") < content.index("debops.debops")


def test_enable_venv_collections_requirements_appends_without_a_newline(
        tmp_path):
    project = make_project_at(tmp_path)
    requirements = write_collections_requirements(
            tmp_path,
            "---\ncollections:\n\n  - name: 'ansible.posix'\n"
            "    version: '*'")

    project._enable_venv_collections_requirements()

    content = requirements.read_text()
    assert content.count("- name: 'debops.debops'") == 1
    assert content.endswith("\n")
    assert "version: '*'\n\n  # The DebOps Collection" in content


def test_append_venv_gitignore_appends_the_entry_once(tmp_path):
    project = make_project_at(tmp_path)
    (tmp_path / ".gitignore").write_text(".env\n")

    project._append_venv_gitignore()
    project._append_venv_gitignore()

    content = (tmp_path / ".gitignore").read_text()
    assert content.startswith(".env\n")
    assert content.count("/.debops/venv/") == 1


def test_append_venv_gitignore_creates_a_missing_file(tmp_path):
    project = make_project_at(tmp_path)

    project._append_venv_gitignore()

    content = (tmp_path / ".gitignore").read_text()
    assert not content.startswith("\n")
    assert "/.debops/venv/" in content


def test_rewrite_view_collections_path_replaces_the_value(tmp_path):
    project = make_project_at(tmp_path)
    conf_d = tmp_path / ".debops" / "conf.d"
    conf_d.mkdir(parents=True)
    view_yml = conf_d / "view-system.yml"
    view_yml.write_text(
            "views:\n"
            "  system:\n"
            "    ansible:\n"
            "      defaults:\n"
            "        collections_path: '~/x:~/.ansible/collections'\n")

    project._rewrite_view_collections_path("system")

    content = view_yml.read_text()
    assert ("collections_path: '${DEBOPS_PROJECT_PATH}/ansible/collections'"
            in content)
    assert "~/.ansible/collections" not in content
    assert content.startswith("views:\n  system:\n")


def test_rewrite_view_collections_path_ignores_a_missing_option(tmp_path):
    project = make_project_at(tmp_path)
    conf_d = tmp_path / ".debops" / "conf.d"
    conf_d.mkdir(parents=True)
    view_yml = conf_d / "view-system.yml"
    view_yml.write_text("views:\n  system: {}\n")

    project._rewrite_view_collections_path("system")

    assert view_yml.read_text() == "views:\n  system: {}\n"


def test_rewrite_view_collections_path_ignores_a_missing_file(tmp_path,
                                                              caplog):
    project = make_project_at(tmp_path)

    with caplog.at_level(logging.NOTICE, logger="debops.projectdir"):
        assert project._rewrite_view_collections_path("system") is False

    assert "View configuration file not found" in caplog.text


def test_enable_venv_rejects_a_legacy_project(tmp_path):
    project = make_project_at(tmp_path, project_type="legacy")

    with pytest.raises(ValueError, match="modern"):
        project.enable_venv()


def test_enable_venv_is_a_noop_when_already_enabled(tmp_path, capsys):
    project = make_project_at(tmp_path, raw={
        "views": {},
        "project": {"venv": {"enabled": True}}})
    write_collections_requirements(
            tmp_path, "---\ncollections:\n\n"
            "  - name: 'debops.debops'\n    version: '3.3.2'\n")

    assert project.enable_venv() is False
    assert "already enabled" in capsys.readouterr().out
    assert not (tmp_path / ".debops" / "conf.d").exists()


def enable_venv_project(tmp_path, monkeypatch, raw=None):
    """A stub project ready for a happy-path 'enable_venv' call."""
    project = make_project_at(tmp_path, raw=raw)
    project.config.merge = mock.Mock()
    monkeypatch.setattr(ProjectDir, "refresh", mock.Mock())
    monkeypatch.setattr(ProjectDir, "commit", mock.Mock())
    monkeypatch.setattr(projectdir_module, "find_missing_external_deps",
                        lambda names: {})
    write_collections_requirements(tmp_path, "---\ncollections: []\n")
    return project


def test_enable_venv_writes_the_configuration(tmp_path, monkeypatch, capsys):
    project = enable_venv_project(tmp_path, monkeypatch,
                                  raw={"views": {}, "project": {}})

    assert project.enable_venv() is True

    assert (tmp_path / ".debops" / "conf.d" / "venv.yml").exists()
    assert (tmp_path / ".debops" / "requirements.txt").exists()
    assert "/.debops/venv/" in (tmp_path / ".gitignore").read_text()
    # The environment file is not modified; PATH is prepended at runtime
    assert not (tmp_path / ".debops" / "environment").exists()
    ProjectDir.refresh.assert_not_called()
    ProjectDir.commit.assert_not_called()
    out = capsys.readouterr().out
    assert "Enabled Python virtual environment" in out
    assert "debops project venv install" in out


def test_enable_venv_commits_when_auto_commit_is_enabled(tmp_path,
                                                         monkeypatch):
    project = enable_venv_project(tmp_path, monkeypatch, raw={
        "views": {}, "project": {"git": {"auto_commit": True}}})

    assert project.enable_venv() is True

    ProjectDir.commit.assert_called_once_with()


def make_venv_config(tmp_path, enabled=True, env_vars=None):
    """A stub config for the runtime PATH handling."""
    return SimpleNamespace(
        raw={"project": {"venv": {"enabled": enabled, "path": ".debops/venv"}}},
        _env_vars=env_vars if env_vars is not None else {})


def test_prepend_venv_path_prepends_the_venv_bin(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", "/usr/bin")
    project = make_project_at(tmp_path)
    project.config = make_venv_config(tmp_path)
    project.config.set_env = lambda key, value: (
        os.environ.__setitem__(key, value),
        project.config._env_vars.__setitem__(key, value))

    project._prepend_venv_path()

    venv_bin = str(tmp_path / ".debops" / "venv" / "bin")
    assert os.environ["PATH"] == venv_bin + ":/usr/bin"
    assert project.config._env_vars["PATH"] == venv_bin + ":/usr/bin"


def test_prepend_venv_path_skipped_when_not_enabled(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", "/usr/bin")
    project = make_project_at(tmp_path)
    project.config = make_venv_config(tmp_path, enabled=False)

    project._prepend_venv_path()

    assert os.environ["PATH"] == "/usr/bin"


def test_prepend_venv_path_respects_a_path_override(tmp_path, monkeypatch):
    """A PATH defined in an environment file overrides the runtime value."""
    monkeypatch.setenv("PATH", "/usr/bin")
    project = make_project_at(tmp_path)
    project.config = make_venv_config(
            tmp_path, env_vars={"PATH": "/custom/bin:/usr/bin"})

    project._prepend_venv_path()

    assert os.environ["PATH"] == "/usr/bin"


def test_prepend_venv_path_does_not_prepend_twice(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", "/usr/bin")
    project = make_project_at(tmp_path)
    project.config = make_venv_config(tmp_path)
    project.config.set_env = lambda key, value: (
        os.environ.__setitem__(key, value),
        project.config._env_vars.__setitem__(key, value))

    project._prepend_venv_path()
    project._prepend_venv_path()

    assert os.environ["PATH"].count("/.debops/venv/bin") == 1


def test_prepend_venv_path_skips_a_process_path_entry(tmp_path, monkeypatch):
    venv_bin = str(tmp_path / ".debops" / "venv" / "bin")
    monkeypatch.setenv("PATH", venv_bin + ":/usr/bin")
    project = make_project_at(tmp_path)
    project.config = make_venv_config(tmp_path)
    project.config.set_env = mock.Mock()

    project._prepend_venv_path()

    project.config.set_env.assert_not_called()
    assert os.environ["PATH"] == venv_bin + ":/usr/bin"


def test_auto_commit_commits_when_enabled():
    project = make_project({"project": {"git": {"auto_commit": True}}})
    project.commit = mock.Mock()

    project.auto_commit()

    project.commit.assert_called_once_with()


def test_auto_commit_skipped_when_disabled():
    project = make_project({"project": {"git": {"auto_commit": False}}})
    project.commit = mock.Mock()

    project.auto_commit()

    project.commit.assert_not_called()


def test_auto_commit_tolerates_a_missing_option():
    project = make_project({"project": {}})
    project.commit = mock.Mock()

    project.auto_commit()

    project.commit.assert_not_called()


def test_commit_is_a_noop_outside_a_git_repository(tmp_path):
    project = make_project_at(tmp_path)

    project.commit()


def test_commit_unstages_changes_without_a_message(
        tmp_path, monkeypatch, capsys):
    project = make_project({"project": {}})
    project.path = str(tmp_path)
    project._is_git_repo = lambda path: True
    hooks = mock.Mock()
    monkeypatch.setattr(projectdir_module, "run_hooks", hooks)
    repo = mock.Mock()
    repo.head.commit.diff.return_value = [mock.Mock()]
    repo.index.commit.side_effect = KeyError
    monkeypatch.setattr(projectdir_module.git, "Repo",
                        mock.Mock(return_value=repo))

    project.commit(interactive=True)

    repo.git.reset.assert_called_once_with()
    assert "auto_commit_message" in capsys.readouterr().out
    assert [call.args[1] for call in hooks.call_args_list] == [
        "pre-commit", "post-commit"]


def test_commit_commits_when_there_are_changes(tmp_path, monkeypatch):
    project = make_project({"project": {"git": {
        "auto_commit_message": "Changes committed automatically"}}})
    project.path = str(tmp_path)
    project._is_git_repo = lambda path: True
    monkeypatch.setattr(projectdir_module, "run_hooks", mock.Mock())
    repo = mock.Mock()
    repo.head.commit.diff.return_value = [mock.Mock()]
    monkeypatch.setattr(projectdir_module.git, "Repo",
                        mock.Mock(return_value=repo))

    project.commit()

    repo.index.commit.assert_called_once_with(
            "Changes committed automatically")


def test_create_aborts_on_a_failing_pre_init_hook(tmp_path):
    project = make_project_at(tmp_path)
    hook_dir = tmp_path / ".debops" / "hooks" / "pre-init"
    hook_dir.mkdir(parents=True)
    hook = hook_dir / "00-fail"
    hook.write_text("#!/bin/sh\nexit 1\n")
    hook.chmod(0o755)

    with pytest.raises(RuntimeError, match="pre-init"):
        project.create()


def test_enable_venv_collections_requirements_without_the_comment(tmp_path):
    project = make_project_at(tmp_path)
    requirements = write_collections_requirements(
            tmp_path,
            "---\ncollections:\n\n"
            "  #- name: 'debops.debops'\n"
            "  #  version: '*'\n")

    project._enable_venv_collections_requirements()

    content = requirements.read_text()
    assert content.count("- name: 'debops.debops'") == 1
    assert "  - name: 'debops.debops'\n" in content


def test_enable_venv_collections_requirements_with_a_tampered_comment(
        tmp_path):
    project = make_project_at(tmp_path)
    requirements = write_collections_requirements(
            tmp_path,
            "---\ncollections:\n\n"
            "  # my own note about the collection\n"
            "  #- name: 'debops.debops'\n"
            "  #  version: '*'\n")

    project._enable_venv_collections_requirements()

    content = requirements.read_text()
    # The user's own comment is preserved, the entry is activated
    assert "  # my own note about the collection\n" in content
    assert "  - name: 'debops.debops'\n" in content
    assert "#- name: 'debops.debops'" not in content


def test_enable_venv_collections_requirements_without_a_version(tmp_path):
    project = make_project_at(tmp_path)
    requirements = write_collections_requirements(
            tmp_path,
            "---\ncollections:\n\n"
            "  #- name: 'debops.debops'\n")

    project._enable_venv_collections_requirements()

    content = requirements.read_text()
    assert "  - name: 'debops.debops'\n" in content
    # The entry is static; the installed version is pinned in the lock file
    assert "    version: '*'\n" in content


def test_enable_venv_collections_requirements_repairs_a_broken_stub(
        tmp_path):
    """The stub written with a broken indent is replaced in place."""
    project = make_project_at(tmp_path)
    requirements = write_collections_requirements(
            tmp_path,
            "---\ncollections:\n\n"
            "# Uncomment this if you want to use DebOps Collection from "
            "Ansible Galaxy\n"
            "  # instead of the one included in the DebOps Python package.\n"
            "  #- name: 'debops.debops'\n"
            "  #  version: '*'\n")

    project._enable_venv_collections_requirements()

    content = requirements.read_text()
    assert content.count("- name: 'debops.debops'") == 1
    assert "  - name: 'debops.debops'\n" in content
    assert "Uncomment this" not in content


def render_requirements_yml(**kwargs):
    """Render the 'requirements.yml' project template the same way the
    project creation does."""
    import jinja2
    import pkgutil
    template = jinja2.Template(
            pkgutil.get_data('debops',
                             os.path.join('_data',
                                          'templates',
                                          'projectdir',
                                          'modern',
                                          'requirements.yml.j2'))
            .decode('utf-8'), trim_blocks=True)
    return template.render(**kwargs) + '\n'


def test_requirements_yml_stub_branch_is_indented_and_trimmed():
    content = render_requirements_yml(include_debops_collection=False)

    assert "\n  #- name: 'debops.debops'\n" in content
    assert "\n  #  version: '*'\n" in content
    assert "\n  # Uncomment this" in content
    # No content at column 0 below the 'collections:' key
    for line in content.split("collections:\n", 1)[1].splitlines():
        assert line == "" or line.startswith(" ")
    assert content.endswith("\n") and not content.endswith("\n\n")


def test_requirements_yml_collection_branch_is_indented_and_trimmed():
    content = render_requirements_yml(include_debops_collection=True)

    assert "\n  - name: 'debops.debops'\n    version: '*'\n" in content
    assert "\n  # The DebOps Collection" in content
    for line in content.split("collections:\n", 1)[1].splitlines():
        assert line == "" or line.startswith(" ")
    assert content.endswith("\n") and not content.endswith("\n\n")


def test_venv_path_defaults_to_the_project_subdirectory(tmp_path):
    project = make_project_at(tmp_path)
    project.config = make_venv_config(tmp_path)

    assert project._venv_path() == str(tmp_path / ".debops" / "venv")


def test_venv_path_accepts_an_absolute_path(tmp_path):
    project = make_project_at(tmp_path)
    project.config = make_venv_config(tmp_path)
    project.config.raw["project"]["venv"]["path"] = "/shared/venv"

    assert project._venv_path() == "/shared/venv"


def test_venv_path_expands_a_tilde(tmp_path):
    project = make_project_at(tmp_path)
    project.config = make_venv_config(tmp_path)
    project.config.raw["project"]["venv"]["path"] = "~/shared/venv"

    assert project._venv_path() == (os.path.expanduser("~")
                                    + "/shared/venv")


def test_update_venv_binaries_points_the_ansible_binaries_at_the_venv(
        tmp_path):
    project = make_project_at(tmp_path)
    project.config = make_venv_config(tmp_path)
    project.config.raw["binaries"] = {}
    project.config.merge = mock.Mock(side_effect=lambda data: (
        project.config.raw["binaries"].update(data["binaries"])))

    project._update_venv_binaries()

    venv_bin = str(tmp_path / ".debops" / "venv" / "bin")
    assert project.config.raw["binaries"]["ansible-playbook"] == (
            venv_bin + "/ansible-playbook")
    assert project.config.raw["binaries"]["ansible-galaxy"] == (
            venv_bin + "/ansible-galaxy")


def test_apply_venv_runtime_computes_binaries_and_path(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", "/usr/bin")
    project = make_project_at(tmp_path)
    project.config = make_venv_config(tmp_path)
    project.config.raw["binaries"] = {}
    project.config.merge = mock.Mock(side_effect=lambda data: (
        project.config.raw["binaries"].update(data["binaries"])))
    project.config.set_env = lambda key, value: (
        os.environ.__setitem__(key, value),
        project.config._env_vars.__setitem__(key, value))

    project._apply_venv_runtime()

    venv_bin = str(tmp_path / ".debops" / "venv" / "bin")
    assert project.config.raw["binaries"]["ansible"] == venv_bin + "/ansible"
    assert os.environ["PATH"] == venv_bin + ":/usr/bin"


def test_apply_venv_runtime_is_a_noop_when_not_enabled(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", "/usr/bin")
    project = make_project_at(tmp_path)
    project.config = make_venv_config(tmp_path, enabled=False)
    project.config.raw["binaries"] = {}
    project.config.merge = mock.Mock()

    project._apply_venv_runtime()

    assert project.config.raw["binaries"] == {}
    assert os.environ["PATH"] == "/usr/bin"


def test_enable_venv_python_scope_skips_the_collections_side(tmp_path,
                                                             monkeypatch):
    project = enable_venv_project(tmp_path, monkeypatch,
                                  raw={"views": {}, "project": {}})
    rewrite = mock.Mock()
    monkeypatch.setattr(ProjectDir, "_rewrite_view_collections_path", rewrite)
    requirements = write_collections_requirements(
            tmp_path, "---\ncollections:\n\n" + COLLECTIONS_STUB)

    assert project.enable_venv(scope="python") is True

    assert (tmp_path / ".debops" / "conf.d" / "venv.yml").exists()
    rewrite.assert_not_called()
    # The 'debops.debops' entry is not activated
    assert "#- name: 'debops.debops'" in requirements.read_text()
    ProjectDir.refresh.assert_not_called()


def test_enable_venv_collections_scope_skips_the_python_side(tmp_path,
                                                             monkeypatch):
    project = enable_venv_project(tmp_path, monkeypatch,
                                  raw={"views": {}, "project": {}})
    requirements = write_collections_requirements(
            tmp_path, "---\ncollections:\n\n" + COLLECTIONS_STUB)

    assert project.enable_venv(scope="collections") is True

    # No virtual environment configuration is written
    assert not (tmp_path / ".debops").exists()
    # The 'debops.debops' entry is activated
    assert "  - name: 'debops.debops'\n" in requirements.read_text()


def test_enable_venv_refreshes_when_a_view_changes(tmp_path, monkeypatch):
    project = enable_venv_project(tmp_path, monkeypatch,
                                  raw={"views": {"system": {}},
                                       "project": {}})
    conf_d = tmp_path / ".debops" / "conf.d"
    conf_d.mkdir(parents=True)
    (conf_d / "view-system.yml").write_text(
            "views:\n"
            "  system:\n"
            "    ansible:\n"
            "      defaults:\n"
            "        collections_path: '~/x:~/.ansible/collections'\n")

    assert project.enable_venv(scope="collections") is True

    ProjectDir.refresh.assert_called_once_with()
    content = (conf_d / "view-system.yml").read_text()
    assert "collections_path: '${DEBOPS_PROJECT_PATH}/ansible/collections'" in content


def test_enable_venv_rejects_an_unknown_scope(tmp_path, monkeypatch):
    project = enable_venv_project(tmp_path, monkeypatch,
                                  raw={"views": {}, "project": {}})

    with pytest.raises(ValueError, match="scope"):
        project.enable_venv(scope="bogus")


def test_ensure_collections_lock_unignored_inserts_the_negation(tmp_path):
    project = make_project_at(tmp_path)
    (tmp_path / ".gitignore").write_text(
            "/ansible/collections/*\n!/ansible/collections/requirements.yml\n")

    assert project._ensure_collections_lock_unignored() is True
    assert project._ensure_collections_lock_unignored() is False

    lines = (tmp_path / ".gitignore").read_text().splitlines()
    assert lines == ["/ansible/collections/*",
                     "!/ansible/collections/requirements.yml",
                     "!/ansible/collections/requirements.lock.yml"]


def test_ensure_collections_lock_unignored_appends_without_the_marker(
        tmp_path):
    project = make_project_at(tmp_path)
    (tmp_path / ".gitignore").write_text("/ansible/collections/*\n")

    assert project._ensure_collections_lock_unignored() is True

    lines = (tmp_path / ".gitignore").read_text().splitlines()
    assert lines[-1] == "!/ansible/collections/requirements.lock.yml"


def test_ensure_collections_lock_unignored_ignores_other_files(tmp_path):
    project = make_project_at(tmp_path)
    (tmp_path / ".gitignore").write_text("/.debops/venv/\n")

    assert project._ensure_collections_lock_unignored() is False
    assert (tmp_path / ".gitignore").read_text() == "/.debops/venv/\n"


def test_load_specs_reports_overlapping_definitions(tmp_path, caplog):
    first = tmp_path / "first.yml"
    second = tmp_path / "second.yml"
    first.write_text("version: 0\nfiles:\n  hosts: first\n")
    second.write_text("version: 0\nfiles:\n  hosts: second\n")
    project = make_project_at(tmp_path)
    project.view = "system"
    project.kwargs = {"spec_sources": [str(first), str(second)]}

    with caplog.at_level(logging.NOTICE, logger="debops.projectdir"):
        files, keep = project._load_specs(str(tmp_path / "inventory"))

    assert files == {"hosts": "second"}
    assert keep == []
    assert 'File "hosts" from' in caplog.text
    assert "replaces an earlier definition" in caplog.text


def test_load_spec_source_rejects_a_terminal_stdin(tmp_path, monkeypatch):
    project = make_project_at(tmp_path)
    monkeypatch.setattr(projectdir_module.sys, "stdin",
                        SimpleNamespace(isatty=lambda: True))

    with pytest.raises(ValueError, match="standard input"):
        project._load_spec_source("-")


def test_process_spec_logs_a_dry_run(tmp_path, caplog):
    project = make_project_at(tmp_path)
    project.kwargs = {"dry_run": True}
    project._load_specs = mock.Mock(return_value=({"hosts": "x"}, []))
    project._report_spec_result = mock.Mock()
    inventory = SimpleNamespace(path=str(tmp_path),
                                apply_spec=mock.Mock(return_value={}))

    with caplog.at_level(logging.INFO, logger="debops.projectdir"):
        project._process_spec(inventory, frozenset())

    assert "will not be written to disk" in caplog.text
    inventory.apply_spec.assert_called_once_with(
            {"hosts": "x"}, pre_existing=frozenset(), overwrite=False,
            dry_run=True, keep=[])
    project._report_spec_result.assert_called_once_with(
            {}, os.path.realpath(str(tmp_path)), True)


def test_process_spec_inspects_without_files(tmp_path):
    project = make_project_at(tmp_path)
    project.kwargs = {"graph": True}
    project._load_specs = mock.Mock(return_value=({}, []))
    project.show_inventory = mock.Mock()
    inventory = SimpleNamespace(path=str(tmp_path))

    project._process_spec(inventory, frozenset())

    project.show_inventory.assert_called_once_with(
            inventory, {}, frozenset(), [])
