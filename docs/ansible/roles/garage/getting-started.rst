.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _garage__ref_getting_started:

Getting started
===============

.. only:: html

   .. contents::
      :local:


What is Garage?
---------------

`Garage`__ is an S3-compatible object store. It stores data as immutable
blocks, keeps a small metadata index next to them, and can later grow
from one node to a geo-distributed cluster without changing the client
API.

The ``debops.garage`` role installs Garage from the official static musl
binary, writes :file:`/etc/garage.toml`, and manages a single
:file:`garage.service` unit. There is one Garage instance per host.

.. __: https://garagehq.deuxfleurs.fr/


Why a static binary?
--------------------

Garage is published as a static musl binary per architecture, not as a
Debian package. The role therefore downloads
``https://garagehq.deuxfleurs.fr/_releases/v<version>/<target>/garage``
and verifies a SHA256 checksum shipped in
:envvar:`garage__binary_sha256_map`. Upstream does not publish
checksums, so the map is computed when the pinned version is bumped.

Hosts without access to the upstream release endpoint can get the binary
in three ways: from an image which already contains it (set
:envvar:`garage__skip_install` to ``True``), as a copy from the Ansible
Controller (:envvar:`garage__controller_binary_path`), or from a different
URL in :envvar:`garage__release_url`, for example an internal HTTP mirror
or a ``file://`` URL of a file already present on the host. See
:ref:`garage__ref_binary_source` for details.


A working single-node install
-----------------------------

A freshly started Garage daemon is not usable until a cluster layout
exists. The role does not call :command:`garage layout assign` from
Ansible (that CLI is not idempotent). It starts the daemon with
``--single-node``, which creates a one-node layout at version 1 on first
boot and is a no-op afterwards.

Add the host to ``[debops_service_garage]`` and, if you want a bucket
and a key pair created on the first start, set
:envvar:`garage__default_bucket`:

.. code-block:: ini

   # inventory/hosts
   [debops_service_garage]
   s3.example.com

.. code-block:: yaml

   # inventory/host_vars/s3.example.com/garage.yml
   garage__default_bucket: 'media'

Then run:

.. code-block:: console

   debops run service/garage -l s3.example.com

After the play the S3 API is reachable at ``https://s3.example.com``
through :ref:`debops.nginx`, :command:`garage status` shows an assigned
layout (not ``NO ROLE ASSIGNED``), and
``http://127.0.0.1:3903/health`` on the node returns HTTP 200. The
default key pair lives on the Ansible Controller under
:file:`secret/garage/clusters/default/` and is also written to
:file:`/etc/garage/default-credentials.env` on the host.

A convenient client environment:

.. code-block:: bash

   export AWS_ACCESS_KEY_ID="$(sudo grep GARAGE_DEFAULT_ACCESS_KEY /etc/garage/default-credentials.env | cut -d= -f2)"
   export AWS_SECRET_ACCESS_KEY="$(sudo grep GARAGE_DEFAULT_SECRET_KEY /etc/garage/default-credentials.env | cut -d= -f2)"
   export AWS_DEFAULT_REGION=garage
   export AWS_ENDPOINT_URL=https://s3.example.com
   aws s3 cp ./README.md s3://media/README.md
   aws s3 ls s3://media/

:envvar:`garage__replication_factor` defaults to ``1`` because
``--single-node`` requires it. Do not use a replication factor of 1 for
anything other than a single-node or test deployment.


Independent instances in one inventory
--------------------------------------

By default all hosts in ``[debops_service_garage]`` form one cluster:
they share the secrets stored under
:file:`secret/garage/clusters/<name>/` and a host enables
``--single-node`` only when it is the only member of the group. The list
of cluster members is defined by :envvar:`garage__cluster_hosts`.

To manage several independent Garage instances in the same inventory,
give each instance its own cluster name and limit its cluster to itself:

.. code-block:: yaml

   # inventory/host_vars/s3-backup.example.com/garage.yml
   garage__cluster_hosts: [ '{{ inventory_hostname }}' ]
   garage__cluster_name: 'backup'

Each such host then gets its own ``rpc_secret`` and tokens, and
bootstraps itself with ``--single-node``.

When a multi-node cluster shares the ``[debops_service_garage]`` group
with other instances, define :envvar:`garage__cluster_hosts` for its
members as well, for example with an inventory group per cluster.
Otherwise they count every host in the group as a cluster member, and
the role stops with an error about an inconsistent cluster name:

.. code-block:: yaml

   # inventory/group_vars/garage_main/garage.yml
   garage__cluster_hosts: '{{ groups["garage_main"] }}'
   garage__cluster_name: 'main'


Explicit UNIX account
---------------------

