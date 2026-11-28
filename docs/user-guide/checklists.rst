.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _checklists:

Operational checklists
======================

Operational checklists are plain Markdown files that track work you
do by hand: release upgrades, host reboots, security reviews. DebOps
opens a checklist as a working copy. A commit records the finished
work as a dated file in the project vault. Git keeps the history in
the project repository. This page explains the format, the lifecycle
of a copy, and the configuration options.

.. contents::
   :local:
   :depth: 2

How the pieces fit together
---------------------------

The :command:`debops checklist` section follows one path from source
to record:

.. code-block:: text

   checklist source file ──open──▶ working copy ──commit──▶ vault record

The *source* is a Markdown file in one of three discovery layers. The
*working copy* lives in the system state directory
(:file:`~/.local/state/`, per the XDG base directory specification__)
and holds
your ticks and annotations. Each project's copies live in their own
directory under :file:`~/.local/state/debops/`, named ``checklists-``
plus the namespace key of the project path. The state directory is
per user: two administrators working on one controller keep separate
copies, and the committed records are where their work meets. The
*record* is a dated copy of the checklist in the project's
``vault/`` directory, committed to the project git repository.

.. __: https://specifications.freedesktop.org/basedir/latest/

A checklist documents work done elsewhere. The release notes drive
the upgrade. The checklist tracks where you are in it. Two genres
exist, and the packaged set ships one of each:

- *Procedure* checklists, like
  ``debian/dist-upgrade/bookworm-to-trixie``, walk a one-time
  operation item by item. You tick as you go and commit checkpoints.
- *Review* checklists, like
  ``example/audit/periodic-security-review``, verify work that the
  configuration management already did. Deviations are findings to
  record, not steps to fix mid-review.

A finding is not a failure of the review. A review that finds
something did its job. Mark the deviation ``[F]``, annotate it with
what happened and where the follow-up lives, and let the next cycle
verify the fix.

The checklist format
--------------------

A checklist is a Markdown file. An optional YAML front matter block
carries a title and links:

.. code-block:: markdown

   ---
   title: "Periodic security review"
   description: "Recurring do-confirm security review of a Debian host."
   documentation:
     - https://www.debian.org/security/
   ---

   # Periodic security review

The first ``# heading`` is the fallback title. Open and commit
preserve the front matter verbatim. Unknown keys survive too. Broken
front matter degrades to no front matter instead of breaking the
commands.

Task items are list lines whose brackets carry a one-character state
marker:

.. list-table::
   :widths: 20 30 50
   :header-rows: 1

   * - State
     - Markers
     - Meaning
   * - open
     - ``[ ]``
     - not done
   * - done
     - ``[x]``, ``[X]``
     - resolved
   * - blocked
     - ``[B]``, ``[~]``
     - open, waiting on something
   * - failed
     - ``[F]``, ``[!]``
     - resolved, unsuccessfully
   * - N/A
     - ``[N]``, ``[-]``
     - resolved

Either spelling parses. Unknown bracket content reads as open, which
keeps the format forward-compatible. Longer bracket content is
commentary, not a state. The parser accepts dash,
asterisk and plus bullets and ordered items, the GitHub task-list
syntax, so pasted content parses as it renders. Fenced code blocks
never carry items. The open and commit commands refuse a file that
parses to zero task items. A pasted document that lost its markers
then fails loudly instead of recording ``0/0 done``.

Two conventions keep a shared checklist readable:

- Keep a copy of the state table in the preamble, both spellings
  included, so a reader never has to guess what ``[B]`` means.
- End the file with a pointer to the source: "Found a gap or an
  error? Fix the source it was opened from, not this copy." The tool
  discards and re-opens copies. The source is the durable artifact.

The discovery layers
--------------------

Checklists resolve against three layers, in order of precedence. The
first match wins, so a project checklist shadows its packaged
namesake:

#. :file:`.debops/checklists/` in the project directory
#. :file:`~/.local/share/debops/checklists/` in the user directory
#. the packaged set inside the DebOps package

The :command:`debops checklist list` command shows the effective
entries. At ``-v`` the titles appear, at ``-vv`` the origin in
brackets, so you can see which layer provided each checklist:

