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
import shlex
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
    ChecklistFilteredError,
    ChecklistNotFoundError,
    ChecklistNotOpenError,
)
from .utils import path_key
import hashlib

# Task items are list lines whose brackets carry a one-character state
# marker. The list marker follows the GitHub task-list syntax: dash,
# asterisk and plus bullets, ordered items with a dot or a parenthesis.
# Longer bracket content is commentary, not a state.
_ITEM_RE = re.compile(
    r"^(?P<indent>\s*)(?:[-*+]|\d+[.)]) \[(?P<marker>.?)\]\s*(?P<text>.*)$")

# Fenced code blocks do not carry task items; a fence toggles until a
# closing fence built from the same character.
_FENCE_RE = re.compile(r"^\s*(?P<fence>`{3,}|~{3,})")

# The frontmatter block, when present, must start on the first line of
# the document; everything after the closing fence is the body.
_FRONTMATTER_RE = re.compile(r"\A---\n(?P<data>.*?)\n---\n", re.DOTALL)

# A frontmatter block larger than this is treated as absent; no
# checklist needs 64 KiB of metadata, and composing one that size is
# an attack surface, not an authoring style.
_FRONTMATTER_LIMIT = 65536

# Control characters carry no information in a title or a name; a
# hostile document could otherwise steer the terminal through escape
# sequences echoed by the display.
_CONTROLS_RE = re.compile(r"[\x00-\x1f\x7f-\x9f]")

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

# The standardized names inside one copy directory. The sidecar
# records the actual filename, so the convention can change without
# stranding older copies.
_COPY_FILENAME = 'checklist.md'
_SIDECAR_FILENAME = 'copy.json'


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

    @property
    def progress(self) -> str:
        """The human progress summary, e.g. ``8/19 done, 1 blocked``."""
        counts = self.counts
        total = len(self.items)
        fragments = ['{}/{} done'.format(counts['done'], total)]
        if counts['blocked']:
            fragments.append('{} blocked'.format(counts['blocked']))
        if counts['failed']:
            fragments.append('{} failed'.format(counts['failed']))
        return ', '.join(fragments)


def parse_checklist(text: str) -> ParsedChecklist:
    """Parse checklist text into frontmatter, title and task items."""
    frontmatter, body = _split_frontmatter(text)
    return ParsedChecklist(
        title=_find_title(frontmatter, body),
        frontmatter=frontmatter,
        items=_parse_items(body),
    )


def _split_frontmatter(text: str) -> tuple[dict, str]:
    """Split YAML frontmatter off the document body.

    A broken frontmatter block -- malformed YAML, nesting too deep to
    compose, an implausibly large block -- degrades to no front
    matter: the title falls back to the first heading and the body
    parses as usual.
    """
    match = _FRONTMATTER_RE.match(text)
    if match is None:
        return {}, text
    data = match.group("data")
    if len(data) > _FRONTMATTER_LIMIT:
        return {}, text
    try:
        parsed = yaml.safe_load(data)
    except (yaml.YAMLError, RecursionError):
        return {}, text
    return (parsed if isinstance(parsed, dict) else {}), text[match.end():]


def _find_title(frontmatter: dict, body: str) -> str | None:
    """The frontmatter title, else the first ``#`` heading, else None."""
    title = frontmatter.get("title")
    if title:
        return _without_controls(str(title))
    match = _HEADING_RE.search(body)
    if match is None:
        return None
    return _without_controls(match.group("title").strip())


def _without_controls(text: str) -> str:
    """The text without control characters."""
    return _CONTROLS_RE.sub("", text)


def _parse_items(body: str) -> list[ChecklistItem]:
    """Collect task items, deriving nesting depth from indentation.

    Only task items enter the nesting stack; plain bullets and
    commentary do not affect the depth of later items.
    """
    items = []
    parents: list[int] = []
    fence = None
    for line in body.splitlines():
        fence_match = _FENCE_RE.match(line)
        if fence is not None:
            if fence_match is not None and \
                    fence_match.group("fence")[0] == fence[0]:
                fence = None
            continue
        if fence_match is not None:
            fence = fence_match.group("fence")
            continue
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
    """The active state of a copy id: the working copy present."""
    return (copy_dir / _COPY_FILENAME).is_file()