The role uses a dedicated ``_garage`` system account instead of the
upstream ``DynamicUser=true`` unit. DebOps needs a stable UID for data
directories on separate mounts, ACLs and backups.
``DynamicUser`` remaps state under :file:`/var/lib/private/garage` and
breaks when :file:`/var/lib/garage` already exists. The unit still
ships the rest of the upstream hardening (``LimitNOFILE=42000``,
``ProtectHome``, ``NoNewPrivileges``) and sends logs to the journal
through ``GARAGE_LOG_TO_JOURNALD``. To change these options, add
a drop-in file for :file:`garage.service` with the :ref:`debops.systemd`
role.


Dependent role usage
--------------------

- The role stores the cluster-wide ``rpc_secret``, admin token, metrics
  token and the optional default key pair on the Ansible Controller under
  :file:`secret/garage/clusters/<name>/`, using the :ref:`debops.secret`
  conventions. The path does not include ``inventory_hostname``, so every
  node of the same cluster receives the same RPC secret.

- :ref:`debops.nginx` terminates TLS for the S3 API
  (``s3.<domain>`` and ``*.s3.<domain>``) and, when
  :envvar:`garage__nginx_web_enabled` is ``True``, for website hosting
  (``*.web.<domain>``). Garage itself has no native TLS. Virtual-hosted
  bucket URLs only work when the X.509 certificate used by nginx covers
  ``*.s3.<domain>``; clients which use path-style URLs need only
  ``s3.<domain>``.

- :ref:`debops.ferm` opens the RPC port (3901) to the addresses listed
  in :envvar:`garage__rpc_allow`. The S3 port stays closed while nginx
  is enabled and :envvar:`garage__s3_allow` is empty. The website port
  is opened only for the addresses in :envvar:`garage__web_allow`. The
  admin port (3903) is bound to loopback.

- :ref:`debops.etc_services` registers the four Garage TCP ports.


Metrics
-------

The admin API exposes ``/health`` and ``/metrics`` on
``127.0.0.1:3903``. ``/health`` does not require authentication.
``/metrics`` requires a bearer token, which is stored on the host in
:file:`/etc/garage/metrics_token` and on the Ansible Controller in
:file:`secret/garage/clusters/<name>/metrics_token`. Any metrics agent
running on the same host can scrape the endpoint with that token.


Example playbook
----------------

If you are using this role without DebOps, here is an example Ansible
playbook that uses the ``debops.garage`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/garage.yml
   :language: yaml
   :lines: 1,6-


Growing from one node to a cluster
----------------------------------

``--single-node`` is safe only while the layout version is 0 or 1 and
the host is the only member of its cluster. Adding a second node
without turning the flag off makes the daemon refuse to start. Before
you expand:

1. Add the new hosts to ``[debops_service_garage]`` in the inventory,
   without running the role on them yet. If the existing node was set
   up as an independent instance, replace its
   :envvar:`garage__cluster_hosts` override with the list of all
   members of the new cluster, for example with a group per cluster as
   shown above, and use the same list on the new hosts. Set its
   :envvar:`garage__cluster_name` on the new hosts as well, so that they
   use the secrets of the existing cluster instead of the default one.

2. Set :envvar:`garage__single_node` to ``False`` on the existing node.

3. Raise :envvar:`garage__replication_factor` only if you are ready to
   rebuild the layout. The value must be identical on every node; the
   role asserts this.

4. List the addresses of the other nodes in :envvar:`garage__rpc_allow`
   on every node, so that the firewall accepts their RPC connections.

5. Re-run the role on the existing node, so that the unit loses the
   ``--single-node`` flag and the firewall picks up the new allow list.

6. Run the role on the new hosts, then connect them by hand with
   :command:`garage node connect` and :command:`garage layout assign` /
   :command:`garage layout apply`.

Declarative multi-node layout, node connect, buckets and keys are
intentionally out of scope for this version of the role and will come
in a later change.


Rolling minor upgrades
----------------------

A minor upgrade (same major version, for example ``2.4.1`` to
``2.5.0``) is a rolling, node-by-node operation. Run the role with
``--limit`` or ``serial: 1`` so that only one node is replaced at
a time:

.. code-block:: console

   debops run service/garage --limit s3-1.example.com

See :ref:`garage__ref_guide_upgrades` for major upgrades, metadata
snapshots and the ``garage__upgrade`` gate. The Ansible local fact
``ansible_local.garage.version`` reports what is actually installed.


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit
what tasks are performed during an Ansible run.

Available role tags:

``role::garage``
  Main role tag, used in the playbook to execute all of the role tasks
  as well as role dependencies.

``skip::garage``
  Skip the main role's tasks.


Other resources
---------------

- `Garage documentation <https://garagehq.deuxfleurs.fr/documentation/>`_
- `Garage configuration reference <https://garagehq.deuxfleurs.fr/documentation/reference-manual/configuration/>`_
- `Garage operations handbook <https://garagehq.deuxfleurs.fr/documentation/operations/>`_
