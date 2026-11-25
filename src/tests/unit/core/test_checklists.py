# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for ``debops.core.checklists`` parsing and discovery."""

from pathlib import Path

import pytest

from debops.core import checklists


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
