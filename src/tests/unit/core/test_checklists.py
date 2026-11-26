# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for ``debops.core.checklists`` parsing and discovery."""

import inspect
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


@pytest.mark.parametrize("line", [
    "* [x] Asterisk bullet",
    "+ [x] Plus bullet",
    "1. [x] Ordered with a dot",
    "2) [x] Ordered with a parenthesis",
    "  * [x] Indented asterisk bullet",
])
def test_github_task_list_bullets_all_parse(line):
    parsed = checklists.parse_checklist(line)
    assert len(parsed.items) == 1
    assert parsed.items[0].state == "done"


def test_fenced_blocks_do_not_carry_items():
    text = ("- [x] Before\n"
            "```sh\n"
            "- [ ] Inside a fence\n"
            "echo example\n"
            "```\n"
            "- [ ] After the fence\n")
    parsed = checklists.parse_checklist(text)
    assert [item.text for item in parsed.items] == \
        ['Before', 'After the fence']


def test_tilde_fences_do_not_carry_items():
    text = ("- [x] Before\n"
            "~~~\n"
            "- [ ] Inside a fence\n"
            "~~~\n")
    parsed = checklists.parse_checklist(text)
    assert [item.text for item in parsed.items] == ['Before']


def test_document_without_task_items_parses_to_none():
    parsed = checklists.parse_checklist("# Notes\n\nJust prose.\n")
    assert parsed.items == []
    assert parsed.has_open_items is False


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


def test_broken_frontmatter_degrades_to_no_frontmatter():
    text = "---\ntitle: [unclosed\n---\n# Heading\n- [ ] Task\n"
    parsed = checklists.parse_checklist(text)
    assert parsed.frontmatter == {}
    assert parsed.title == "Heading"
    assert len(parsed.items) == 1


def test_deeply_nested_frontmatter_does_not_crash():
    text = "---\ntitle: " + "[" * 50000 + "\n---\n# Heading\n"
    parsed = checklists.parse_checklist(text)
    assert parsed.frontmatter == {}
    assert parsed.title == "Heading"


def test_oversized_frontmatter_is_treated_as_absent():
    text = "---\ndescription: '" + "x" * 70000 + "'\n---\n# Heading\n"
    parsed = checklists.parse_checklist(text)
    assert parsed.frontmatter == {}
    assert parsed.title == "Heading"


def test_control_characters_are_stripped_from_titles():
    text = "---\ntitle: \"Review \\x1b]0;pwned\\x07 done\"\n---\n"
    parsed = checklists.parse_checklist(text)
    assert parsed.title == "Review ]0;pwned done"


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


def test_find_checklist_refuses_a_symlink_escaping_the_layer(layer_roots):
    project, user, packaged = layer_roots
    secret = project.parent.parent / "secret.txt"
    secret.write_text("private key material\n")
    (project / "notes.md").symlink_to(secret)
    with pytest.raises(checklists.ChecklistError) as raised:
        checklists.find_checklist("notes", _layers(*layer_roots))
    assert "outside of its discovery layer" in str(raised.value)


def test_list_omits_symlinks_escaping_the_layer(layer_roots):
    project, user, packaged = layer_roots
    secret = project.parent.parent / "secret.txt"
    secret.write_text("private key material\n")
    (project / "notes.md").symlink_to(secret)
    (packaged / "audit").mkdir()
    (packaged / "audit" / "review.md").write_text("# Review\n")
    names = [name for name, path, origin in
             checklists.list_checklists(_layers(*layer_roots))]
    assert names == ["audit/review"]


def test_user_layer_honors_symlinked_checklists(layer_roots):
    project, user, packaged = layer_roots
    outside = user.parent.parent / "personal-notes.md"
    outside.write_text("# Personal\n- [x] Note\n")
    (user / "notes.md").symlink_to(outside)
    found, origin = checklists.find_checklist(
        "notes", _layers(*layer_roots))
    assert found == user / "notes.md"
    assert origin == "user"
    names = [name for name, path, entry_origin in
             checklists.list_checklists(_layers(*layer_roots))]
    assert names == ["notes"]


@pytest.fixture
def example_tree(layer_roots):
    """A packaged tree with an example namespace and a system one."""
    project, user, packaged = layer_roots
    example = packaged / "example" / "audit"
    example.mkdir(parents=True)
    (example / "review.md").write_text("# Review\n")
    (packaged / "system").mkdir()
    (packaged / "system" / "reboot.md").write_text("# Reboot\n")
    (packaged / "notes.md").write_text("# Notes\n")
    return _layers(*layer_roots)


def test_filters_hide_a_whole_namespace(example_tree):
    names = [name for name, path, origin in checklists.list_checklists(
        example_tree, filters=["!example/**"])]
    assert names == ["notes", "system/reboot"]