.. code-block:: console

   alice@controller:~$ debops checklist list -vv
   debian/dist-upgrade/bookworm-to-trixie │ Debian 12 (bookworm) to 13 (trixie) release upgrade [packaged]
   example/audit/cluster-security-review │ Cluster security review [packaged]
   example/audit/periodic-security-review │ Periodic security review [packaged]

The progress in parentheses, ``14/30 done``, appears when an implicit
copy of the checklist is open. A copy whose source changed after the
copy was opened is marked ``[stale]``: the listing compares the
source's content with the hash recorded at open time.
``--reset`` re-copies the latest source and clears the marker.

The listing takes selection globs: ``debops checklist list 'deb*'``
lists the matching names only, the open copies under ``--active``
included. A copy matches through its checklist name or its copy id,
in the stored, the relative or the qualified spelling, so ``*review*``
reaches a copy nested under a checklist. The globs use the syntax
of the ``checklist.filters`` patterns but act on the listing alone: a
name left out of the listing can still be opened.

Personal checklists do not need to live in the user directory. Make
a file symbolic link into the user layer and keep the target
wherever you keep your notes:

.. code-block:: console

   alice@controller:~$ mkdir -p ~/.local/share/debops/checklists/audit
   alice@controller:~$ ln -s ~/notes/audit/periodic-security-review.md \
       ~/.local/share/debops/checklists/audit/periodic-security-review.md

The packaged set ships three checklists, two of them under the
``example/`` namespace as demonstrations of the format. The
:ref:`filters <checklists__ref_filters>` configuration option hides a
whole namespace without editing the tree.

Working with copies
-------------------

The copy commands work inside a DebOps project directory: the vault
records and the git commits land in it. :command:`debops checklist
list` also works outside one. The project layer of the discovery is
simply omitted then.

:command:`debops checklist open` copies a checklist into the state
directory. Two forms exist. The one-argument form creates an
implicit copy whose id is the checklist name. The two-argument form
creates a named copy:

.. code-block:: console

   alice@controller:~$ debops checklist open example/audit/periodic-security-review
   Opened example/audit/periodic-security-review [packaged]

   alice@controller:~$ debops checklist open web example/audit/periodic-security-review
   Opened example/audit/periodic-security-review as copy web [packaged]

The origin in brackets names the layer that provided the checklist.
That matters when a project checklist shadows a packaged one: the
line tells you which variant you opened.

An id holds exactly one checklist. Re-opening an occupied id refuses
unless ``--reset`` discards the current state and re-copies the
checklist, possibly a different one, and refreshes the open
timestamp. Copy ids may carry slashes. Nested ids such as
``web1/alpha`` show as a tree and record under nested vault paths.
In the tree, a copy id that starts with the checklist name renders
relative to it. For the checklist ``flow``, the copy ``flow/alpha``
appears as ``alpha`` directly under the root. The strip is skipped
when another copy already occupies the stripped id, so two copies
never merge into one node.

A recurring review runs one cycle at a time. Open the copy once.
Commit it at the end of each cycle with ``--close``, and open it
again at the next cycle:

.. code-block:: console

   alice@controller:~$ debops checklist open review example/audit/periodic-security-review
   ... run the review, record findings and measured values ...
   alice@controller:~$ debops checklist commit review --close

The closed copy no longer occupies the id, so the next cycle starts
with a plain open:

.. code-block:: console

   alice@controller:~$ debops checklist open review example/audit/periodic-security-review

A lone copy id works too, with ``--reset``: the open copy records
its checklist in a sidecar, so ``debops checklist open review
--reset`` re-opens from the recorded name. The resolution runs fresh
through the current layers. A copy whose recorded checklist no
longer resolves anywhere has no heal. Close or edit it.

An id can carry an Ansible inventory pattern in square brackets. The
pattern expands to the matching hosts, one copy per host:

.. code-block:: console

   alice@controller:~$ debops checklist open 'subdir/[webservers]/check' example/audit/periodic-security-review
   Opened example/audit/periodic-security-review as copy subdir/web1/check [packaged]
   Opened example/audit/periodic-security-review as copy subdir/web2/check [packaged]

