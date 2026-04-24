.. Copyright (C) 2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Shared Erlang cookie
--------------------

The role configures the same Erlang cookie (password) on all hosts managed in
a given environment with an idea that all of the hosts are joined in the same
RabbitMQ cluster. If you want to do things differently, change the
:envvar:`rabbitmq_server__erlang_cookie_password` as needed.


Erlang 19.x from 'jessie-backports' on Debian Jessie
----------------------------------------------------

On Debian Jessie hosts, the role will configure an APT preference for
backported Erlang 19.x packages from Debian Stretch. They provide better
Elliptic Curve Cryptography (ECC) support and allow deactivation of TLS
client-initiated protocol renegotiation, which mitigates potential DoS attacks.


Encrypted client connections
----------------------------

The role will check if the :ref:`debops.pki` and :ref:`debops.dhparam` Ansible roles
configured their environment on a host, and will automatically enable or
disable support for encrypted AMQP connections. Plaintext connections will be
available if encryption is disabled.


RabbitMQ clustering
-------------------

By default the ``debops.rabbitmq_server`` role configures RabbitMQ service in
a standalone mode, without external access through the firewall. To allow for
clustering, you need to define IP addresses and/or CIDR subnets, which will be
allowed to connect to the ``epmd`` (Erlang Port Mapper Daemon) and ``einc``
(Erlang Inter-Process Communication) TCP ports. To do that, set the variable
below in the Ansible inventory:

.. code-block:: yaml

   ---
   # Allow for cluster communication
   rabbitmq_server__cluster_allow: [ '192.0.2.0/24' ]

After that, re-run the role to apply changes to the firewall configuration.

The role composes the RabbitMQ cluster automatically, see the
`Automatic cluster formation`_ section below. Opt out with
``rabbitmq_server__cluster_autojoin: False`` to fall back to the legacy
workflow where cluster membership is managed manually:

.. code-block:: console

   rabbitmqctl stop_app
   rabbitmqctl join_cluster rabbit@host1
   rabbitmqctl start_app

You can check the RabbitMQ cluster status by running the command:

.. code-block:: console

   rabbitmqctl cluster_status

See the `RabbitMQ Clustering Guide <https://www.rabbitmq.com/clustering.html>`_
for more details.


Rolling restart and cluster bootstrap
-------------------------------------

Starting with RabbitMQ 4.2 the broker uses Khepri (Raft) for metadata
storage by default (in 4.0 and 4.1 it is available as an opt-in feature
flag), which means that restarting a majority of cluster nodes
simultaneously causes a ``timeout_waiting_for_leader`` boot deadlock. To
prevent this, the service playbook uses ``serial: 1`` together with
``any_errors_fatal: true`` and ``max_fail_percentage: 0``, and runs a
post-task health check (``rabbitmqctl await_startup`` +
``cluster_status`` + ``assert`` that the current node is visible in
``running_nodes``). Nodes are restarted one at a time and the play stops
on the first failure.

On top of that, the ``Restart rabbitmq-server`` handler first calls
``rabbitmqctl stop_app`` (to avoid ``duplicate_node_name`` races with EPMD),
restarts the systemd unit and waits for ``rabbitmqctl await_startup`` to
return. The handler also carries ``throttle: 1`` as a second line of
defense in case the role is used outside of the service playbook.

Both invocation modes are supported out of the box:

- Running the playbook against the whole group at once::

      debops run service/rabbitmq_server

  ``serial: 1`` forces sequential processing, so nodes are configured and
  restarted one after another even if the inventory targets the whole
  cluster.

- Running the playbook per host via ``--limit`` (useful when the role is
  not configured to form the cluster automatically and each node needs
  a manual ``rabbitmqctl join_cluster`` in between)::

      debops run service/rabbitmq_server --limit host1
      debops run service/rabbitmq_server --limit host2
      debops run service/rabbitmq_server --limit host3

The post-task assertion only checks that the current node itself rejoined
the cluster, so it does not trip up either scenario; peer availability is
guaranteed by the sequential execution model.


Automatic cluster formation
---------------------------

The role can form and maintain a RabbitMQ cluster on its own, but the
feature is **opt-in** - ``rabbitmq_server__cluster_autojoin`` defaults to
``False`` so that upgrading the role on an existing deployment never
alters cluster membership on its own. In particular, several independent
single-node RabbitMQ instances that happen to share the
``debops_service_rabbitmq_server`` inventory group stay independent.
Enable auto-join explicitly on the inventory groups that should form a
cluster:

.. code-block:: yaml

   # group_vars/debops_service_rabbitmq_server/rabbitmq_server.yml
   rabbitmq_server__cluster_autojoin: True

When enabled, the role joins every non-seed node to the cluster after its
configuration has been applied and the ``Restart rabbitmq-server`` handler
has fired. The seed node is the first entry of
``rabbitmq_server__cluster_hosts``, which defaults to the
``debops_service_rabbitmq_server`` inventory group sorted alphabetically.
Override the seed explicitly by setting
``rabbitmq_server__cluster_seed_node`` (or by reordering
``rabbitmq_server__cluster_hosts``) in the inventory.

On every host the role runs ``rabbitmqctl cluster_status`` and checks whether
the seed node is already visible in ``running_nodes``. If it is, the task is
a no-op. Otherwise the role performs:

.. code-block:: console

   rabbitmqctl stop_app
   rabbitmqctl reset
   rabbitmqctl join_cluster rabbit@<seed>
   rabbitmqctl start_app

The reset step is guarded by an ``assert`` that the current node's
``disk_nodes`` list contains only itself. This prevents the role from
destroying state on a node that is already part of a different cluster; in
that case the play stops with a clear error message and requires manual
intervention (``rabbitmqctl forget_cluster_node`` / ``reset``) or an opt-out
via ``rabbitmq_server__cluster_autojoin: False``.

Combined with ``serial: 1`` in the ``service/rabbitmq_server.yml`` playbook,
this makes both invocation modes fully automatic:

- ``debops run service/rabbitmq_server`` against the whole group: the seed
  is configured first, then each subsequent host joins the now-running seed.
- ``debops run service/rabbitmq_server --limit hostN``: the role still
  identifies the seed via the inventory group and joins against it, provided
  the seed is already reachable.

Multiple independent clusters in one environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a single inventory manages several RabbitMQ clusters, split them
into dedicated inventory groups and point
``rabbitmq_server__cluster_hosts`` at the matching group in each
``group_vars`` subtree. See
:ref:`rabbitmq_server__ref_cluster_autojoin` in the defaults reference
for a full inventory layout example with two independent clusters.


Inter-node communication is not encrypted
-----------------------------------------

Erlang supports encrypting communication between nodes (processes on the same
or other hosts) using TLS, which RabbitMQ can use to
`secure traffic between hosts <https://www.rabbitmq.com/clustering-ssl.html>`_.
However one downside is that when inter-node traffic is encrypted,
`Erlang uses dynamic random ports <https://groups.google.com/forum/#!msg/rabbitmq-users/rJaJWctOYKQ/q5nP2Cb-5k0J>`_
for communication, which might interfere with the host's firewall. Therefore by
default ``debops.rabbitmq_server`` role does not configure encrypted inter-node
communication. You should consider alternative means of securing the traffic
between hosts, for example a separate VLAN or use of a VPN connection.


Example inventory
-----------------

To configure RabbitMQ on a host, it should be added to the
``[debops_service_rabbitmq_server]`` Ansible inventory group:

.. code-block:: none

   [debops_service_rabbitmq_server]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.rabbitmq_server`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/rabbitmq_server.yml
   :language: yaml
   :lines: 1,5-
