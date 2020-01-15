Getting started
===============

.. contents::
   :local:


Default configuration
---------------------

At the initial deployment, the role will disable the default Redis instance
configuration defined by the distribution packages. Next, a new,
:command:`systemd`-based instance will be created with the configuration like
TCP ports and UNIX socket the same as the default Redis Server setup. This
should allow easy creation of additional Redis instances when necessary.


Access control and autorization
-------------------------------

The :ref:`debops.redis_server` role configures Redis Server instances with
a randomly generated password, the same for all instances in the same domain.
The password is stored in the :file:`secret/` directory on the Ansible
Controller (see :ref:`debops.secret` role for details).

The Redis password can be accessed on the Redis hosts using the
:command:`redis-password` script. Only the users that have read access to the
:file:`redis.conf` configuration files will be able to use it; the role sets up
an auxiliary ``redis-auth`` UNIX system group to allow members of this group
access to the configuration. The script accepts an instance name as an
argument; if not specified the ``main`` instance will be checked and the
password will be retrieved from the configuration file.

To access the default Redis Server instance via the :command:`redis-cli`
interface, you can use the command:

.. code-block:: console

   redis-cli -a $(redis-password)

Redis password is also exposed in the Ansible local facts, so that other
Ansible roles can use it to configure access to Redis by other applications.
Run the :file:`/etc/ansible/facts.d/redis_server.fact` script on the remote
host to see the local fact structure and contents.


Example inventory
-----------------

To enable Redis Server configuration on a host, it needs to be added to
a specific Ansible inventory group:

.. code-block:: none

   [debops_service_redis_server]
   hostname

By default Redis listens only for local connections on the ``loopback`` network
interface. If you want to set up a cluster of Redis instances on different
hosts that talk to each other, you should configure the default instance to
bind to all network interfaces, as well as open the TCP ports in the firewall:

.. code-block:: yaml

   # Listen to TCP connections on all interfaces
   redis_server__bind: [ '0.0.0.0', '::' ]

   # Allow connections to Redis from specific subnets
   redis_server__allow: [ '192.0.2.0/24', '2001:db8::/32' ]


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.redis_server`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/redis_server.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::redis_server``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.redis_server`` Ansible
role:

- Official `Redis documentation <https://redis.io/documentation>`__
- `Redis configuration file format <https://redis.io/topics/config>`__