Quote the id: the shell reads unquoted brackets as a glob. The id
supports one pattern. The batch is all-or-nothing: an occupied id
refuses the whole batch and names the copies, and with ``--reset``
the occupied copies are discarded and re-opened. An occupied copy
that holds a different checklist refuses the batch even with
``--reset``; close it first. A pattern that
matches no hosts, or an :command:`ansible` run that fails, refuses
the batch before anything opens. The ``--dry-run`` option prints
what would be opened without opening anything, with already-open
copies marked:

.. code-block:: console

   alice@controller:~$ debops checklist open --dry-run 'subdir/[webservers]/check' example/audit/periodic-security-review
   Would open 2 of example/audit/periodic-security-review [packaged]:
     subdir/web1/check
     subdir/web2/check

The remaining commands -- :command:`debops checklist edit`,
:command:`debops checklist commit` and :command:`debops checklist
close` -- take a copy id or a checklist path. Their options and edge
cases are documented in the :ref:`command reference
<cmd_debops-checklist>`.

The vault
---------

:command:`debops checklist commit` writes each record under the
``checklist.commit_path`` directory of the project, by default
``vault/checklists``. Records group by checklist. The filename is
the copy's open date, so one directory holds a copy's entire run
history. The git log holds the progression:

.. code-block:: text

   vault/checklists/
   ├── debian/dist-upgrade/bookworm-to-trixie/
   │   └── 2026-11-10.md
   ├── example/audit/periodic-security-review/
   │   └── _copies/review/
   │       └── 2026-05-11.md
   └── system/host-reboot/
       └── 2026-07-14.md

The open date decides the filename, not the commit date: a checklist
opened at 23:50 and committed at 00:30 records under the day it
started. Implicit copies record beside the checklist. Named copies
nest under the reserved ``_copies`` segment. That name is refused in
checklist names and copy ids, so the two namespaces cannot collide.

The commit command writes each record with mode ``0600``. The vault
becomes part of the project git repository like any other content.
In a project directory without a git repository, the record is
written and a notice reports the skipped commit. The command runs
the git commit itself, with a generated message:

.. code-block:: text

   checklist: review example/audit/periodic-security-review (14/30 done, 2 blocked)

Every re-commit of an open copy overwrites its own record. The next
dated record starts when the copy is closed and re-opened. The
history lives in git. Find a past review there. The commit messages
carry the checklist name and the progress, so a search finds the
cycle you need:

.. code-block:: console

   alice@controller:~$ git log --oneline -- vault/checklists/example/audit/periodic-security-review
   4f1c2a3 checklist: review example/audit/periodic-security-review (30/30 done, 2 failed)
   alice@controller:~$ git show 4f1c2a3:vault/checklists/example/audit/periodic-security-review/_copies/review/2026-05-11.md

.. _checklists__ref_filters:

Configuration
-------------

Both options live in the ``[checklist]`` section of the DebOps
configuration. The shipped defaults come from
:file:`src/debops/_data/defaults.toml`. Set your own values in the
project or user configuration.

``checklist.commit_path``
  Type: string
  Purpose: The project-relative directory that holds the committed
  records. The directory must resolve inside the project directory.
  ``..`` escapes and symbolic links pointing outside are refused.
  The vault is a project artifact, committed with the project, and
  an outside location would lose the git versioning.
  Default: ``vault/checklists``
  Example:

  .. code-block:: toml

     [checklist]
     commit_path = "records/checklists"

``checklist.filters``
  Type: list of strings
  Purpose: Ordered glob rules over the checklist names, applied to
  the discovery. A bare pattern keeps matching names visible, a
  ``!``-prefixed pattern hides them, the last matching rule wins and
  a name no rule matches stays visible. Matching is anchored to the
  whole name: a run of ``*`` crosses the slash, ``?`` matches any
  single character. The state
  commands do not consult the filters: a copy of a now-hidden
  checklist still commits, still shows in ``--active`` and can be
  closed. A hidden checklist cannot be opened either, by name or
  through a sidecar re-open.
  Default: ``[]``
  Example:

  .. code-block:: toml

     [checklist]
     filters = ["!example/**"]

  Hide everything, then make an exception, to get an allowlist:

  .. code-block:: toml

     [checklist]
     filters = ["!**", "system/**"]

See also
--------

- :ref:`cmd_debops-checklist` for the command reference
- :ref:`debops_configuration` for the DebOps configuration system
- the packaged checklists in
  :file:`src/debops/_data/checklists/` as worked examples
