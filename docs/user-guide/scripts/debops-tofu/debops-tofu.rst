.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

:command:`debops tofu`
----------------------

The section resolves the view from the :literal:`-V/--view` option or
the project default. It refuses to operate on a view directory the
project does not define. The options of the wrapper stand before the
operation, and the options of the operation after it. The
:literal:`--` separator may stand between them.

Options
~~~~~~~

The options below need to be specified before the operation to take
effect.

``-h, --help``
  Display the OpenTofu help followed by the options of the wrapper.

``--project-dir <project_dir>``
  Path to the project directory to work on. If it's not specified, the
  script will use the current directory.

``-V <view>, --view <view>``
  Specify the name of the "infrastructure view" to run the operation
  against. If not specified, the default view will be used
  automatically.

``-E, --bell``
  Emit an ASCII "bell" at the end of the operation to notify the
  user. This might be useful during longer operations.

``--no-color``
  Strip the ANSI color codes from the operation output.

``-w <workspace>, --workspace <workspace>``
  Run the operation against the named workspace of the view,
  overriding the workspace configured for the view. OpenTofu refuses
  a nonexistent workspace; create it with
  :command:`debops tofu workspace new <workspace>`.

``-M, --allow-missing-state``
  Proceed with the state-touching operations on a view whose state
  file is missing: the deliberate wipe-and-rebuild path. Without the
  option the wrapper refuses, because OpenTofu would silently
  re-initialize the state and plan to create all of the
  infrastructure again.

``--eval``
  Do not execute the operation; print out the environment variables
  and the command itself to stdout. On the DebOps-level operations
  which render changes, the behavior is the dry run: the changes are
  reported without the writes.

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

``--``
  Mark the end of the wrapper options. Any of the options after this
  mark belong to the operation.

The DebOps-level operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

``mkview <new_view>``
  Create a new view with its encrypted store and the environment
  file with the generated state passphrase.

  ``-e, --encrypt [encfs|git-crypt|plain]`` picks the encryption of
  the store. The mechanism detected in the project is the default:
  ``git-crypt`` for the repository-wide setup, ``encfs`` where the
  Ansible views carry EncFS volumes. The option is required when the
  project carries no store yet. ``plain`` commits the passphrase
  unencrypted.

  ``--keys <recipients>``
    The list of the GPG recipients with secret access, delimited by
    commas. Required for EncFS.

  ``-p, --provider <source>``
    Require the OpenTofu provider in the created view, as a registry
    source address. Repeatable.

  ``-m, --module <spec>``
    Instantiate the OpenTofu module in the created view, as a
    registry source address with an optional ``=version`` suffix.
    Repeatable.

``update``
  Reconcile the files DebOps owns in the view and run
  :command:`tofu init` through the wrapper.

  ``-n, --dry-run``
    Report the reconcile without applying it.

  ``--diff``
    Print the unified diffs of the changes instead of the paths.

  ``--force``
    Overwrite, clear or remove paths which already exist.

``install``
  Install the OpenTofu binaries which the views of the project pin,
  verified against the release checksums.

  ``--force``
    Reinstall the binaries which are installed already.

``plans [<verb> [<id>]]``
  List the plan files the wrapper saves for the view. The
  ``show``, ``apply`` and ``delete`` verbs act on one of them by its
  sequence id or the unique prefix of its file name.

  ``--json``
    Render the plan as JSON with the ``show`` verb.

``rekey``
  Rotate the state passphrase of the view. An interrupted rotation
  resumes on a re-run.

``inventory``
  Render the inventory outputs of the view into the Ansible view's
  inventory.

  ``-t, --to-view <view>``
    Render into the named Ansible view's inventory and store,
    instead of the mirror view of the same name. The
    ``views.<view>.tofu.inventory.to_view`` option sets the
    default. The option on the command line wins.

  ``-f, --force``
    Refresh the state of the view before the render.

  ``-n, --dry-run``
    Report the render without applying it.

  ``--diff``
    Print the unified diffs of the changes instead of the paths.

``cache``
  List the OpenTofu caches of the project: the data directories of
  its views, the in-tree leftovers of the older views and the shared
  plugin cache.

  ``--clean``
    Remove the cache entries of the selected scope.

  ``--project``
    Scope the clean to the data directories of all the views of the
    project.

  ``--plugins``
    Scope the clean to the shared plugin cache of all the views and
    projects.

  ``--reset``
    Clean the whole cache root: the data directories of all the
    projects, the shared plugin cache, and the stale entries of
    the projects which moved away. The clean reaches the caches
    of the other projects too.

``<tofu operation> [<args>]``
  Every other token runs the :command:`tofu` command with the
  wrapper environment composed around it. Run
  :command:`debops tofu --help` for the full list of the OpenTofu
  commands.

Examples
~~~~~~~~

Create a view, initialize it and save the first plan:

.. code-block:: shell

   debops tofu mkview production -p lxc/incus
   debops tofu -V production update
   debops tofu -V production plan

Review the saved plan and apply it:

.. code-block:: shell

   debops tofu -V production plans show 1
   debops tofu -V production plans apply 1

Render the inventory outputs of the view into the Ansible inventory,
with the state refreshed first:

.. code-block:: shell

   debops tofu -V production inventory --force

Check the drift of a view and print the diff of the reconciliation
plan:

.. code-block:: shell

   debops tofu -V production plan -detailed-exitcode --diff

Print the command the wrapper would run, without executing it:

.. code-block:: shell

   debops tofu --eval -V production plan
