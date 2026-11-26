.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The :command:`debops checklist` section manages operational checklists:
plain Markdown files that carry a five-state marker syntax. The
section opens a checklist as a working copy in the system state
directory. The copy holds the sysadmin's ticks and annotations. The
:command:`debops checklist commit` command writes the copy into the
project vault, by default the :file:`vault/checklists/` directory,
committed to the project git repository. Each commit leaves one
dated record. The record is the audit trail. A year from now it
answers what you checked and what you found.

The markers describe the state of each task item: ``[ ]`` open,
``[x]`` done, ``[B]`` blocked, ``[F]`` failed, ``[N]`` not applicable.
Each state accepts a second spelling, for example ``[~]`` for
blocked. Checklists come from three layers, in order of precedence:
the project's :file:`.debops/checklists/` directory, the user
directory :file:`~/.local/share/debops/checklists/`, and the packaged
set shipped with DebOps. The :command:`debops checklist list` command
shows the effective entries and the open copies.

The review workflow is meant to recur. Open a named copy once, run
the review, commit the record and close the copy, then re-open it
with ``--reset`` at the next cycle. See :ref:`checklists` for the
full guide to the format and the workflow.
