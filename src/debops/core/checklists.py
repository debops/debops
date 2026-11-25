# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""Checklist file parsing for the ``debops checklist`` commands.

A checklist is a GitHub-flavored Markdown document whose task-list
items carry their state in the brackets. Both marker sets parse as
synonyms; unknown bracket content parses as an open item.
"""

import json
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath

import yaml
from xdg.BaseDirectory import xdg_data_home

from .constants import DEBOPS_PACKAGE_DATA
from .exceptions import (
    ChecklistAlreadyOpenError,
    ChecklistAmbiguousError,
    ChecklistError,
    ChecklistNotFoundError,
    ChecklistNotOpenError,
)
from .utils import path_key

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


def _resolve_state_home() -> str:
    """``$XDG_STATE_HOME``, or the XDG base directory spec default.

    pyxdg 0.28 (Debian trixie) exposes ``xdg_state_home``; bookworm
    ships 0.27, which does not. The fallback computes the spec
    default, identical to pyxdg's own computation.
    """
    try:
        from xdg.BaseDirectory import xdg_state_home
        return xdg_state_home
    except ImportError:
        return os.environ.get('XDG_STATE_HOME') or os.path.join(
            os.path.expanduser('~'), '.local', 'state')


def checklist_state_dir(
    project_dir: str | Path,
    state_home: str | Path | None = None,
) -> Path:
    """The per-project state directory holding the open copies.

    The directory name starts with ``checklists-`` and carries the
    ``path_key()`` of the project directory, so same-named projects
    cannot collide and the copies of one project stay together.
    """
    if state_home is None:
        state_home = _resolve_state_home()
    name = Path(project_dir).name
    return Path(state_home) / 'debops' / ('checklists-' + path_key(
        project_dir, name))


def _ensure_private_dir(path: Path) -> None:
    """Create *path* and missing parents with 0700 permissions.

    Existing directories keep their mode -- only the directories this
    call creates are made private. The state tree can hold sensitive
    operational notes, so nothing it owns is world-readable.
    """
    missing = []
    current = path
    while not current.exists():
        missing.append(current)
        current = current.parent
    for directory in reversed(missing):
        try:
            directory.mkdir(mode=0o700)
        except FileExistsError:
            pass


def _has_open_files(copy_dir: Path) -> bool:
    """The active state of a copy id: any checklist file present."""
    return copy_dir.is_dir() and any(copy_dir.rglob('*.md'))


def open_copy(
    checklist_path: Path,
    checklist: str,
    origin: str,
    copy_id: str,
    state_dir: Path,
    reset: bool = False,
) -> Path:
    """Copy a checklist into the state directory as an open copy.

    Returns the path of the opened checklist file. A copy id holds
    exactly one checklist: opening an occupied id refuses unless
    *reset* discards the current state first.
    """
    _validate_name(copy_id)
    copy_dir = Path(state_dir) / copy_id
    if _has_open_files(copy_dir):
        if not reset:
            raise ChecklistAlreadyOpenError(
                f"Copy id already open: {copy_id}")
        shutil.rmtree(copy_dir)
    checklist = _strip_md(checklist)
    destination = copy_dir / f"{checklist}.md"
    _ensure_private_dir(destination.parent)
    shutil.copyfile(checklist_path, destination)
    sidecar = copy_dir / 'copy.json'
    sidecar.write_text(json.dumps({
        'opened': datetime.now().astimezone().isoformat(
            timespec='seconds'),
        'checklist': checklist,
        'origin': origin,
    }, indent=2) + '\n')
    return destination


@dataclass(frozen=True)
class OpenCopy:
    """An open copy as found in the state directory."""

    copy_id: str
    path: Path
    state_dir: Path
    checklist: str
    origin: str
    opened: datetime


def find_open_copies(state_dir: Path) -> list[OpenCopy]:
    """Scan the state directory for open copies, ordered by id."""
    state_dir = Path(state_dir)
    if not state_dir.is_dir():
        return []
    copies = []
    for copy_dir in sorted(state_dir.iterdir()):
        if not copy_dir.is_dir():
            continue
        for md in sorted(copy_dir.rglob('*.md')):
            copies.append(_open_copy_record(state_dir, copy_dir, md))
    return copies


def _open_copy_record(state_dir: Path, copy_dir: Path, md: Path) -> OpenCopy:
    """Assemble an open-copy record, falling back to the mtime.

    A missing or corrupt sidecar costs the recorded metadata: the
    checklist name is derived from the file layout and the open date
    from the file's mtime.
    """
    checklist = _strip_md(md.relative_to(copy_dir).as_posix())
    origin = ''
    opened = None
    try:
        data = json.loads((copy_dir / 'copy.json').read_text())
        checklist = data.get('checklist', checklist)
        origin = data.get('origin', '')
        opened = data.get('opened')
    except (OSError, json.JSONDecodeError, ValueError):
        pass
    if opened is None:
        opened = datetime.fromtimestamp(md.stat().st_mtime).astimezone()
    else:
        opened = datetime.fromisoformat(opened)
    return OpenCopy(
        copy_id=copy_dir.name, path=md, state_dir=state_dir,
        checklist=checklist, origin=origin, opened=opened)


def resolve_copy(target: str, state_dir: Path) -> tuple[str, Path]:
    """Resolve an edit/commit/close target to its copy id and file.

    An exact copy id wins; otherwise the target is matched against
    the checklist path of the open copies. One match resolves,
    several are ambiguous, none means the target is not open.
    """
    copies = find_open_copies(state_dir)
    for copy in copies:
        if copy.copy_id == target:
            return copy.copy_id, copy.path
    name = _strip_md(target)
    matches = [copy for copy in copies if copy.checklist == name]
    if not matches:
        raise ChecklistNotOpenError(f"Checklist copy not open: {target}")
    if len(matches) > 1:
        ids = ', '.join(sorted(copy.copy_id for copy in matches))
        raise ChecklistAmbiguousError(f"Several open copies of {name}: {ids}")
    return matches[0].copy_id, matches[0].path


def close_copy(state_dir: Path, copy_id: str) -> None:
    """Discard an open copy, pruning the state directory if empty."""
    copy_dir = Path(state_dir) / copy_id
    shutil.rmtree(copy_dir)
    state_dir = Path(state_dir)
    if state_dir.is_dir() and not any(state_dir.iterdir()):
        state_dir.rmdir()


def vault_record_path(
    vault_dir: str | Path,
    checklist: str,
    copy_id: str,
    opened: datetime,
) -> Path:
    """The vault record path for one committed copy.

    Records group by checklist; the copy id directory appears only
    for named copies, where the id differs from the checklist path.
    The filename is the open date -- the sidecar's ``opened``, stable
    for the copy's whole life -- so same-day re-commits overwrite the
    copy's own record and the history lives in git.
    """
    record = Path(vault_dir) / 'checklists' / _strip_md(checklist)
    if copy_id != _strip_md(checklist):
        record /= copy_id
    return record / f"{opened.date().isoformat()}.md"


def checklist_layers(
    project_dir: str | Path | None = None,
) -> list[tuple[Path, str]]:
    """The checklist discovery layers, most specific first.

    The project layer wins over the user layer, which wins over the
    packaged layer. Contexts without a project -- ``checklist list``
    outside a project directory -- simply omit the first layer.
    """
    layers = []
    if project_dir is not None:
        layers.append(
            (Path(project_dir) / '.debops' / 'checklists', 'project'))
    layers.append((Path(xdg_data_home) / 'debops' / 'checklists', 'user'))
    layers.append((Path(DEBOPS_PACKAGE_DATA) / 'checklists', 'packaged'))
    return layers


def find_checklist(
    name: str,
    layers: list[tuple[Path, str]],
) -> tuple[Path, str]:
    """Resolve a checklist name against the discovery layers.

    Layers are ``(root, origin)`` pairs; the first existing file wins
    and its origin is returned alongside the path. A name may be given
    with or without the ``.md`` suffix -- both spellings resolve
    identically regardless of how the file is stored.
    """
    _validate_name(name)
    candidates = [name]
    stripped = _strip_md(name)
    if stripped != name:
        candidates.append(stripped)
    else:
        candidates.append(name + '.md')
    for root, origin in layers:
        for candidate in candidates:
            path = root / candidate
            if path.is_file():
                return path, origin
    raise ChecklistNotFoundError(f"Checklist not found: {name}")


def _strip_md(name: str) -> str:
    """The checklist name without its ``.md`` suffix, if present."""
    return name[:-3] if name.endswith('.md') else name


def _validate_name(name: str) -> None:
    """Reject absolute names and names escaping their root.

    The check runs on the name itself, before any join: an absolute
    name would replace the root outright, and ``..`` parts would
    escape it. Checklist names and copy ids share the rule.
    """
    parts = PurePosixPath(name).parts
    if not name or PurePosixPath(name).is_absolute() or '..' in parts:
        raise ChecklistError(f"Invalid checklist name: {name!r}")
