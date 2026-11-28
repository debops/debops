.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The :command:`debops checklist` subcommand manages operational
checklists: Markdown files whose task items use the GitHub task-list
syntax__.

.. __: https://github.github.com/gfm/

A task item is a list line with a one-character state marker in its
brackets. The state markers are: ``[ ]`` open, ``[x]`` or ``[X]``
done, ``[B]`` or ``[~]`` blocked, ``[F]`` or ``[!]`` failed, ``[N]``
or ``[-]`` not applicable. Both spellings parse. Unknown bracket
content reads as open. Longer bracket content is commentary, not a
state.

Checklists resolve from the project directory, the user directory and
the packaged set, in that order of precedence. Several copies can be
open at once. Committing a copy writes a dated record into the
DebOps project directory.

The full documentation of the section lives in the DebOps manual,
in the :ref:`checklists` page.
