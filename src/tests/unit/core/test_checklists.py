# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for ``debops.core.checklists`` parsing and discovery."""

import json
import os
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from debops.core import checklists, utils


@pytest.mark.parametrize("marker, state", [
    (" ", "open"),
    ("x", "done"),
    ("X", "done"),
    ("B", "blocked"),
    ("~", "blocked"),
    ("F", "failed"),
    ("!", "failed"),
    ("N", "not_applicable"),
    ("-", "not_applicable"),
])
def test_each_marker_parses_to_its_state(marker, state):
    parsed = checklists.parse_checklist(f"- [{marker}] Do a thing")
    assert parsed.items[0].state == state


@pytest.mark.parametrize("marker", ["", "?", "W"])
def test_unknown_marker_parses_as_open(marker):
    parsed = checklists.parse_checklist(f"- [{marker}] Do a thing")
    assert parsed.items[0].state == "open"


def test_multichar_bracket_content_is_not_an_item():
    parsed = checklists.parse_checklist("- [TODO] Do a thing")
    assert parsed.items == []


def test_nested_items_get_depth():
    text = (
        "- [ ] Parent task\n"
        "    - [x] Child task\n"
        "        - [ ] Grandchild task\n"
        "- [ ] Next parent\n"
    )
    parsed = checklists.parse_checklist(text)
    assert [item.depth for item in parsed.items] == [0, 1, 2, 0]


def test_sibling_subitems_share_depth():
    text = (
        "- [ ] Parent task\n"
        "    - [x] First child\n"
        "    - [ ] Second child\n"
    )
    parsed = checklists.parse_checklist(text)
    assert [item.depth for item in parsed.items] == [0, 1, 1]


def test_non_item_lines_are_ignored():
    text = (
        "# Section\n"
        "\n"
        "Prose paragraph.\n"
        "\n"
        "- plain bullet, not a task\n"
        "  - indented plain bullet\n"
        "- [ ] Real task\n"
    )
    parsed = checklists.parse_checklist(text)
    assert len(parsed.items) == 1
    assert parsed.items[0].text == "Real task"


def test_item_text_is_captured_without_the_marker():
    parsed = checklists.parse_checklist("- [x] Verify the backups\n")
    assert parsed.items[0].text == "Verify the backups"


def test_frontmatter_title_wins_over_first_heading():
    text = (
        "---\n"
        'title: "Review the backups"\n'
        "---\n"
        "# Not this heading\n"
        "- [ ] Task\n"
    )
    parsed = checklists.parse_checklist(text)
    assert parsed.title == "Review the backups"


def test_missing_frontmatter_falls_back_to_first_heading():
    text = "# Reboot a host\n\n- [ ] Announce the window\n"
    parsed = checklists.parse_checklist(text)
    assert parsed.title == "Reboot a host"


def test_frontmatter_keys_are_exposed_verbatim():
    text = (
        "---\n"
        'title: "T"\n'
        'description: "D"\n'
        "documentation:\n"
        "  - https://example.com/notes\n"
        "---\n"
        "- [ ] Task\n"
    )
    parsed = checklists.parse_checklist(text)
    assert parsed.frontmatter["documentation"] == [
        "https://example.com/notes"]
    assert parsed.frontmatter["description"] == "D"


def test_document_without_frontmatter_has_empty_frontmatter():
    parsed = checklists.parse_checklist("- [ ] Task\n")
    assert parsed.frontmatter == {}


def test_tally_counts_each_state():
    text = (
        "- [ ] Open task\n"
        "- [x] Done task\n"
        "- [B] Blocked task\n"
        "- [F] Failed task\n"
        "- [N] Skipped task\n"
    )
    parsed = checklists.parse_checklist(text)
    assert parsed.counts == {
        "open": 1,
        "done": 1,
        "blocked": 1,
        "failed": 1,
        "not_applicable": 1,
    }


def test_open_item_detection_counts_blocked_as_open():
    parsed = checklists.parse_checklist("- [x] Done\n- [B] Blocked\n")
    assert parsed.has_open_items


def test_fully_resolved_checklist_has_no_open_items():
    text = "- [x] Done\n- [F] Failed\n- [N] Skipped\n"
    parsed = checklists.parse_checklist(text)
    assert not parsed.has_open_items


@pytest.fixture
def layer_roots(tmp_path):
    """Three discovery roots: project, user and packaged."""
    project = tmp_path / "project" / ".debops" / "checklists"
    user = tmp_path / "user" / "checklists"
    packaged = tmp_path / "packaged" / "checklists"
    for root in (project, user, packaged):
        root.mkdir(parents=True)
    return project, user, packaged


