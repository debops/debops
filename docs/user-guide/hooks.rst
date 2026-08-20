.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _debops_hooks:

Hook scripts
============

DebOps CLI supports hook scripts that let you extend or customize its behavior
at various points during execution. You can use hooks to run custom commands
before or after Ansible playbook execution, project initialization, secrets
locking, and other operations.

Hook locations
--------------

DebOps searches for hook scripts in two directories, in priority order:

1. :file:`<project>/.debops/hooks/<hook_name>/` — project-local hooks
2. :file:`$XDG_CONFIG_HOME/debops/hooks/<hook_name>/` — user-global hooks

Scripts from the project-local directory run first, followed by user-global
scripts. Within each directory, scripts run in sorted order. Use numeric
prefixes like ``00-``, ``99-`` for deterministic ordering.

The project-local hooks directory (``.debops/hooks/``) is intentionally **not**
created automatically during :command:`debops project init`. This avoids
polluting git repositories with empty directories and ``.gitkeep`` files. Create
the directory manually when you need it:

.. code-block:: shell

   mkdir -p .debops/hooks/pre-run

Available hook points
---------------------

The following hook names are available. Each hook point has a ``pre-`` variant
that runs before the operation, and a ``post-`` variant that runs after.

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Hook name
     - Triggered by
   * - ``pre-run`` / ``post-run``
     - :command:`debops run` (playbook execution)
   * - ``pre-check`` / ``post-check``
     - :command:`debops check`, or :command:`debops run` with ``--check``
   * - ``pre-exec`` / ``post-exec``
     - :command:`debops exec` (ad-hoc Ansible command)
   * - ``pre-env`` / ``post-env``
     - :command:`debops env` (environment inspection)
   * - ``pre-init`` / ``post-init``
     - :command:`debops project init`
   * - ``pre-commit`` / ``post-commit``
     - :command:`debops project commit`
   * - ``pre-refresh`` / ``post-refresh``
     - :command:`debops project refresh`
   * - ``pre-lock`` / ``post-lock``
     - :command:`debops project lock`
   * - ``pre-unlock`` / ``post-unlock``
     - :command:`debops project unlock`

The ``run`` and ``check`` hook points are distinguished by the actual execution
mode, not the CLI subcommand. If you run :command:`debops run` with ``--check``
in the ansible arguments, or if the ``read_only_friday`` project option is
enabled, the ``pre-check``/``post-check`` hooks will fire instead of
``pre-run``/``post-run``.

Execution environment
---------------------

Each hook script runs as a subprocess with the following environment:

``DEBOPS_HOOK_NAME``
  Name of the hook being executed (e.g. ``pre-run``, ``post-lock``).

``DEBOPS_PROJECT_PATH``
  Absolute path to the DebOps project directory.

``DEBOPS_RETURN_CODE``
  Exit code of the preceding operation. Available only in ``post-`` hooks
  for :command:`debops run`, :command:`debops check`, :command:`debops exec`,
  and :command:`debops env`. Not available in ``pre-`` hooks or project
  lifecycle hooks.

The script also inherits the full process environment, which includes all
DebOps-configured variables (``DEBOPS_ANSIBLE_COLLECTIONS_PATH``,
``ANSIBLE_CONFIG``, etc.).

The working directory for the script is set to the project directory.

Script requirements
-------------------

Hook scripts must be:

- **Executable** — non-executable files in the hooks directory are silently
  skipped.
- **Well-behaved** — each script should complete within 5 minutes (300 seconds).
  Scripts that exceed the timeout are killed and treated as failures.
- **Exit-code aware** — a non-zero exit code from any script aborts the
  operation. Subsequent scripts in the same hook point are not executed.

Secrets visibility
------------------

The availability of decrypted secrets depends on the hook point:

- **Pre-hooks in runners** (``pre-run``, ``pre-check``, ``pre-exec``,
  ``pre-env``) run **before** the secrets are unlocked. Encrypted files are not
  accessible at this point.
- **Post-hooks in runners** (``post-run``, ``post-check``, ``post-exec``,
  ``post-env``) run **after** the secrets have been re-locked. Encrypted files
  are not accessible.
- **Pre-hooks for lock/unlock** run before the respective operation, so secrets
  may be in either state depending on the current lock status.
- **Post-hooks for lock/unlock** run after the respective operation completes.

Examples
--------

Log playbook execution
~~~~~~~~~~~~~~~~~~~~~~

Create a hook that logs every playbook run to a file:

.. code-block:: shell

   #!/bin/bash
   # .debops/hooks/pre-run/00-log-run

   LOGFILE="${DEBOPS_PROJECT_PATH}/.debops/hooks.log"
   echo "$(date -Iseconds) pre-run: starting playbook execution" >> "${LOGFILE}"

Notify on failure
~~~~~~~~~~~~~~~~~

Create a hook that sends a notification when a playbook fails. This example
uses the ``DEBOPS_RETURN_CODE`` variable available in ``post-`` hooks:

.. code-block:: shell

   #!/bin/bash
   # .debops/hooks/post-run/99-notify-failure

   if [ "${DEBOPS_RETURN_CODE:-0}" -ne 0 ]; then
       echo "Playbook execution failed in ${DEBOPS_PROJECT_PATH}" \
           | mail -s "DebOps failure" admin@example.com
   fi

Prevent commits on Fridays
~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a hook that blocks project commits on Fridays:

.. code-block:: shell

   #!/bin/bash
   # .debops/hooks/pre-commit/00-no-friday-commits

   if [ "$(date +%u)" -eq 5 ]; then
       echo "Friday commits are not allowed. Try again Monday."
       exit 1
   fi

See also
--------

- :ref:`debops-cli` for an overview of the DebOps command-line interface
- :ref:`project_directory` for project directory structure

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
