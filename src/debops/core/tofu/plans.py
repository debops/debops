# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The plan-file store of the OpenTofu views.

The plan files the wrapper saves live in the view's ``plans/``
directory -- tofu-native ciphertext beside the view configuration,
transient and untracked. The names carry the monotonic sequence id
of the view and the timestamp: the ids address the files while the
retention prunes the oldest ones, and this module owns the grammar,
the listing, the id resolution and the retention policy. The runner
saves and prunes through it; the 'debops tofu plans' operation
lists and resolves through it.
"""

import datetime
import os

PLAN_DIR = 'plans'
PLAN_FILE_PREFIX = 'debops-'


def parse_plan_seq(name):
    """Return the sequence id of a saved plan file name: the integer
    between the 'debops-' prefix and the stamp. None for the names
    which carry no sequence -- the plan files the operator saves
    with the '-out' option, and the pre-sequence DebOps ones."""
    if not name.startswith(PLAN_FILE_PREFIX) or \
            not name.endswith('.tfplan'):
        return None
    tail = name[len(PLAN_FILE_PREFIX):-len('.tfplan')]
    sequence, separator, _stamp = tail.partition('-')
    if not separator or not sequence.isdigit():
        return None
    return int(sequence)


def plan_file_names(view_root):
    """Return the plan file names of the view's plans directory,
    sorted by name."""
    plans_dir = os.path.join(view_root, PLAN_DIR)
    try:
        names = os.listdir(plans_dir)
    except OSError:
        return []
    return sorted(name for name in names if name.endswith('.tfplan'))


def plans_dir(view_root):
    """Return the plans directory of the view."""
    return os.path.join(view_root, PLAN_DIR)


def save_path(view_root):
    """Return the view-relative path of the plan file the next plan
    saves: the sequence id one above the maximum of the live files,
    with the timestamp sorting the files of one id."""
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    return os.path.join(
        PLAN_DIR, '{}{}-{}.tfplan'.format(
            PLAN_FILE_PREFIX, max_plan_seq(view_root) + 1, timestamp))


def prune(view_root, retention):
    """Remove the expired plan files DebOps saved in the view and
    return their view-relative paths.

    The plan files DebOps saves carry the 'debops-' prefix; the
    retention keeps the newest 'retention' of them and removes the
    older ones, sorted by the sequence id -- the lexicographic order
    of the sequence-prefixed names would break at ten. The
    pre-sequence DebOps plan files sort before every sequenced one,
    they are the older generation. The plan files the operator
    saves with the '-out' option are never touched."""
    saved = sorted(
        (name for name in plan_file_names(view_root)
         if name.startswith(PLAN_FILE_PREFIX)),
        key=lambda name: (parse_plan_seq(name) or 0, name))
    removed = []
    for name in saved[:-retention]:
        os.remove(os.path.join(view_root, PLAN_DIR, name))
        removed.append(os.path.join(PLAN_DIR, name))
    return removed


def max_plan_seq(view_root):
    """Return the highest sequence id among the saved plan files.

    The next plan saves with the id one above the maximum, and the
    retention pruning never collides: the maximum keeps rising as
    the oldest files are pruned. A wiped plans directory resets the
    counter to one -- the ids are unique among the live set, and the
    listing documents that contract."""
    sequences = [parse_plan_seq(name)
                 for name in plan_file_names(view_root)]
    return max((sequence for sequence in sequences
                if sequence is not None), default=0)


def plan_rows(view_root):
    """Return the listing rows of the saved plans: the sequence id,
    the file name, the size and the modification time of each
    DebOps-saved plan, sorted by the sequence. The plan files the
    operator saved with the '-out' option carry no sequence and are
    not the listing's business."""
    rows = []
    for name in plan_file_names(view_root):
        sequence = parse_plan_seq(name)
        if sequence is None:
            continue
        path = os.path.join(view_root, PLAN_DIR, name)
        rows.append((sequence, name, os.path.getsize(path),
                     os.path.getmtime(path)))
    return sorted(rows)


def resolve_plan_file(view_root, plan_id):
    """Return the view-relative path of the plan file one id names.

    An integer id resolves against the parsed sequences -- the ids
    are unique among the live files by construction, a collision
    refuses with the names listed. Any other id resolves by the
    unique prefix of the file names: the operator's own '-out'
    plans and the pre-sequence DebOps ones carry stamp-only names.
    An unknown or ambiguous id refuses with the names the view
    holds."""
    names = plan_file_names(view_root)
    if plan_id.isdigit():
        sequence = int(plan_id)
        matches = [name for name in names
                   if parse_plan_seq(name) == sequence]
        if len(matches) > 1:
            raise ValueError(
                'The sequence id {} of the saved plans is not '
                'unique: {}.'.format(sequence, ', '.join(matches)))
    else:
        matches = [name for name in names
                   if name.startswith(plan_id)]
        if len(matches) > 1:
            raise ValueError(
                'The prefix {!r} of the saved plans is ambiguous: '
                '{}.'.format(plan_id, ', '.join(matches)))
    if not matches:
        raise ValueError(
            'No saved plan of the view matches the id {!r}: the '
            'saved plans are {}.'.format(
                plan_id, ', '.join(names) or '(none)'))
    return os.path.join(PLAN_DIR, matches[0])
