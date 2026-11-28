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
content reads as open.

Checklists resolve from the project directory, the user directory and
the packaged set, in that order of precedence. Multiple checklist
copies can be opened at once, edited and committed in the DebOps
project directory as records.
