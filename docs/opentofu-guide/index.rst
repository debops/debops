.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _debops_tofu:

OpenTofu integration
====================

.. contents::
   :local:

DebOps can manage infrastructure with OpenTofu through the
:command:`debops tofu` command section. The section wraps the
:command:`tofu` binary. Every OpenTofu operation runs in the project
environment, and the state of the views stays encrypted. The wrapper
also manages the pinned binaries and bridges the created
infrastructure into the Ansible inventory. After
reading this page you can create a view, plan and apply changes
against it, and keep the plan files under control.

DebOps does not ship OpenTofu modules the way it ships Ansible roles.
An OpenTofu configuration describes a specific infrastructure, not a
parameterized collection of tasks. What DebOps ships instead is the
wrapper around the tool, the view templates, and the secrets
machinery that keeps the key material safe.


How a view maps to OpenTofu
---------------------------

The :ref:`infrastructure views <project_infrastructure_views>` are
environments: the same view name points at the Ansible inventory
root, the Ansible secrets, and the OpenTofu working directory. Each
view with OpenTofu resources gets one OpenTofu workdir. The state of one view never
mixes with the state of another.

In a modern project the OpenTofu tree sits beside the Ansible tree:

.. code-block:: text

   project/
   ├── ansible/
   │   └── views/
   │       └── system/
   └── tofu/
       └── views/
           └── system/
               ├── main.tf               view configuration, owned by you
               ├── providers.tf          generated from the drop-in
               ├── modules.tf            generated, optional
               ├── .terraform.lock.hcl   provider pins, committed
               ├── state/                tracked, natively encrypted
               ├── plans/                transient, retention-pruned
               └── secret/               the encrypted store

A legacy project keeps its OpenTofu tree at :file:`tofu/` directly. Everything below works the same way. The commands resolve the view
from the working directory, so you can run :command:`debops tofu`
from inside :file:`tofu/views/system/` as well as from the
project root.

Run OpenTofu operations against a specific view with the
:literal:`-V/--view` option, or let the wrapper resolve the default
view. This matters more than it looks. The wrapper refuses to guess
when you stand inside a view the project does not define. A command
without :literal:`-V` runs against the default view, not the one you
created last.


What protects what
------------------

One sentence carries the security model:

The DebOps encrypted stores (git-crypt, EncFS) protect the
DebOps-managed secrets. The OpenTofu native encryption protects the
OpenTofu artifacts. The store unlock releases the keys.

In practice this means three things.

The state and the plan files live inside the encrypted store. OpenTofu
encrypts them natively with the ``encryption`` stanza the view
template ships: ``aes_gcm`` over a ``pbkdf2`` key provider, with
``enforced = true`` so OpenTofu refuses to ever write plaintext. The
view creation generates the passphrase and lands it in the store's
tracked :file:`secret/environment` file.

Because the stanza lives in the view configuration and not in the
wrapper, plain :command:`tofu` runs stay encrypted without DebOps.
The wrapper supplies the passphrase through the environment, which is
why every wrapped operation cycles the store: unlock before the
operation, lock after it.

The store itself is the boundary of the key material. The
``secret/environment`` file carries only ``TF_VAR_*`` variables. The
wrapper refuses other keys there and points you at the untracked
:file:`.env` files for general variables.


Getting started
---------------

Create a view, reconcile it, and run the first plan:

.. code-block:: console

   alice@controller:~$ debops tofu mkview system
   Created the OpenTofu view 'system' in project 'example';
       the environment file with the state passphrase is tracked
       behind the git-crypt store
   alice@controller:~$ debops tofu update
   alice@controller:~$ debops tofu plan
   Saved the plan file 'plans/debops-1-20261122T120000.tfplan' of
       the view 'system'

The :command:`debops tofu mkview` operation creates the view tree,
the encrypted store, and the environment file with the generated
state passphrase. The wrapper detects the store mechanism from the
project: git-crypt for a repository-wide setup, EncFS where the
Ansible views carry EncFS volumes. You can also pick it with the
:literal:`-e/--encrypt` option, and seed providers or modules with
:literal:`-p/--provider` and :literal:`-m/--module`.

The :command:`debops tofu update` operation reconciles the files
DebOps owns in the view and runs :command:`tofu init` through the
wrapper. The generated :file:`providers.tf` and :file:`modules.tf`
follow the sets recorded in the view's configuration drop-in. Run the
operation again after you change the recorded sets.

The :command:`debops tofu plan` without an operator's
:literal:`-out` saves the plan file into the view's store, encrypted
at rest together with the state. The saved plan applies without an
approval prompt:

.. code-block:: console

   alice@controller:~$ debops tofu plans show 1
   alice@controller:~$ debops tofu plans apply 1

A one-step :command:`debops tofu apply` (no plan file)
asks for confirmation on a terminal, and refuses without one unless
you pass :literal:`-auto-approve` explicitly. OpenTofu cannot ask for
the approval itself under the wrapper's non-interactive contract, so
the wrapper asks on its behalf.


The wrapper operations
----------------------

The section distinguishes DebOps-level operations, which the wrapper
implements itself, from raw OpenTofu operations, which pass through
with the wrapper environment composed around them:

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Operation
     - What it does
   * - :command:`mkview`
     - Create a new view with its store and the environment file.
   * - :command:`update`
     - Reconcile the generated files of the view and run
       :command:`tofu init`.
   * - :command:`install`
     - Install the OpenTofu binaries the views pin, verified against
       the release checksums and their signature.
   * - :command:`inventory`
     - Render the inventory outputs of the view into the Ansible
       inventory. See :ref:`the OpenTofu - Ansible inventory bridge <debops_tofu_inventory>`.
   * - :command:`plans`
     - List, show, apply or delete the saved plan files.
   * - :command:`rekey`
     - Rotate the state passphrase through the fallback key provider.
   * - :command:`cache`
     - List and clean the relocated OpenTofu data directories and the
       shared plugin cache.