_INVENTORY_PATTERN_RE = re.compile(
    r'^(?P<prefix>[^\[\]]*)\[(?P<pattern>[^\[\]]+)\](?P<suffix>[^\[\]]*)$')
_PATTERN_INVALID_RE = re.compile(r'[;&|`\n\r]')


def find_stale_copies(copies: list['OpenCopy'], layers, filters=()):
    """The open copies whose source changed since they were opened.

    The stale check compares the source's current content hash with
    the hash recorded at open time: a mismatch means the checklist
    was updated after this copy started, and the copy is showing
    yesterday's procedure. Copies without a recorded hash -- opened
    before the field existed -- and copies whose checklist no
    longer resolves are never stale: there is nothing to compare
    against.
    """
    stale = []
    for copy in copies:
        if not copy.source_sha256:
            continue
        try:
            path, _origin = find_checklist(
                copy.checklist, layers, filters=filters)
        except ChecklistError:
            continue
        current = hashlib.sha256(path.read_bytes()).hexdigest()
        if current != copy.source_sha256:
            stale.append(copy)
    return stale


def parse_copy_pattern(copy_id: str) -> tuple[str, str, str] | None:
    """The inventory pattern of a copy id, when it carries one.

    A ``[pattern]`` segment in the copy id expands to one copy per
    matching host: for the id ``subdir/[webservers]/check``, the
    pattern is ``webservers`` and every matching host replaces the
    segment. The id supports one pattern segment, and the pattern
    must be a plausible ansible pattern. An id without brackets
    comes back as no pattern; a bracket id that does not parse is
    an error.
    """
    if '[' not in copy_id and ']' not in copy_id:
        return None
    if copy_id.count('[') != 1 or copy_id.count(']') != 1:
        raise ChecklistError(
            'The copy id supports only one inventory pattern: '
            '{}'.format(copy_id))
    match = _INVENTORY_PATTERN_RE.match(copy_id)
    if match is None:
        raise ChecklistError(
            'The copy id carries brackets that do not form an '
            'inventory pattern: {}'.format(copy_id))
    pattern = match.group('pattern')
    if _PATTERN_INVALID_RE.search(pattern):
        raise ChecklistError(
            'The inventory pattern [{}] contains characters that '
            'are not valid in an ansible pattern'.format(pattern))
    return match.group('prefix'), pattern, match.group('suffix')


def expand_copy_ids(copy_id: str, hosts: list[str]) -> list[str]:
    """One copy id per host, the pattern segment replaced.

    Every generated id passes the name validation, so a malformed
    host name cannot leave the batch half-open.
    """
    parsed = parse_copy_pattern(copy_id)
    if parsed is None:
        return [copy_id]
    prefix, pattern, suffix = parsed
    expanded = [prefix + host + suffix for host in hosts]
    for expanded_id in expanded:
        validate_name(expanded_id)
    return expanded


def require_task_items(parsed: ParsedChecklist, name: str) -> None:
    """Refuse a checklist that parsed to zero task items.

    The data-loss guard: a document that lost its markers would
    otherwise close as ``0/0 done`` and destroy the copy.
    """
    if not parsed.items:
        raise ChecklistError(
            'The checklist {} does not contain any task items'.format(
                name))


def resolve_single(copy: str | None, state_dir: Path) -> 'OpenCopy':
    """The copy argument, defaulting to the only open copy.

    An omitted operand resolves when exactly one copy is open; none
    or several are errors -- with a fleet open, the command needs to
    be told which copy it targets.
    """
    if copy is not None:
        return resolve_copy(copy, state_dir)
    copies = find_open_copies(state_dir)
    if not copies:
        raise ChecklistNotOpenError('No open copies')
    if len(copies) > 1:
        ids = ', '.join(sorted(item.copy_id for item in copies))
        raise ChecklistAmbiguousError(
            'Several open copies: {}; name one'.format(ids))
    return copies[0]