def test_filters_star_stops_at_the_slash(example_tree):
    names = [name for name, path, origin in checklists.list_checklists(
        example_tree, filters=["!example/*"])]
    assert "example/audit/review" in names


def test_filters_last_matching_rule_wins(example_tree):
    names = [name for name, path, origin in checklists.list_checklists(
        example_tree, filters=["!example/**", "example/audit/**"])]
    assert names == ["example/audit/review", "notes", "system/reboot"]


def test_filters_without_a_match_stay_visible(example_tree):
    # A bare pattern keeps its matches visible; everything else is
    # visible by default, so a lone bare rule restricts nothing
    names = [name for name, path, origin in checklists.list_checklists(
        example_tree, filters=["system/**"])]
    assert names == ["example/audit/review", "notes", "system/reboot"]


def test_filters_allowlist_through_the_hide_all_anchor(example_tree):
    names = [name for name, path, origin in checklists.list_checklists(
        example_tree, filters=["!**", "system/**"])]
    assert names == ["system/reboot"]


def test_filters_empty_rules_hide_nothing(example_tree):
    names = [name for name, path, origin in checklists.list_checklists(
        example_tree, filters=[])]
    assert len(names) == 3


def test_find_checklist_refuses_a_hidden_name(example_tree):
    with pytest.raises(checklists.ChecklistFilteredError) as raised:
        checklists.find_checklist(
            "example/audit/review", example_tree,
            filters=["!example/**"])
    assert "hidden by checklist.filters" in str(raised.value)


def test_find_checklist_resolves_a_visible_name(example_tree):
    found, origin = checklists.find_checklist(
        "system/reboot", example_tree, filters=["!example/**"])
    assert found == example_tree[2][0] / "system" / "reboot.md"


def test_filters_refuse_a_malformed_pattern(example_tree):
    with pytest.raises(checklists.ChecklistError) as raised:
        checklists.list_checklists(
            example_tree, filters=["system/[z-a]"])
    assert "Invalid checklist.filters pattern" in str(raised.value)


def test_filters_refuse_an_over_complex_pattern(example_tree):
    with pytest.raises(checklists.ChecklistError) as raised:
        checklists.list_checklists(
            example_tree, filters=["a*b*c*d*e*f*g*"])
    assert "too complex" in str(raised.value)
    with pytest.raises(checklists.ChecklistError):
        checklists.list_checklists(
            example_tree, filters=["a" * 129])


def test_validate_name_refuses_a_bare_dot():
    with pytest.raises(checklists.ChecklistError):
        checklists.validate_name(".")


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
    "_copies",
    "audit/_copies",
    "with\x1bescape",
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

    assert opened == state / "review" / "checklist.md"
    assert opened.read_text() == source.read_text()

    sidecar = json.loads((state / "review" / "copy.json").read_text())
    assert sidecar["checklist"] == "audit/review"
    assert sidecar["origin"] == "packaged"
    assert sidecar["filename"] == "checklist.md"
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
    assert copies["db"].path == state / "db" / "checklist.md"


def test_find_open_copies_falls_back_to_mtime(tmp_path):
    state = tmp_path / "state"
    source = _write_checklist(tmp_path / "packaged" / "audit" / "review.md")
    opened = checklists.open_copy(
        source, "audit/review", "packaged", "web", state)
    (state / "web" / "copy.json").unlink()

    records = checklists.find_open_copies(state)
    assert records[0].copy_id == "web"
    assert records[0].checklist == ""
    expected = datetime.fromtimestamp(
        opened.stat().st_mtime).astimezone()
    assert records[0].opened == expected


def test_hostile_sidecar_fields_fall_back_to_the_standards(tmp_path):
    state = tmp_path / "state"
    source = _write_checklist(tmp_path / "packaged" / "audit" / "review.md")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    (state / "web" / "copy.json").write_text(
        '{"filename": "../../escape.md", "checklist": "../../x", '
        '"origin": ["not", "a", "label"], '
        '"opened": "2026-11-10T08:00:00+00:00"}')

    records = checklists.find_open_copies(state)
    assert records[0].copy_id == "web"
    assert records[0].path == state / "web" / "checklist.md"
    assert records[0].checklist == ""
    assert records[0].origin == ""
    assert records[0].opened == datetime(
        2026, 11, 10, 8, 0, tzinfo=timezone.utc)


def test_slash_copy_ids_round_trip(tmp_path):
    state = tmp_path / "state"
    source = _write_checklist(tmp_path / "packaged" / "debian" / "up.md")
    copy_id = "debian/dist-upgrade/bookworm-to-trixie"
    checklists.open_copy(source, "debian/upgrade", "packaged", copy_id,
                         state)

    copies = checklists.find_open_copies(state)
    assert [copy.copy_id for copy in copies] == [copy_id]
    assert copies[0].checklist == "debian/upgrade"

    resolved = checklists.resolve_copy(copy_id, state)
    assert resolved.checklist == "debian/upgrade"
    resolved = checklists.resolve_copy("debian/upgrade", state)
    assert resolved.copy_id == copy_id

    checklists.close_copy(state, copy_id)
    assert not checklists.find_open_copies(state)
    assert not state.exists()


