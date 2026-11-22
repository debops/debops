# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The change records the reconciles propose.

The generated-file reconcile of the registry and the inventory
renderer answer the same question -- what did the reconcile
propose, with what diff, at what label -- and share one record
shape: the path, the action, the unified diff, and the security
flag of the sensitive files. The '--diff' option of the operations
prints these records; the dry runs report them. The apply logic
stays with each reconcile -- the marker check of the generated
files and the containment of the inventory writes are genuinely
different -- only the contract and the helpers are shared here.
"""

import difflib
import os


def change_label(path, project_root):
    """The path form the change records print and label: relative to
    the project directory when the path is inside it, absolute
    otherwise."""
    path = os.path.normpath(path)
    project_root = os.path.normpath(project_root)
    if path.startswith(project_root + os.sep):
        return os.path.relpath(path, project_root)
    return path


def unified_diff(old_content, new_content, label):
    """Return the unified diff between two file contents, labeled
    with the change label of the path."""
    return ''.join(difflib.unified_diff(
        (old_content or '').splitlines(keepends=True),
        (new_content or '').splitlines(keepends=True),
        fromfile='a/' + label, tofile='b/' + label))


def file_change(path, action, old_content, new_content, project_root,
                secret=False):
    """The change record one reconcile step proposes.

    The diff rides the record for the '--diff' option; the sensitive
    files record none, their values must not reach the terminal --
    the action line names the file instead."""
    label = change_label(path, project_root)
    return {
        'path': path,
        'action': action,
        'diff': None if secret else unified_diff(old_content,
                                                 new_content, label),
        'secret': secret,
    }
