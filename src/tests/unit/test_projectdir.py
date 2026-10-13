# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for the self-contained helpers in ``debops.projectdir``.

``ProjectDir`` is constructed with a full project on disk and therefore
belongs to the integration tests; these cover the pure helpers that can be
exercised against small directory trees.
"""

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
