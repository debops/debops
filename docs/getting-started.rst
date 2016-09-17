Getting started
===============

.. contents:: Sections
   :local:


Default configuration of the Redis cluster
------------------------------------------

The ``debops.redis`` role can work either in the standalone mode (each host has
its own Redis Server instance) or in a clustered mode (all hosts in the
inventory group work together in a cluster). At the moment switching between
these modes after Redis is configured is not supported, therefore the choice
should be made before deployment. The separate Redis instances can be later
reconfigured to join a cluster, but the role does not provide any support for that
beyond the initial deployment.

The role can be used to deploy multiple Redis clusters in the same environment,
however this requires careful management of the Ansible inventory.

Standalone operation
~~~~~~~~~~~~~~~~~~~~

By default, ``debops.redis`` manages each Redis Server instance as a separate
master server. Redis Sentinel is not enabled in this mode.

Clustered operation
~~~~~~~~~~~~~~~~~~~

The role can configure a Redis Server/Sentinel cluster on multiple hosts in the
``[debops_service_redis]`` inventory group. The first host in this group will be
the master server. The specific group of hosts is defined in the
:envvar:`redis__inventory_hosts` variable.

To enable the clustered operation, you can configure the relevant variables in
the :file:`inventory/group_vars/debops_service_redis/redis.yml` file:

.. code-block:: yaml

   redis__server_master_host: 'hostname.{{ ansible_domain }}'
   redis__server_bind: '0.0.0.0'
   redis__server_allow: [ '192.0.2.0/24' ]
   redis__sentinel_enabled: True
   redis__sentinel_bind: '0.0.0.0'
   redis__sentinel_allow: [ '192.0.2.0/24' ]

This will configure the Redis Server and Sentinel to listen on all available
interfaces and accept connections from local network. Keep in mind that Redis
communication is performed in plaintext, therefore you might want to create a
separate physical network for Redis communication, a VLAN, or use a VPN like
Tinc to keep the traffic encrypted.

The specified Redis Server master host should be the same as the first included
in the ``[debops_service_redis]`` group, otherwise deployment might not be
completed successfully.

.. FIXME: might not be completed successfully

Password authentication
-----------------------

The access to the Redis server is controlled by a password. Users in a specific
UNIX system group (by default ``redis-auth``) have access to the Redis Server
configuration files and can read the password or use the custom
``redis-password`` script to retrieve it in their own scripts.

All hosts on a given DNS domain share the same Redis password for ease of use
and easy failover. The Redis password is accessible through the Ansible local
facts as ``ansible_local.redis.password``.

To access the Redis instance via ``redis-cli`` command, you can invoke it like
this:

.. code-block:: console

   redis-cli -a "$(redis-password)"

You can disable the password authentication by setting the
:envvar:`redis__auth_password` to an empty string.

Use as a role dependency
------------------------

The ``debops.redis`` role can be used in other playbooks as a dependency to
install Redis automatically. However, configuration of the Redis Server or
Sentinel should be performed at the inventory level, and not through the role
dependent variables, to preserve idempotency.


Example inventory
-----------------

To enable Redis Server/Sentinel support on a host, it needs to be included in
the ``[debops_service_redis]`` Ansible inventory group:

.. code-block:: none

   [debops_service_redis]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.redis`` role:

.. literalinclude:: playbooks/redis.yml
   :language: yaml
