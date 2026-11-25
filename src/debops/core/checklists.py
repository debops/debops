# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Checklist file parsing for the ``debops checklist`` commands.

A checklist is a GitHub-flavored Markdown document whose task-list
items carry their state in the brackets. Both marker sets parse as
synonyms; unknown bracket content parses as an open item.
"""

import re
from dataclasses import dataclass

import yaml

# Task items are list lines whose brackets carry a one-character state
# marker. Longer bracket content is commentary, not a state.
_ITEM_RE = re.compile(
    r"^(?P<indent>\s*)- \[(?P<marker>.?)\]\s*(?P<text>.*)$")

# The frontmatter block, when present, must start on the first line of
# the document; everything after the closing fence is the body.
_FRONTMATTER_RE = re.compile(r"\A---\n(?P<data>.*?)\n---\n", re.DOTALL)

_HEADING_RE = re.compile(r"^# (?P<title>.+)$", re.MULTILINE)

# Both marker sets parse as synonyms.
_MARKER_STATES = {
    " ": "open",
    "x": "done", "X": "done",
    "B": "blocked", "~": "blocked",
    "F": "failed", "!": "failed",
    "N": "not_applicable", "-": "not_applicable",
}

# Unknown bracket content parses as an open item.
_UNKNOWN_STATE = "open"

# States that count as open when deciding whether work remains.
_OPEN_STATES = ("open", "blocked")

_STATES = ("open", "done", "blocked", "failed", "not_applicable")


@dataclass(frozen=True)
class ChecklistItem:
    """One task item in a checklist, flattened from its nesting."""

    state: str
    depth: int
    text: str


@dataclass(frozen=True)
class ParsedChecklist:
    """The parsed form of a checklist document."""

    title: str | None
    frontmatter: dict
    items: list[ChecklistItem]

    @property
    def counts(self) -> dict[str, int]:
        """Number of items in each state."""
        counts = dict.fromkeys(_STATES, 0)
        for item in self.items:
            counts[item.state] += 1
        return counts

    @property
    def has_open_items(self) -> bool:
        """True when any item still counts as open (open or blocked)."""
        return any(item.state in _OPEN_STATES for item in self.items)


def parse_checklist(text: str) -> ParsedChecklist:
    """Parse checklist text into frontmatter, title and task items."""
    frontmatter, body = _split_frontmatter(text)
    return ParsedChecklist(
        title=_find_title(frontmatter, body),
        frontmatter=frontmatter,
        items=_parse_items(body),
    )


def _split_frontmatter(text: str) -> tuple[dict, str]:
    """Split YAML frontmatter off the document body."""
    match = _FRONTMATTER_RE.match(text)
    if match is None:
        return {}, text
    data = yaml.safe_load(match.group("data"))
    return (data if isinstance(data, dict) else {}), text[match.end():]


def _find_title(frontmatter: dict, body: str) -> str | None:
    """The frontmatter title, else the first ``#`` heading, else None."""
    if frontmatter.get("title"):
        return str(frontmatter["title"])
    match = _HEADING_RE.search(body)
    return match.group("title").strip() if match else None


def _parse_items(body: str) -> list[ChecklistItem]:
    """Collect task items, deriving nesting depth from indentation.

    Only task items enter the nesting stack; plain bullets and
    commentary do not affect the depth of later items.
    """
    items = []
    parents: list[int] = []
    for line in body.splitlines():
        match = _ITEM_RE.match(line)
        if match is None:
            continue
        indent = len(match.group("indent"))
        while parents and indent <= parents[-1]:
            parents.pop()
        items.append(ChecklistItem(
            state=_MARKER_STATES.get(match.group("marker"), _UNKNOWN_STATE),
            depth=len(parents),
            text=match.group("text").strip(),
        ))
        parents.append(indent)
    return items
