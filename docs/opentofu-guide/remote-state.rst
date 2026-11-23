.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _tofu_remote_state:

OpenTofu remote state with GitLab
=================================

.. contents::
   :local:

A single controller carrying the state of a fleet is a risk you do
not have to take. GitLab hosts OpenTofu state through the standard
HTTP backend contract. The state lives in a GitLab project, protected
by GitLab's own at-rest encryption, with locking and version history.
The state stays encrypted twice. OpenTofu seals it with the view's
passphrase before the backend writes it, and GitLab stores the sealed
envelope. The ``encryption`` stanza of the view template keeps
working unchanged.


Prerequisites
-------------

You need two things before touching the view.

A GitLab project to host the state. Any project works. A small
dedicated one like :file:`infra/tofu-state` keeps the state clearly
owned. Note the numeric project id: the endpoint URLs use it.

A personal access token with the ``api`` scope, from the user that
owns the state. Tokens expire. Plan the rotation when you create one.

The view configuration
----------------------

The backend block stays partial, with no secrets in tracked files:

.. code-block:: text

   # tofu/views/<view>/main.tf
   terraform {
     backend "http" {}

     encryption {
       # the stanza the view template carries, unchanged
     }
   }

The endpoints and the token live in the view's store, in a file the
store routing encrypts at commit. The store cycle makes it readable
for every operation:

.. code-block:: ini

   # tofu/views/<view>/secret/backend.conf
   address        = "https://gitlab.example.com/api/v4/projects/42/terraform/state/production"
   lock_address   = "https://gitlab.example.com/api/v4/projects/42/terraform/state/production/lock"
   unlock_address = "https://gitlab.example.com/api/v4/projects/42/terraform/state/production/lock"
   username       = "alice"
   password       = "<personal access token>"
   lock_method    = "POST"
   unlock_method  = "DELETE"
   retry_wait_min = "5"

The backend requires the lock endpoints. Without them the HTTP
backend runs
with locking disabled, and two concurrent runs would race the state.
The lock and unlock URLs are the state URL with :literal:`/lock`
appended.

Then mark the view as remote-backed, so the wrapper skips the local
state checks:

.. code-block:: console

   alice@controller:~$ debops config set views.<view>.tofu.state_path ''

The same switch, hand-written in the view's configuration drop-in:

.. code-block:: toml

   # .debops/conf.d/view-<view>-tofu.toml

   [views."<view>".tofu]
   state_path = ""

What stays local: the plan files, the view configuration, the store.
The store cycle still runs around every operation. The passphrase
reaches OpenTofu through the environment, which is why the cycle
remains required.


The command flow
----------------

.. code-block:: console

   alice@controller:~$ cd ~/src/projects/<project>
   alice@controller:~$ debops tofu -V <view> init -reconfigure \
       -backend-config=secret/backend.conf
   alice@controller:~$ debops tofu -V <view> plan
   alice@controller:~$ debops tofu -V <view> plans apply 1

Use :literal:`-reconfigure` on the first init and on any backend
change. The apply takes the saved plan by its view-relative path —
the wrapper runs OpenTofu from the view directory, so
:file:`plans/<file>`, not :file:`tofu/views/<view>/plans/<file>`.
The plan acquires and releases the remote lock for its duration. An
apply holds it for the whole run.

**Migrating an existing view.** When the state already sits in the
local store, point the backend block at GitLab and run the init with
:literal:`-migrate-state` instead of :literal:`-reconfigure`. The
local state uploads to GitLab and the store keeps the last local copy
as the just-in-case net.


Checking the deployment
-----------------------

Read the state back through the API:

.. code-block:: console

   alice@controller:~$ curl -sS -H "Authorization: Bearer <token>" \
       "https://gitlab.example.com/api/v4/projects/42/terraform/state/production"

The response should be the encrypted envelope: the
``encrypted_data``, ``encryption_version``, ``lineage`` and ``serial``
keys at the top level. A serial that advances per apply and the
envelope keys are the proof that the remote write works and the
encryption applied.


Locking
-------

Every state-touching operation acquires the lock for its duration and
releases it at the end. The lock is per state, not per view: separate
state names lock independently. GitLab has no HTTP-backend
workspaces. Separate environments mean separate state names, which
matches the DebOps view model directly.

A lock created by hand makes the next plan refuse:

.. code-block:: text

   Error: Error acquiring the state lock
   Error message: HTTP remote state already locked: ID=manual-lock-test

GitLab checks the complete lock payload. A partial body gets a 400
response naming the missing fields.

A crashed run leaves the lock held, because dead processes do not
release it, and the refusing run names the lock id. The way out is the raw
passthrough, in its non-interactive form:

.. code-block:: console

   alice@controller:~$ debops tofu -V <view> force-unlock -force 7f3a2b1c9d4e

The lock id to release is the one the refusing operation named. For a
GitLab-hosted state the web UI carries lock and unlock buttons on the
state page, the same surface without the terminal.

Never force-unlock a lock you cannot explain. An operation may still
be running on another controller, and pulling the lock out from
under a live apply corrupts the state.


Other backends
--------------

The HTTP backend is OpenTofu's generic remote protocol, and GitLab
is one implementation of it. The same view pattern serves every
standard backend: an empty backend block, credentials in a store file
passed with :literal:`-backend-config=`, and an empty
``state_path``. What changes per backend is where the
credentials live:

.. list-table::
   :widths: 15 40 45
   :header-rows: 1

   * - Backend
     - Storage and locking
     - Credentials
   * - ``s3``
     - Object storage. Native S3 lockfiles via
       :literal:`use_lockfile = true`, or DynamoDB. MinIO, Ceph and
       Garage work through the ``endpoints`` option.
     - Static keys in the backend config file, or the ``AWS_*``
       environment variables.
   * - ``consul``
     - Consul KV with session locks.
     - The ``access_token`` backend option, or the
       ``CONSUL_HTTP_TOKEN`` environment variable.
   * - ``pg``
     - A PostgreSQL table with advisory locks. No ``force-unlock``.
     - The ``PG*`` environment variables: the untracked
       :file:`.env` file or the ambient environment.
   * - ``kubernetes``
     - A Secret plus a Lease.
     - A kubeconfig path, or the in-cluster configuration.
   * - ``azurerm``, ``gcs``
     - The cloud blob stores with their native locking.
     - The cloud credentials through their own environment
       variables.

One caveat applies to every backend. OpenTofu caches the values
passed through :literal:`-backend-config=` in its data directory and
in the plan files. The view's stanza encrypts the plan files. The
data directory is the relocated cache the :command:`debops tofu
cache` operation manages. Credentials which exist as backend options
belong in the store file. Credentials which exist only as environment
variables belong in the untracked :file:`.env` file or your shell
environment.


See also
--------

- :ref:`debops_tofu` for the OpenTofu integration and the view
  model
- :ref:`tofu_registry_modules` for hosting the OpenTofu modules on
  the same GitLab instance
- :ref:`tofu_state_adoption` for moving an existing fleet to a view
  with a fresh passphrase
