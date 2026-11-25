# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for ``debops.core.checklists`` parsing."""

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