Everything else -- :command:`init`, :command:`plan`, :command:`apply`,
:command:`destroy`, :command:`import`, :command:`state`, and the rest
— passes through to OpenTofu. The wrapper options stand before the
operation, the options of the operation after it. On every
passthrough run the wrapper composes the environment: the relocated
data directory, the shared plugin cache, the workspace, the state
passphrase. It checks the state of the view and fires the
:literal:`pre-tofu-<operation>` and :literal:`post-tofu-<operation>`
hooks around it. See :ref:`debops_hooks` for the hook contract.

The :literal:`tofu.operations` option names the operations the
wrapper may run. An empty list allows all of them. The raw
:command:`tofu` command is not affected by the option, which is why
the option is a nudge, not a fence.

The binary the operations run comes from the version the view pins.
The view creation records the pin in the configuration drop-in,
seeded from the ``tofu.upstream.known_version`` option.
:command:`debops tofu install` downloads, verifies and installs the
pinned versions into the DebOps data directory. A view whose pinned
binary is missing falls back to the configured
``binaries.tofu`` binary.


Plans and drift detection
-------------------------

The saved plan files carry a sequence id and a timestamp stamp. The
ids are stable while the retention prunes the oldest files. The
:literal:`tofu.plan_retention` option (3 by default, 0 disables the
saving) keeps the newest ones. Review one with :command:`plans show`,
with :literal:`--json` for scripts. :command:`plans delete` drops a
plan file you no longer want. The plan files your
own :literal:`-out` option saves are never touched by the retention.

The same surface makes the drift-detection workflow:

.. code-block:: console

   alice@controller:~$ debops tofu plan -detailed-exitcode
   Saved the plan file 'plans/debops-2-20261122T130000.tfplan' of
       the view 'system'

An exit code of 2 means the plan carries changes: the state drifted
from the configuration, or the infrastructure changed outside of
OpenTofu. The saved plan is the reconciliation artifact. Review it with
:command:`plans show 2` and reconcile with
:command:`plans apply 2`.


The cache
---------

The wrapper relocates the OpenTofu data directory out of the view
tree. The resolved providers and modules live under the XDG cache
home, keyed by the project path and the view. One shared plugin cache
serves all views and projects. Everything in the relocated data
directory is re-derivable from the project: the backend metadata from
the view configuration, the provider binaries against the committed
lock file, the modules from their recorded sources. The irreplaceable
state lives in the view's secret store, not in the cache. That is why
the relocation is safe.

The :command:`debops tofu cache` operation lists the data directories
of the project, the in-tree :file:`.terraform/` leftovers of older
views, and the shared plugin cache. The clean scopes rank from the
narrow to the whole:

- :literal:`--clean` cleans the resolved view's data dir.
- :literal:`--clean --project` cleans every view of the project.
- :literal:`--clean --plugins` cleans the shared provider cache.
- :literal:`--clean --reset` cleans the entire cache root.

A cleaned data directory is not a disaster: the next state-touching
operation fails fast until :command:`debops tofu init` runs, and
:command:`debops tofu update` runs it for you. The shared plugin
cache keeps the rebuild cheap.


Configuration options
---------------------

The tofu options live in the project configuration. The table lists
the ones you will actually touch. :command:`debops config get tofu`
prints the effective tree. The defaults in
:file:`src/debops/_data/defaults.toml` document every option.

.. list-table::
   :widths: 35 65
   :header-rows: 1

   * - Option
     - Purpose
   * - ``tofu.state_path``
     - The state file path of the local backend, relative to the view
       directory. Set it to an empty string in views which use a
       remote backend. The wrapper then skips the local state checks.
   * - ``tofu.operations``
     - The operations the wrapper runs. Empty means all.
   * - ``tofu.plan_retention``
     - How many saved plan files to keep. 0 disables the saving.
   * - ``tofu.mkview.*``
     - The options of the view creation: the default provider and
       module sets, the store parameters.
   * - ``tofu.inventory.*``
     - The OpenTofu - Ansible inventory bridge options, in the
       page named above.
   * - ``tofu.upstream.*``
     - The OpenTofu release source: the known version, the release
       base, the release key fingerprint.
   * - ``views.<name>.tofu.*``
     - Per-view overrides: the workspace, the state path, the plan
       retention, the provider and module sets, the binary version.

The view creation records the per-view options in the configuration
drop-in, a file like :file:`.debops/conf.d/view-system-tofu.toml`.
:command:`debops config set` edits it later. The drop-in is the
complete record of what DebOps manages in the view.
:command:`debops config get views.<name>.tofu` prints the recorded
provider and module sets of the view.

Remote state backends are an explicit choice you make in the OpenTofu
configuration, not a DebOps default. The
:ref:`remote state recipe <tofu_remote_state>` walks through the
GitLab setup, and the same pattern serves any backend.


See also
--------

- :ref:`debops_tofu_inventory` for the OpenTofu - Ansible
  inventory bridge, the loop
  that turns created infrastructure into managed hosts
- :ref:`project_infrastructure_views` for the view concept shared by
  Ansible and OpenTofu
- :ref:`debops_hooks` for the hook scripts around the operations
- :ref:`tofu_remote_state` for the remote state recipes
- :ref:`tofu_state_adoption` for adopting existing infrastructure and
  rotating passphrases

.. toctree::
   :maxdepth: 1

   inventory-bridge
   remote-state
   registry-modules
   state-adoption
   ci
   incus