def resolve_heal(name: str, state_dir: Path, layers, filters=(),
                 reset: bool = False, dry_run: bool = False):
    """Resolve a lone open copy id to its recorded checklist.

    The copy records its checklist in the sidecar; the discovery
    re-resolves it fresh, so the healed copy picks up the latest
    source and its current origin. Without *reset* the match is an
    error spelling the reset command; a recorded checklist that no
    longer resolves in any layer is never healable -- the copy is
    close and edit territory then. A dry run skips the reset
    refusal: the preview shows what the heal would do.
    """
    copies = find_open_copies(state_dir)
    match = next((copy for copy in copies if copy.copy_id == name),
                 None)
    if match is None:
        raise ChecklistNotFoundError(f"Checklist not found: {name}")
    if not match.checklist:
        raise ChecklistNotFoundError(
            'Checklist not found: {}\n'
            'An open copy {} does not record its checklist\n'
            'Re-open it from the checklist name'.format(name, name))
    try:
        path, origin = find_checklist(match.checklist, layers,
                                      filters=filters)
    except ChecklistNotFoundError:
        raise ChecklistNotFoundError(
            'Checklist not found: {}\n'
            'An open copy {} of {} exists\n'
            'The recorded checklist no longer resolves in any layer; '
            'close or edit the copy instead'.format(
                name, name, match.checklist)) from None
    if not reset and not dry_run:
        raise ChecklistNotFoundError(
            'Checklist not found: {}\n'
            'An open copy {} of {} exists\n'
            'To reset: debops checklist open {} --reset'.format(
                name, name, match.checklist, match.copy_id))
    return match.copy_id, match.checklist, path, origin


def check_occupancy(state_dir: Path, copy_ids: list[str],
                    checklist: str, reset: bool = False,
                    expanded: bool = False) -> None:
    """Refuse a multi-copy batch when one of its ids is occupied.

    All-or-nothing: the batch either opens completely or not at
    all. A single occupied copy keeps the single-copy refusal of
    :command:`open_copy`; with *reset* the occupied copies are
    discarded and re-opened as requested. Expanded ids are
    manufactured from the inventory rather than typed: when one of
    them holds a different checklist, the collision is refused
    instead of discarding another checklist's copy.
    """
    open_copies = {copy.copy_id: copy for copy in
                   find_open_copies(state_dir)}
    occupied = [copy_id for copy_id in copy_ids
                if copy_id in open_copies]
    if not occupied:
        return
    if not reset:
        if len(copy_ids) >= 2:
            raise ChecklistAlreadyOpenError(
                'Already open: {}'.format(', '.join(occupied)))
        return
    if expanded:
        foreign = [copy_id for copy_id in occupied
                   if open_copies[copy_id].checklist !=
                   strip_md(checklist)]
        if foreign:
            raise ChecklistError(
                'The copies {} already hold other checklists; close '
                'them before opening {}'.format(
                    ', '.join(foreign), checklist))