def test_close_keeps_nested_copies(tmp_path):
    state = tmp_path / "state"
    first = _write_checklist(tmp_path / "packaged" / "a.md")
    second = _write_checklist(tmp_path / "packaged" / "b.md")
    checklists.open_copy(first, "a", "packaged", "a", state)
    checklists.open_copy(second, "b", "packaged", "a/b", state)

    checklists.close_copy(state, "a")

    assert (state / "a" / "b" / "checklist.md").is_file()
    remaining = checklists.find_open_copies(state)
    assert [copy.copy_id for copy in remaining] == ["a/b"]


def test_corrupt_sidecar_leaves_the_id_resolvable(tmp_path):
    state = tmp_path / "state"
    source = _write_checklist(tmp_path / "packaged" / "a.md")
    checklists.open_copy(source, "a", "packaged", "web", state)
    (state / "web" / "copy.json").write_text("{not json")

    records = checklists.find_open_copies(state)
    assert records[0].copy_id == "web"
    assert records[0].checklist == ""
    copy = checklists.resolve_copy("web", state)
    assert copy.copy_id == "web"


def test_resolve_prefers_the_exact_copy_id(tmp_path):
    state = tmp_path / "state"
    source = _write_checklist(tmp_path / "packaged" / "audit" / "review.md")
    checklists.open_copy(source, "audit/review", "packaged", "web", state)
    copy = checklists.resolve_copy("web", state)
    assert copy.copy_id == "web"
    assert copy.path == state / "web" / "checklist.md"


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
    assert implicit == (tmp_path / "system" /
                        "host-reboot" / "2026-11-10.md")


def test_vault_record_path_nests_named_copies(tmp_path):
    opened = datetime(2026, 5, 11, 9, 0, tzinfo=timezone.utc)
    named = checklists.vault_record_path(
        tmp_path, "audit/periodic-security-review", "review", opened)
    assert named == (tmp_path / "audit" /
                     "periodic-security-review" / "_copies" / "review" /
                     "2026-05-11.md")


def test_vault_record_paths_of_named_and_implicit_copies_differ(tmp_path):
    opened = datetime(2026, 5, 11, 9, 0, tzinfo=timezone.utc)
    named = checklists.vault_record_path(
        tmp_path, "security", "web1", opened)
    implicit = checklists.vault_record_path(
        tmp_path, "security/web1", "security/web1", opened)
    assert named != implicit
    assert named == tmp_path / "security" / "_copies" / "web1" / \
        "2026-05-11.md"
    assert implicit == tmp_path / "security" / "web1" / "2026-05-11.md"


def test_copies_segment_is_refused_in_names(layer_roots):
    for name in ("_copies", "audit/_copies", "audit/_copies/review"):
        with pytest.raises(checklists.ChecklistError):
            checklists.find_checklist(name, _layers(*layer_roots))
    with pytest.raises(checklists.ChecklistError):
        checklists.open_copy(layer_roots[0] / "x.md", "audit/review",
                             "project", "_copies",
                             layer_roots[0].parent.parent / "state")


def test_close_copy_refuses_an_invalid_id(tmp_path):
    state = tmp_path / "state"
    state.mkdir()
    with pytest.raises(checklists.ChecklistError):
        checklists.close_copy(state, "../escape")
    with pytest.raises(checklists.ChecklistError):
        checklists.close_copy(state, "with\x1bescape")


def test_open_copy_reset_is_keyword_only():
    signature = inspect.signature(checklists.open_copy)
    assert signature.parameters["reset"].kind == \
        inspect.Parameter.KEYWORD_ONLY


def test_implicit_copies_recognize_themselves():
    opened = datetime(2026, 11, 10, 8, 0, tzinfo=timezone.utc)
    implicit = checklists.OpenCopy(
        copy_id="audit/review", path=Path("/state/audit/review/checklist.md"),
        state_dir=Path("/state"), checklist="audit/review",
        origin="packaged", opened=opened)
    named = checklists.OpenCopy(
        copy_id="web", path=Path("/state/web/checklist.md"),
        state_dir=Path("/state"), checklist="audit/review",
        origin="packaged", opened=opened)
    assert implicit.implicit is True
    assert named.implicit is False


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


def test_editor_argv_refuses_an_unsplitable_value():
    with pytest.raises(checklists.ChecklistError) as raised:
        checklists.editor_argv({"EDITOR": "vi 'broken"})
    assert "EDITOR" in str(raised.value)


def test_editor_argv_treats_an_empty_split_as_unset():
    environ = {"VISUAL": "   ", "EDITOR": "xterm -e"}
    assert checklists.editor_argv(environ) == ["xterm", "-e"]
