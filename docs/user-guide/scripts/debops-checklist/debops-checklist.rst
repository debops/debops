.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

:command:`debops checklist list`
--------------------------------

The listing shows what the discovery layers provide and which copies
you have open. Selection globs narrow the listing to the matching
names and copy subtrees. A copy whose source changed since you opened
it is marked ``[stale]``, and an implicitly open copy reports its
progress.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``-v, --verbose``
  Increase the output verbosity: the titles at ``-v``, the origin of
  each checklist at ``-vv``.

``--project-dir <project_dir>``
  Path to the project directory to work on. If it's not specified, the
  script will use the current directory.

``-a, --active``
  List the open copies instead of the discovered checklists.

``-f, --format text|json``
  Select the output format, ``text`` by default. The JSON format
  prints one record per checklist, or per open copy with
  ``--active``, for scripts to consume.

``<glob>...``
  Selection globs over the checklist names. The globs use the syntax
  of the ``checklist.filters`` patterns. A run of ``*`` crosses the
  slash, ``?`` matches any single character, and the match is
  anchored to the whole name. A name matching any glob is listed.
  Without globs, everything is listed. A copy is listed through its
  checklist name or its copy id, in the stored, the relative or the
  qualified spelling. The globs narrow the listing, not the
  discovery: a name left out of the listing can still be opened. A
  ``!``-prefixed glob is refused. The ``!`` hide rules belong to the
  ``checklist.filters`` configuration option.

Examples
~~~~~~~~

List the checklists and show which layer provided each:

.. code-block:: shell

   debops checklist list -vv

List only the checklists of one namespace:

.. code-block:: shell

   debops checklist list 'system/**'

:command:`debops checklist open`
--------------------------------

Open turns a checklist into a working copy: the source file stays
untouched, and your ticks and annotations land in the copy. Copies let
you run the same checklist for several hosts, systems or cycles at the
same time. The implicit copy takes the checklist name as its id. A
named copy uses an id you choose.

An Ansible inventory pattern in square brackets opens one copy per
matching host in a single command. A lone copy id re-opens the
existing copy from the checklist its sidecar records.

This is the cycle of a recurring review. Open the copy once. Commit
it with ``--close`` after each cycle. A closed copy no longer
occupies the id, so the next cycle opens without ``--reset``. That
option is for a different case: it replaces a modified, still-open
copy with a clean one.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

``--project-dir <project_dir>``
  Path to the project directory to work on. If it's not specified, the
  script will use the current directory.

``-r, --reset``
  Discard the current state of the copy id and re-copy the checklist,
  possibly a different one. An occupied id refuses without the option,
  so ``--reset`` is the way to replace a modified, still-open copy with
  a clean one. A lone copy id with ``--reset`` re-opens the copy from
  the checklist its sidecar records, resolved fresh through the current
  layers.

``--no-reset``
  Keep the current state of the copy id (default).

``-d, --dry-run``
  Print what would be opened, with already-open copies marked, without
  opening anything.

``<copy-id>``
  Copy id for a named copy. Omit it to open an implicit copy whose id
  is the checklist name.

``<checklist>``
  Checklist path relative to a layer root, with an optional ``.md``
  suffix.

Examples
~~~~~~~~

Open a named copy of a packaged checklist:

.. code-block:: shell

   debops checklist open web example/audit/periodic-security-review

Open one copy per host of an inventory pattern:

.. code-block:: shell

   debops checklist open 'subdir/[webservers]/check' host-verify

:command:`debops checklist edit`
--------------------------------

Edit opens the working copy in your editor, so you can tick items and
add notes. It prints the copy's progress when the editor returns. The
editor comes from ``$VISUAL``, ``$EDITOR`` or the ``sensible-editor``
fallback, with ``vi`` as the last resort.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

``--project-dir <project_dir>``
  Path to the project directory to work on. If it's not specified, the
  script will use the current directory.

``<copy>``
  Copy id or checklist path. Without one, the command uses the only
  open copy.

Examples
~~~~~~~~

Edit the open copy ``review``:

.. code-block:: shell

   debops checklist edit review

:command:`debops checklist commit`
----------------------------------

Commit turns the working copy into a dated record in the project
vault, and the copy stays open for further work. The command commits
the record to the project git repository with a generated message that
names the checklist and the progress. A search of the git log finds a
past cycle by its message.

An unchanged re-commit reports ``No changes since the last commit``
and still attempts the git commit. A failed git commit is an error.
The record stays on disk, and the next run commits it. The project's
pre- and post-commit hooks run on every commit, also on an unchanged
re-commit.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

``--project-dir <project_dir>``
  Path to the project directory to work on. If it's not specified, the
  script will use the current directory.

``-A, --all``
  Commit every open copy, or every copy of the checklist named as the
  operand. An invalid copy is skipped with its reason, and the rest of
  the batch proceeds. The exit code reports the partial failure.

``-c, --close``
  Deactivate the copy after the commit. Unlike close, no ``--force``
  is demanded for an incomplete copy: the vault record exists, so the
  working copy's loss is recoverable.

``-e, --edit``
  Compose the commit message in the editor.

``<copy>``
  Copy id or checklist path. Without one, the command uses the only
  open copy. With ``--all``, the operand names the checklist whose
  copies all commit.

Examples
~~~~~~~~

Commit the open copy and deactivate it:

.. code-block:: shell

   debops checklist commit review --close

:command:`debops checklist close`
---------------------------------

Close discards a working copy without recording it. Open items mean
unfinished work, so the command refuses unless you pass ``--force``.
The same refusal covers a copy without task items. With ``--all``,
completed copies close normally, and the rest close only with
``--force``.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

``--project-dir <project_dir>``
  Path to the project directory to work on. If it's not specified, the
  script will use the current directory.

``-f, --force``
  Discard the copy even when items are still open.

``-A, --all``
  Close every open copy: the completed ones normally, the rest only
  with ``--force``. The skipped copies appear in the report with their
  reason.

``<copy>``
  Copy id or checklist path. Without one, the command uses the only
  open copy.

Examples
~~~~~~~~

Close every open copy, forcing the incomplete ones:

.. code-block:: shell

   debops checklist close --all --force
