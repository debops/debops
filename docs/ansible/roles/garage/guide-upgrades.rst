.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _garage__ref_guide_upgrades:

Upgrading Garage
================

.. only:: html

   .. contents::
      :local:


Why the role gates upgrades
---------------------------

Garage treats a change of the major version number as a major upgrade.
A minor upgrade (``2.4.1`` to ``2.5.0``) is a rolling restart. A major
upgrade (``1.x`` to ``2.0``) switches the RPC protocol, must go through
each major version in turn, and needs every node restarted together
after you have read the upstream changelog.

The role therefore refuses to replace an installed binary unless
:envvar:`garage__upgrade` allows that class of change. The role manages
upgrades from Garage 1.0 onwards; upgrade older installations to the
latest 1.x release by hand first. Bumping :envvar:`garage__version`
without also updating :envvar:`garage__binary_sha256_map` makes the
download fail its checksum verification.


Before upgrading a cluster
--------------------------

Upstream recommends to check the consistency of the metadata tables
before an upgrade. This walks every node of the cluster and is not done
by the role. Run it on one node and wait until the repair workers listed
by :command:`garage worker list` have finished:

.. code-block:: console

   sudo garage repair --all-nodes --yes tables
   sudo garage worker list


Minor upgrades
--------------

A minor upgrade stays inside the same major version. The default
:envvar:`garage__upgrade` is ``minor``, so a play that only bumps the
minor or patch number will:

1. Check the upgrade gate: no downgrade, no change of the major version,
   and :envvar:`garage__upgrade` not set to ``none``.

2. Run :command:`garage meta snapshot` on the running daemon when
   :envvar:`garage__upgrade_snapshot` is ``True``. The snapshot needs
   the daemon: when :file:`garage.service` is not active, the role skips
   it and still replaces the binary, so back up the metadata directory
   yourself before you upgrade a stopped node.

3. Download the new binary next to the installed one and verify its
   checksum, then replace the installed binary atomically while the
   daemon is still running. A failed download or checksum stops the
   play here and leaves both the binary and the service untouched.

4. Restart :file:`garage.service` with the new binary. The restart is an
   Ansible handler which runs at the end of the role. If the play stops
   between the binary replacement and the restart, the next run finds
   the new version already installed and does not restart the daemon,
   so restart :file:`garage.service` by hand.

An installed binary which does not report its version stops the role
before any of these steps. Check or remove it by hand first.

Run the playbook node by node:

.. code-block:: yaml

   garage__version: '2.5.0'

.. code-block:: console

   debops run service/garage --limit s3-1.example.com
   debops run service/garage --limit s3-2.example.com

or set ``serial: 1`` in a wrapper playbook. Clients keep working as
long as the remaining nodes still form a quorum.


Major upgrades
--------------

Set :envvar:`garage__upgrade` to ``major`` only after you have:

- read the upstream changelog and any ``garage migrate`` notes for
  that hop,
- confirmed that the target major version is the next one after the
  installed version (``1`` to ``2`` is fine, ``1`` to ``3`` is refused),
- taken a metadata snapshot you can restore.

The `upstream upgrade guide`__ lists the checks to do before and after
the upgrade; the steps below cover the parts the role is involved in.

.. __: https://garagehq.deuxfleurs.fr/documentation/operations/upgrading/

A major upgrade changes the RPC protocol, and nodes on different major
versions cannot talk to each other. The role cannot restart all nodes at
the same moment: the restart handler runs on each host on its own, and
a host which fails or is unreachable does not stop the others. Stop the
whole cluster before the play instead, so that no node runs the old
version next to the new one:

1. Stop writing to the cluster and take a metadata snapshot on every
   node while the daemons still run:

   .. code-block:: console

      sudo garage meta snapshot --all

   Garage keeps only the two most recent snapshots, and a snapshot does
   not include the cluster layout. Copy the new snapshot, together with
   the :file:`cluster_layout` file from :envvar:`garage__metadata_dir`,
   off every node until the upgrade is confirmed.

2. Stop :file:`garage.service` on every node of the cluster being
   upgraded. When ``[debops_service_garage]`` holds several independent
   clusters, use the inventory group of that cluster (``garage_main``
   in this example) here and in the next step:

   .. code-block:: console

      debops exec garage_main -b -m ansible.builtin.systemd \
                  -a 'name=garage.service state=stopped'

3. Set the new version and allow the major upgrade in the inventory,
   then run the service playbook against the same nodes. The role
   replaces the binary and starts the service with the new version;
   its own snapshot step is skipped, because the daemon is stopped.

   .. code-block:: yaml

      garage__version: '2.5.0'
      garage__upgrade: 'major'

   .. code-block:: console

      debops run service/garage --limit garage_main

4. When the play fails on a node, the node can be left with the old or
   the new binary and with the service stopped or running, depending on
   the task which failed. Check :command:`garage --version` and
   :command:`systemctl status garage.service` there, stop the service
   if it runs the old version, fix the cause and run the playbook on
   that node again.

5. Before you resume writing, check that every node reports the new
   version and that :command:`garage status` lists all of them as
   connected.

Do not use ``--limit`` or ``serial: 1`` with the daemons still running
for a major upgrade: the cluster would run with mixed major versions
until the last node is done.


Disabling upgrades
------------------

:envvar:`garage__upgrade` ``none`` makes the role fail when the
installed binary does not match :envvar:`garage__version`. Use this on
hosts where a binary change must be a separate, reviewed event.


Downgrades
----------

Downgrades are not supported. Restore the previous data directory from
backup and pin :envvar:`garage__version` to the restored binary.


Local facts
-----------

After a successful play, ``ansible_local.garage`` reports at least:

``installed``
  Whether the binary at :envvar:`garage__bin_path` is present.

``version``
  Installed binary version.

``layout_version``
  Current cluster layout version, when the daemon is reachable. The
  role uses this to refuse ``--single-node`` once the layout has grown
  past version 1.

The fact script limits each call of the :command:`garage` CLI to 10
seconds, so a daemon which does not respond does not block fact
gathering.
