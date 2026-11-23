.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The :command:`debops tofu` section runs OpenTofu in the environment of
a DebOps project. Each infrastructure view of the project maps to one
OpenTofu working directory. OpenTofu encrypts the state and the plan
files of the view natively and keeps them in the view's encrypted
store. The wrapper composes the environment of every OpenTofu run.
The environment carries the relocated data directory, the shared
plugin cache, the workspace and the state passphrase read from the
unlocked store.

The DebOps-level operations manage the view and its artifacts.
``mkview`` creates a view with its encrypted store. ``update``
reconciles the generated files of the view and initializes the
working directory. ``install`` installs the pinned OpenTofu
binaries. ``plans`` manages the saved plan files. ``rekey`` rotates
the state passphrase. ``inventory`` renders the OpenTofu outputs
into the Ansible inventory. ``cache`` maintains the OpenTofu
caches.

The OpenTofu operations pass through, with the wrapper environment
composed around them. A few of them build the workflows. ``init``
prepares the working directory. ``plan`` saves a plan file into the
view's store when the operator does not name one with ``-out``.
``apply`` and ``destroy`` need an approval. On a terminal the
wrapper asks for it. A non-interactive run needs an explicit
``-auto-approve`` option or a saved plan file, which is pre-approved
by construction. Run :command:`debops tofu --help` for the full list
of the OpenTofu commands.

This command executes :ref:`hook scripts <debops_hooks>`
(``pre-tofu-<operation>`` and ``post-tofu-<operation>``) before and
after the OpenTofu operations.

The full documentation of the section lives in the DebOps manual:
the :ref:`OpenTofu integration <debops_tofu>` page and the
:ref:`OpenTofu - Ansible inventory bridge <debops_tofu_inventory>` page.