def _layers(project, user, packaged):
    return [(project, "project"), (user, "user"), (packaged, "packaged")]


def test_find_checklist_prefers_the_project_layer(layer_roots):
    project, user, packaged = layer_roots
    for root in (project, user, packaged):
        path = root / "audit" / "review.md"
        path.parent.mkdir(parents=True)
        path.write_text("# Review\n")
    found, origin = checklists.find_checklist(
        "audit/review", _layers(*layer_roots))
    assert found == project / "audit" / "review.md"
    assert origin == "project"


def test_find_checklist_falls_back_through_the_layers(layer_roots):
    project, user, packaged = layer_roots
    (packaged / "system").mkdir()
    (packaged / "system" / "host-reboot.md").write_text("# Reboot\n")
    found, origin = checklists.find_checklist(
        "system/host-reboot", _layers(*layer_roots))
    assert found == packaged / "system" / "host-reboot.md"
    assert origin == "packaged"

    (user / "system").mkdir()
    (user / "system" / "host-reboot.md").write_text("# Reboot\n")
    found, origin = checklists.find_checklist(
        "system/host-reboot", _layers(*layer_roots))
    assert found == user / "system" / "host-reboot.md"
    assert origin == "user"


def test_missing_layers_are_tolerated(layer_roots):
    project, user, packaged = layer_roots
    (packaged / "system").mkdir()
    (packaged / "system" / "host-reboot.md").write_text("# Reboot\n")
    found, origin = checklists.find_checklist(
        "system/host-reboot", _layers(*layer_roots))
    assert origin == "packaged"

    missing = [(Path("/nonexistent") / "project", "project"),
               (Path("/nonexistent") / "user", "user"),
               (packaged, "packaged")]
    found, origin = checklists.find_checklist(
        "system/host-reboot", missing)
    assert origin == "packaged"


def test_md_less_and_md_suffixed_names_resolve_identically(layer_roots):
    project, user, packaged = layer_roots
    (project / "system").mkdir()
    (project / "system" / "host-reboot.md").write_text("# Reboot\n")
    with_suffix, _ = checklists.find_checklist(
        "system/host-reboot.md", _layers(*layer_roots))
    without_suffix, _ = checklists.find_checklist(
        "system/host-reboot", _layers(*layer_roots))
    assert with_suffix == without_suffix

    (project / "plain").write_text("# Plain\n")
    found, _ = checklists.find_checklist("plain.md", _layers(*layer_roots))
    assert found == project / "plain"


@pytest.mark.parametrize("name", [
    "../secret",
    "audit/../secret.md",
    "/etc/passwd",
    "",
])
def test_traversal_and_invalid_names_are_rejected(layer_roots, name):
    with pytest.raises(checklists.ChecklistError):
        checklists.find_checklist(name, _layers(*layer_roots))


def test_unknown_checklist_raises_not_found(layer_roots):
    with pytest.raises(checklists.ChecklistNotFoundError):
        checklists.find_checklist("no/such/checklist", _layers(*layer_roots))


def test_checklist_layers_order_and_roots(tmp_path, monkeypatch):
    monkeypatch.setattr(checklists, "xdg_data_home", str(tmp_path / "data"))
    project = tmp_path / "project"
    layers = checklists.checklist_layers(project_dir=project)
    assert layers == [
        (project / ".debops" / "checklists", "project"),
        (tmp_path / "data" / "debops" / "checklists", "user"),
        (Path(checklists.DEBOPS_PACKAGE_DATA) / "checklists", "packaged"),
    ]

    without_project = checklists.checklist_layers()
    assert [origin for _, origin in without_project] == [
        "user", "packaged"]


def test_state_home_uses_pyxdg_when_available():
    from xdg.BaseDirectory import xdg_state_home
    assert checklists._resolve_state_home() == xdg_state_home


def test_state_home_honors_the_environment_without_pyxdg(monkeypatch):
    monkeypatch.setenv("XDG_STATE_HOME", "/state")
    monkeypatch.setitem(sys.modules, "xdg", None)
    monkeypatch.setitem(sys.modules, "xdg.BaseDirectory", None)
    assert checklists._resolve_state_home() == "/state"


def test_state_home_falls_back_to_the_spec_default(monkeypatch):
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    monkeypatch.setitem(sys.modules, "xdg", None)
    monkeypatch.setitem(sys.modules, "xdg.BaseDirectory", None)
    expected = os.path.join(os.path.expanduser("~"), ".local", "state")
    assert checklists._resolve_state_home() == expected


