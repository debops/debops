.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

The checklist format
--------------------

A checklist is a Markdown file. It can carry a YAML front matter
block with a ``title`` and a ``description``. The first ``# heading``
is the fallback title. Task items are list lines whose brackets carry
a one-character state marker:

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

Either marker spelling parses. Unknown bracket content reads as
open. Dash, asterisk and plus bullets and ordered items all parse.
Fenced code blocks never carry items. The open and commit commands
refuse a checklist that parses to zero task items.

The discovery layers
--------------------

Checklists resolve against three layers, in order of precedence. The
first match wins, so a project checklist shadows its packaged
counterpart of the same name:

- :file:`.debops/checklists/` in the project directory
- :file:`~/.local/share/debops/checklists/` for personal checklists
- the packaged set inside the DebOps package

Personal checklists can live outside the user directory. Make a file
symbolic link into the user layer. The link target is your file, and
the checklist resolves and lists through it.

The packaged set currently ships:

- ``debian/dist-upgrade/bookworm-to-trixie``
- ``example/audit/periodic-security-review``
- ``example/audit/cluster-security-review``

The ``example/`` namespace holds demonstration content. The
``checklist.filters`` configuration option hides a whole namespace
without editing the tree. See :ref:`checklists` for the full format
and workflow guide.

Working copies
--------------

:command:`debops checklist open` copies a checklist into the state
directory as a working copy. One form takes a checklist name and
creates an implicit copy whose id is the name:

.. code-block:: console

   alice@controller:~$ debops checklist open example/audit/periodic-security-review
   Opened example/audit/periodic-security-review [packaged]

The other form takes a copy id first:

.. code-block:: console

   alice@controller:~$ debops checklist open web example/audit/periodic-security-review
   Opened example/audit/periodic-security-review as copy web [packaged]

An id holds exactly one checklist. Re-opening an occupied id refuses
unless ``--reset`` discards the current state. The cycle of a
recurring review is:

.. code-block:: console

   alice@controller:~$ debops checklist open review example/audit/periodic-security-review
   ... run the review, record findings and measured values ...
   alice@controller:~$ debops checklist commit review --close

Re-open the copy with ``--reset`` at the next cycle. A lone copy
id works too: ``debops checklist open review --reset`` resolves
through the sidecar of the open copy.

A copy id can carry an Ansible inventory pattern in square brackets:
'subdir/[webservers]/check' opens one copy per matching host,
all-or-nothing -- an occupied id refuses the whole batch unless
``--reset`` re-opens the occupied copies. The id supports one
pattern; a pattern that matches no hosts refuses the batch.
``--dry-run`` prints the expansion without opening anything. The id
needs quoting in the shell.

The copy id can carry slashes. Nested ids form a tree and record
under nested vault paths. A copy id that starts with the checklist
name displays relative to it: the copy ``flow/alpha`` of the
checklist ``flow`` shows as ``alpha`` under the root, unless
another copy already occupies the stripped id.

Commit and close
----------------

:command:`debops checklist commit` writes the copy into the project
vault and the checklist stays active. With ``--close``, the command
deactivates the copy after the commit; unlike the close command, no
``--force`` is demanded for an incomplete copy, because the record
exists and the working copy's loss is recoverable. An unchanged
re-commit reports "No changes since the last commit". The command
still attempts the git commit, so a record that a failed hook left
out of history heals on the next run. With ``--edit``, you compose
the commit message in the editor. With ``--all``, every open copy
commits -- or every copy of the checklist named as the operand; an
invalid copy is skipped with its reason, the rest of the batch
proceeds.

:command:`debops checklist close` discards a copy. It refuses when
open items remain or the checklist has no task items. ``--force``
overrides. With ``--all``, every open copy closes: completed ones
normally, the rest only with ``--force``.

An omitted ``<copy>`` operand resolves to the only open copy. With
several copies open, name one.

Vault layout
------------

Records group by checklist. The filename is the copy's open date.
The ``_copies`` segment separates named copies from the implicit
ones. The reserved name is refused in checklist names and copy ids.

.. code-block:: text

   vault/checklists/
   ├── example/audit/periodic-security-review/
   │   └── _copies/review/
   │       └── 2026-05-11.md
   ├── debian/dist-upgrade/bookworm-to-trixie/
   │   └── 2026-11-10.md
   └── system/host-reboot/
       └── 2026-07-14.md

The commit command writes each record with mode ``0600``. The git
history of the vault keeps the progression of each copy.

Options
-------

:command:`debops checklist list`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

List the discovered checklists and the open copies. With
``--active``, the roster of the open copies replaces the discovered
entries.

``-a, --active``
  List the open copies instead of the discovered checklists.

``-f, --format text|json``
  Select the output format, ``text`` by default. The JSON format
  prints one record per checklist, or per open copy with
  ``--active``, for scripts to consume.

``-v, --verbose``
  Increase the output verbosity: the titles at ``-v``, the origin
  of each checklist at ``-vv``.

``-h, --help``
  Display the help and usage information.

:command:`debops checklist open`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Copy a checklist into the state directory as an open copy. The
checklist name is relative to a layer root and accepts an optional
``.md`` suffix. A copy id before the name creates a named copy.

``-r, --reset``
  Discard the current state of the copy id and re-copy the
  checklist. A lone copy id with ``--reset`` re-opens the copy from
  the checklist its sidecar records, resolved fresh through the
  current layers.

``--no-reset``
  Keep the current state of the copy id (default).

``-d, --dry-run``
  Print what would be opened -- the expanded copy ids, already-open
  copies marked -- without opening anything.

``-h, --help``
  Display the help and usage information.

:command:`debops checklist edit`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open the working copy in the editor and print the copy's progress
after the editor returns. The editor comes from ``$VISUAL``,
``$EDITOR``, the ``sensible-editor`` fallback, and ``vi`` last.

``-h, --help``
  Display the help and usage information.

:command:`debops checklist commit`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Write the copy into the project vault as a dated record and keep
the checklist active.

``-c, --close``
  Deactivate the copy after the commit.

``-e, --edit``
  Compose the commit message in the editor.

``-A, --all``
  Commit every open copy, or every copy of the checklist named as
  the operand; an invalid copy is skipped with its reason, the rest
  of the batch proceeds.

``-h, --help``
  Display the help and usage information.

:command:`debops checklist close`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Discard the copy. The command refuses when open items remain or
the checklist has no task items.

``-f, --force``
  Discard the copy anyway.

``-A, --all``
  Close every open copy: the completed ones normally, the rest
  only with ``--force``.

``-h, --help``
  Display the help and usage information.