def open_copy(
    checklist_path: Path,
    checklist: str,
    origin: str,
    copy_id: str,
    state_dir: Path,
    *,
    reset: bool = False,
) -> Path:
    """Copy a checklist into the state directory as an open copy.

    Returns the path of the opened checklist file. A copy id holds
    exactly one checklist: opening an occupied id refuses unless
    *reset* discards the current state first. The reset removes only
    the files the copy owns -- nested copy ids survive.
    """
    _validate_name(copy_id)
    copy_dir = Path(state_dir) / copy_id
    if _has_open_files(copy_dir):
        if not reset:
            raise ChecklistAlreadyOpenError(
                f"Copy id already open: {copy_id}")
        _discard_copy(copy_dir, state_dir)
    destination = copy_dir / _COPY_FILENAME
    _ensure_private_dir(copy_dir)
    shutil.copyfile(checklist_path, destination)
    (copy_dir / _SIDECAR_FILENAME).write_text(json.dumps({
        'opened': datetime.now().astimezone().isoformat(
            timespec='seconds'),
        'checklist': strip_md(checklist),
        'origin': origin,
        'filename': _COPY_FILENAME,
        'source_sha256': hashlib.sha256(
            checklist_path.read_bytes()).hexdigest(),
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
    source_sha256: str | None

    @property
    def implicit(self) -> bool:
        """True when the copy id is the checklist's implicit copy."""
        return self.copy_id == strip_md(self.checklist)


def find_open_copies(state_dir: Path) -> list[OpenCopy]:
    """Scan the state directory for open copies, ordered by id.

    The scan looks for the two standardized files -- the working copy
    and its sidecar -- and each match's parent directory is exactly
    its copy directory: the copy id is that directory's path relative
    to the state root, slashes intact, however deep the id nests.
    """
    state_dir = Path(state_dir)
    if not state_dir.is_dir():
        return []
    candidates: dict[Path, None] = {}
    for pattern in (_COPY_FILENAME, _SIDECAR_FILENAME):
        for path in sorted(state_dir.rglob(pattern)):
            candidates[path.parent] = None
    copies = []
    for copy_dir in sorted(candidates):
        copy_id = copy_dir.relative_to(state_dir).as_posix()
        md, data = _copy_files(copy_dir)
        if md is None:
            # A directory without a working copy is not an open copy
            continue
        copies.append(
            _open_copy_record(state_dir, copy_id, copy_dir, md, data))
    return copies


def _copy_files(copy_dir: Path) -> tuple[Path | None, dict | None]:
    """The working copy file and sidecar data of one copy directory.

    The filename comes from the sidecar when it can be read and is a
    plain relative name; the standardized name is the fallback. A
    directory whose working copy is missing has no active state.
    """
    try:
        loaded = json.loads((copy_dir / _SIDECAR_FILENAME).read_text())
    except (OSError, json.JSONDecodeError):
        loaded = None
    data = loaded if isinstance(loaded, dict) else None
    filename = _copy_filename(data or {})
    md = copy_dir / filename
    if not md.is_file():
        return None, data
    return md, data


def _copy_filename(data: dict) -> str:
    """The working file name from the sidecar, when it is safe.

    The sidecar is a user-editable file; a filename that is not a
    single plain name would point the working copy outside of its
    directory, so anything else falls back to the standardized name.
    """
    filename = data.get('filename', _COPY_FILENAME)
    if (isinstance(filename, str) and filename not in ('.', '..')
            and PurePosixPath(filename).parts == (filename,)):
        return filename
    return _COPY_FILENAME


def _open_copy_record(
    state_dir: Path,
    copy_id: str,
    copy_dir: Path,
    md: Path,
    data: dict | None,
) -> OpenCopy:
    """Assemble an open-copy record, falling back to the mtime.

    A missing or corrupt sidecar costs the recorded metadata: the
    checklist name is unknown and the open date comes from the
    file's mtime. Sidecar fields that are present but hostile -- not
    a string, or a checklist name that would escape its roots --
    degrade the same way. The copy id stays resolvable from the
    directory path, and ``open <id> <checklist> --reset`` heals the
    copy.
    """
    if data:
        checklist = _sidecar_checklist(data)
        origin = _sidecar_origin(data)
        opened = data.get('opened')
    else:
        checklist, origin, opened = '', '', None
    source_sha256 = data.get('source_sha256') if data else None
    if not isinstance(source_sha256, str) or not re.fullmatch(
            r'[0-9a-f]{64}', source_sha256):
        source_sha256 = None
    if opened is not None:
        try:
            opened = datetime.fromisoformat(opened)
        except (TypeError, ValueError):
            opened = None
    if opened is None:
        opened = datetime.fromtimestamp(md.stat().st_mtime).astimezone()
    return OpenCopy(
        copy_id=copy_id, path=md, state_dir=state_dir,
        checklist=checklist, origin=origin, opened=opened,
        source_sha256=source_sha256)


def _sidecar_checklist(data: dict) -> str:
    """The checklist name from the sidecar, when it is one.

    The name becomes a path component of the vault record; anything
    that would not validate as a checklist name leaves the copy with
    an unknown checklist instead.
    """
    checklist = data.get('checklist', '')
    if isinstance(checklist, str) and checklist:
        try:
            _validate_name(checklist)
        except ChecklistError:
            return ''
        return checklist
    return ''


def _sidecar_origin(data: dict) -> str:
    """The origin label from the sidecar, when it is printable."""
    origin = data.get('origin', '')
    if isinstance(origin, str):
        return _without_controls(origin)
    return ''


def resolve_copy(target: str, state_dir: Path) -> OpenCopy:
    """Resolve an edit/commit/close target to its open-copy record.

    An exact copy id wins; otherwise the target is matched against
    the checklist path of the open copies. One match resolves,
    several are ambiguous, none means the target is not open.
    """
    copies = find_open_copies(state_dir)
    for copy in copies:
        if copy.copy_id == target:
            return copy
    name = strip_md(target)
    matches = [copy for copy in copies if copy.checklist == name]
    if not matches:
        raise ChecklistNotOpenError(f"Checklist copy not open: {target}")
    if len(matches) > 1:
        ids = ', '.join(sorted(copy.copy_id for copy in matches))
        raise ChecklistAmbiguousError(f"Several open copies of {name}: {ids}")
    return matches[0]


def close_copy(state_dir: Path, copy_id: str) -> None:
    """Discard an open copy, pruning the state directory if empty.

    The copy id shares the checklist name rule: a second client --
    an MCP tool, a TUI -- must not be able to point the discard at a
    path outside of the state directory.
    """
    _validate_name(copy_id)
    _discard_copy(Path(state_dir) / copy_id, Path(state_dir))


def _discard_copy(copy_dir: Path, state_dir: Path) -> None:
    """Remove the copy's files and prune empty directories.

    Only the two files the copy owns are removed -- nested copy ids
    live inside the same tree and must survive a close. Empty
    directories are pruned upward, the state directory included.
    """
    for filename in (_COPY_FILENAME, _SIDECAR_FILENAME):
        (copy_dir / filename).unlink(missing_ok=True)
    current = copy_dir
    while current != state_dir.parent:
        try:
            current.rmdir()
        except OSError:
            break
        if current == state_dir:
            break
        current = current.parent


# The reserved vault segment nesting the named copies. Implicit
# copies record beside the checklist instead. The segment is refused
# in checklist names and copy ids, so the two namespaces cannot
# collide: a named copy of checklist ``a`` can never occupy the
# record path of an implicit copy of a checklist named ``a/_copies``.
_COPIES_SEGMENT = '_copies'


def vault_record_path(
    vault_dir: str | Path,
    checklist: str,
    copy_id: str,
    opened: datetime,
) -> Path:
    """The vault record path for one committed copy.

    *vault_dir* is the checklist base directory -- the resolved
    `checklist.commit_path`. Records group by checklist; named
    copies nest under the reserved ``_copies`` segment. The
    filename is the open date, stable for the copy's whole life.
    """
    record = Path(vault_dir) / strip_md(checklist)
    if copy_id != strip_md(checklist):
        record = record / _COPIES_SEGMENT / copy_id
    return record / f"{opened.date().isoformat()}.md"


def list_checklists(
    layers: list[tuple[Path, str]],
    filters=(),
) -> list[tuple[str, Path, str]]:
    """The effective checklist entries across the discovery layers.

    One entry per checklist name: the first layer that provides it
    wins, so a project checklist shadows its user and packaged
    counterparts. The entries sort by name. Checklist files in the
    shared layers that resolve outside of their root through a
    symbolic link are omitted.

    The *filters* are the ordered ``checklist.filters`` rules
    shared with ``find_checklist``.
    """
    rules = _filter_rules(list(filters))
    entries = {}
    for root, origin in layers:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob('*.md')):
            if origin != 'user' and not _inside_layer(path, root):
                continue
            name = strip_md(path.relative_to(root).as_posix())
            entries.setdefault(name, (name, path, origin))
    return [entries[name] for name in sorted(entries)
            if _visible(name, rules)]


def _filter_rules(filters: list) -> list[tuple[re.Pattern, bool]]:
    """The compiled show/hide rules of the ordered filter list.

    A bare pattern keeps matching names visible, a ``!``-prefixed
    pattern hides them. The patterns are globs over the checklist
    name -- relative to the layer root, ``.md`` stripped.
    Patterns with many ambiguous wildcard runs backtrack
    catastrophically, so an over-complex pattern is refused instead
    of compiling into a hang.
    """
    rules = []
    for pattern in filters:
        hide = pattern.startswith('!')
        body = pattern[1:] if hide else pattern
        rules.append((
            _compile_checked(body, 'checklist.filters'),
            not hide))
    return rules


def _compile_checked(pattern: str, source: str) -> re.Pattern:
    """One compiled path glob, with the complexity guard.

    Patterns with many ambiguous wildcard runs backtrack
    catastrophically, so an over-complex pattern is refused instead
    of compiling into a hang. The *source* names the feature the
    pattern came from, for the error messages.
    """
    if len(pattern) > 128 or len(re.findall(r'\*+', pattern)) > 6:
        raise ChecklistError(
            f"The {source} pattern {pattern!r} is too complex; at "
            "most 128 characters and 6 wildcard runs are supported")
    try:
        return _compile_glob(pattern)
    except re.error:
        raise ChecklistError(
            f"Invalid {source} pattern: {pattern!r}") from None


def _compile_glob(pattern: str) -> re.Pattern:
    """Compile one glob to a regular expression.

    The match target is a checklist name or a copy id. A run of
    ``*`` stars crosses the slash and matches any stretch of the
    name, ``?`` matches any single character, and the ``[...]``
    classes keep their shell meaning -- the language of shell globs,
    matched against the whole name.
    """
    parts = []
    index = 0
    while index < len(pattern):
        char = pattern[index]
        if char == '*':
            parts.append('.*')
            while index < len(pattern) and pattern[index] == '*':
                index += 1
        elif char == '?':
            parts.append('.')
            index += 1
        elif char == '[':
            end = pattern.find(']', index + 1)
            if end == -1:
                parts.append(re.escape(char))
                index += 1
            else:
                body = pattern[index + 1:end]
                if not body:
                    parts.append(re.escape('[]'))
                elif body.startswith('!'):
                    parts.append('[^' + body[1:] + ']')
                else:
                    parts.append('[' + body + ']')
                index = end + 1
        else:
            parts.append(re.escape(char))
            index += 1
    return re.compile(''.join(parts) + r'\Z')


def _visible(name: str, rules: list[tuple[re.Pattern, bool]]) -> bool:
    """Whether the name passes the ordered rules; the last match wins."""
    visible = True
    for regex, show in rules:
        if regex.match(name):
            visible = show
    return visible


def compile_selection(globs: list) -> list[re.Pattern]:
    """The compiled selection globs of the ``checklist list`` command.

    A glob selects the checklist names that match it; a name matching
    any glob is listed. The globs use the same language as
    the ``checklist.filters`` rules: a run of ``*`` crosses the
    slash, ``?`` matches any character, and the match is anchored to
    the whole name. The ``!`` prefix of the hide rules is not part of
    the selection language and is refused, so a stray ``!`` cannot
    silently list nothing.
    """
    patterns = []
    for glob in globs:
        if glob.startswith('!'):
            raise ChecklistError(
                f"Invalid selection glob {glob!r}: the '!' prefix "
                "belongs to the checklist.filters rules")
        patterns.append(_compile_checked(glob, 'selection'))
    return patterns


def name_selected(name: str, patterns: list[re.Pattern]) -> bool:
    """Whether the checklist name matches any of the selection globs.

    An empty selection lists everything.
    """
    return not patterns or any(
        pattern.match(name) for pattern in patterns)


def copy_selected(checklist: str, copy_id: str,
                  patterns: list[re.Pattern]) -> bool:
    """Whether a copy passes the selection globs.

    A copy is listed when its checklist name matches a glob, or its
    copy id does. The id matches in three spellings: as stored,
    relative to the checklist name, and qualified with it -- the
    copies of the checklist ``flow`` are reachable as ``alpha*`` as
    well as ``flow/alpha*``, whichever way they were named.
    """
    if name_selected(checklist, patterns):
        return True
    candidates = [copy_id]
    prefix = checklist + '/'
    if copy_id.startswith(prefix):
        candidates.append(copy_id[len(prefix):])
    else:
        candidates.append(prefix + copy_id)
    return any(name_selected(candidate, patterns)
               for candidate in candidates)


def editor_argv(environ=None) -> list[str]:
    """The editor command line for interactive editing.

    ``$VISUAL`` wins over ``$EDITOR``; without either, the Debian
    ``sensible-editor`` indirection runs, and ``vi`` is the last
    resort. The values may carry arguments and are split the way a
    shell would split them; a value that does not split -- an
    unclosed quote, for example -- raises ChecklistError instead of
    crashing the command, and a value that splits to nothing counts
    as unset.
    """
    environ = os.environ if environ is None else environ
    for variable in ('VISUAL', 'EDITOR'):
        value = environ.get(variable)
        if value:
            try:
                argv = shlex.split(value)
            except ValueError as errmsg:
                raise ChecklistError(
                    "The {} value does not split into a command: "
                    "{}".format(variable, errmsg)) from None
            if argv:
                return argv
    for editor in ('sensible-editor', 'vi'):
        if shutil.which(editor):
            return [editor]
    return ['vi']


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
    filters=(),
) -> tuple[Path, str]:
    """Resolve a checklist name against the discovery layers.

    Layers are ``(root, origin)`` pairs; the first existing file wins
    and its origin is returned alongside the path. A name may be given
    with or without the ``.md`` suffix -- both spellings resolve
    identically regardless of how the file is stored.

    The *filters* are the ordered ``checklist.filters`` rules shared
    with ``list_checklists``; a hidden name is refused before the
    layer walk. In the shared layers, a checklist file that resolves
    outside of its layer root through a symbolic link is refused.
    """
    _validate_name(name)
    if not _visible(name, _filter_rules(list(filters))):
        raise ChecklistFilteredError(
            f"The checklist {name} is hidden by checklist.filters")
    candidates = [name]
    stripped = strip_md(name)
    if stripped != name:
        candidates.append(stripped)
    else:
        candidates.append(name + '.md')
    for root, origin in layers:
        for candidate in candidates:
            path = root / candidate
            if not path.is_file():
                continue
            if origin != 'user' and not _inside_layer(path, root):
                raise ChecklistError(
                    f"The checklist {name} resolves outside of its "
                    f"discovery layer: {path}")
            return path, origin
    raise ChecklistNotFoundError(f"Checklist not found: {name}")


def _inside_layer(path: Path, root: Path) -> bool:
    """Whether the path resolves inside its layer root.

    The comparison uses real paths, so symbolic links cannot carry a
    checklist that lives outside of the layer.
    """
    return os.path.realpath(path).startswith(
        os.path.realpath(root) + os.sep)


def strip_md(name: str) -> str:
    """The checklist name without its ``.md`` suffix, if present."""
    return name[:-3] if name.endswith('.md') else name


def _validate_name(name: str) -> None:
    """Reject absolute names and names escaping their root.

    The check runs on the name itself, before any join. Absolute
    names, ``..`` parts, control characters and the reserved
    ``_copies`` vault segment are refused; checklist names and copy
    ids share the rule.
    """
    parts = PurePosixPath(name).parts
    if (not name or not parts or PurePosixPath(name).is_absolute()
            or '..' in parts
            or _COPIES_SEGMENT in parts or _CONTROLS_RE.search(name)):
        raise ChecklistError(f"Invalid checklist name: {name!r}")


def validate_name(name: str) -> None:
    """The public face of the checklist name and copy id rule.

    The copy id expansion validates every generated id before the
    first copy opens, so a hostile or malformed inventory host name
    cannot leave the batch half-open.
    """
    _validate_name(name)