def test_checklist_state_dir_namespaces_by_project(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    dir_first = checklists.checklist_state_dir(first, state_home="/state")
    dir_second = checklists.checklist_state_dir(second, state_home="/state")
    expected = Path("/state") / "debops" / (
        "checklists-" + utils.path_key(first, first.name))
    assert dir_first == expected
    assert dir_first != dir_second
    assert dir_first.name.startswith("checklists-")


def _write_checklist(path, content="# Review\n- [ ] Check\n"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def test_open_copies_the_checklist_and_writes_the_sidecar(tmp_path):
    state = tmp_path / "state"
    source = _write_checklist(tmp_path / "packaged" / "audit" / "review.md")
    opened = checklists.open_copy(
        source, "audit/review", "packaged", "review", state)

    assert opened == state / "review" / "audit" / "review.md"
    assert opened.read_text() == source.read_text()

    sidecar = json.loads((state / "review" / "copy.json").read_text())
    assert sidecar["checklist"] == "audit/review"
    assert sidecar["origin"] == "packaged"
    parsed_opened = datetime.fromisoformat(sidecar["opened"])
    assert parsed_opened.tzinfo is not None


def test_open_creates_private_state_directories(tmp_path):
    def mode(path):
        return stat.S_IMODE(path.stat().st_mode)

    state = tmp_path / "state"
    source = _write_checklist(tmp_path / "packaged" / "audit" / "review.md")
    checklists.open_copy(
        source, "audit/review", "packaged", "review", state)
    assert mode(state) == 0o700
    assert mode(state / "review") == 0o700
    assert mode(state / "review" / "audit") == 0o700


def test_open_refuses_an_occupied_copy_id(tmp_path):
    state = tmp_path / "state"
    source = _write_checklist(tmp_path / "packaged" / "audit" / "review.md")
    checklists.open_copy(source, "audit/review", "packaged", "review", state)
    other = _write_checklist(tmp_path / "packaged" / "other" / "other.md")
    with pytest.raises(checklists.ChecklistAlreadyOpenError):
        checklists.open_copy(other, "other/other", "packaged", "review",
                             state)


def test_open_reset_replaces_the_copy_state(tmp_path):
    state = tmp_path / "state"
    first = _write_checklist(tmp_path / "packaged" / "audit" / "review.md",
                             "# First\n")
    checklists.open_copy(first, "audit/review", "packaged", "review", state)
    second = _write_checklist(tmp_path / "user" / "audit" / "review.md",
                              "# Second\n")
    opened = checklists.open_copy(
        second, "audit/review", "user", "review", state, reset=True)
    assert opened.read_text() == "# Second\n"
    sidecar = json.loads((state / "review" / "copy.json").read_text())
    assert sidecar["origin"] == "user"


def test_open_rejects_traversal_copy_ids(tmp_path):
    source = _write_checklist(tmp_path / "packaged" / "audit" / "review.md")
    with pytest.raises(checklists.ChecklistError):
        checklists.open_copy(
            source, "audit/review", "packaged", "../escape",
            tmp_path / "state")


def test_find_open_copies_reads_the_sidecars(tmp_path):
    state = tmp_path / "state"
    review = _write_checklist(tmp_path / "packaged" / "audit" / "review.md")
    reboot = _write_checklist(tmp_path / "packaged" / "system" / "reboot.md")
    checklists.open_copy(review, "audit/review", "packaged", "web", state)
    checklists.open_copy(reboot, "system/reboot", "packaged", "db", state)

    copies = {copy.copy_id: copy for copy in
              checklists.find_open_copies(state)}
    assert set(copies) == {"web", "db"}
    assert copies["web"].checklist == "audit/review"
    assert copies["web"].origin == "packaged"
    assert copies["web"].opened.tzinfo is not None
    assert copies["db"].path == state / "db" / "system" / "reboot.md"


def test_find_open_copies_falls_back_to_mtime(tmp_path):
    state = tmp_path / "state"
    source = _write_checklist(tmp_path / "packaged" / "audit" / "review.md")
    opened = checklists.open_copy(
        source, "audit/review", "packaged", "web", state)
    (state / "web" / "copy.json").unlink()

    records = checklists.find_open_copies(state)
    assert records[0].checklist == "audit/review"
    expected = datetime.fromtimestamp(
        opened.stat().st_mtime).astimezone()
    assert records[0].opened == expected


def test_resolve_prefers_the_exact_copy_id(tmp_path):
    state = tmp_path / "state"
    source = _write_checklist(tmp_path / "packaged" / "audit" / "review.md")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    copy = checklists.resolve_copy("web", state)
    assert copy.copy_id == "web"
    assert copy.path == state / "web" / "audit" / "review.md"


def test_resolve_falls_back_to_the_checklist_path(tmp_path):
    state = tmp_path / "state"
    source = _write_checklist(tmp_path / "packaged" / "audit" / "review.md")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    for target in ("audit/review", "audit/review.md"):
        copy = checklists.resolve_copy(target, state)
        assert copy.copy_id == "web"


def test_resolve_lists_ids_when_ambiguous(tmp_path):
    state = tmp_path / "state"
    source = _write_checklist(tmp_path / "packaged" / "audit" / "review.md")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    checklists.open_copy(source, "audit/review", "packaged", "db", state)
    with pytest.raises(checklists.ChecklistAmbiguousError) as raised:
        checklists.resolve_copy("audit/review", state)
    assert "db" in str(raised.value)
    assert "web" in str(raised.value)


def test_resolve_raises_when_the_target_is_not_open(tmp_path):
    with pytest.raises(checklists.ChecklistNotOpenError):
        checklists.resolve_copy("audit/review", tmp_path / "state")


def test_close_removes_the_copy_and_prunes_the_state(tmp_path):
    state = tmp_path / "state"
    source = _write_checklist(tmp_path / "packaged" / "audit" / "review.md")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    checklists.close_copy(state, "web")
    assert not (state / "web").exists()
    assert not state.exists()


def test_close_keeps_the_state_dir_for_remaining_copies(tmp_path):
    state = tmp_path / "state"
    review = _write_checklist(tmp_path / "packaged" / "audit" / "review.md")
    reboot = _write_checklist(tmp_path / "packaged" / "system" / "reboot.md")
    checklists.open_copy(review, "audit/review", "packaged", "web", state)
    checklists.open_copy(reboot, "system/reboot", "packaged", "db", state)
    checklists.close_copy(state, "web")
    assert (state / "db").exists()
    assert state.exists()


def test_vault_record_path_groups_by_checklist(tmp_path):
    opened = datetime(2026, 11, 10, 23, 50, tzinfo=timezone.utc)
    implicit = checklists.vault_record_path(
        tmp_path, "system/host-reboot", "system/host-reboot", opened)
    assert implicit == (tmp_path / "checklists" / "system" /
                        "host-reboot" / "2026-11-10.md")


def test_vault_record_path_nests_named_copies(tmp_path):
    opened = datetime(2026, 5, 11, 9, 0, tzinfo=timezone.utc)
    named = checklists.vault_record_path(
        tmp_path, "audit/periodic-security-review", "review", opened)
    assert named == (tmp_path / "checklists" / "audit" /
                     "periodic-security-review" / "review" /
                     "2026-05-11.md")


def test_progress_summarizes_the_counts():
    text = (
        "- [x] First\n"
        "- [x] Second\n"
        "- [B] Third\n"
        "- [F] Fourth\n"
        "- [ ] Fifth\n"
    )
    parsed = checklists.parse_checklist(text)
    assert parsed.progress == "2/5 done, 1 blocked, 1 failed"


def test_list_checklists_shadows_and_sorts(tmp_path):
    project = tmp_path / "project"
    user = tmp_path / "user"
    packaged = tmp_path / "packaged"
    for root in (project, user, packaged):
        (root / "audit").mkdir(parents=True)
    (project / "audit" / "review.md").write_text("# Review\n")
    (packaged / "system").mkdir()
    (packaged / "system" / "reboot.md").write_text("# Reboot\n")
    (user / "zzz.md").write_text("# Zzz\n")

    entries = checklists.list_checklists([
        (project, "project"), (user, "user"), (packaged, "packaged")])
    assert [name for name, _, _ in entries] == [
        "audit/review", "system/reboot", "zzz"]
    assert entries[0][2] == "project"
    assert entries[1][2] == "packaged"
    assert entries[2][2] == "user"


def test_editor_argv_prefers_visual():
    environ = {"VISUAL": "code -w", "EDITOR": "vim"}
    assert checklists.editor_argv(environ) == ["code", "-w"]


def test_editor_argv_uses_the_editor_variable():
    assert checklists.editor_argv({"EDITOR": "nano"}) == ["nano"]


def test_editor_argv_uses_sensible_editor(monkeypatch):
    monkeypatch.setattr(checklists.shutil, "which",
                        lambda name: "/usr/bin/" + name)
    assert checklists.editor_argv({}) == ["sensible-editor"]


def test_editor_argv_falls_back_to_vi(monkeypatch):
    monkeypatch.setattr(checklists.shutil, "which", lambda name: None)
    assert checklists.editor_argv({}) == ["vi"]
