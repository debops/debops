Getting started
===============

.. contents::
   :local:


Default configuration
---------------------

At the initial deployment, the role will disable the default Redis Sentinel instance
configuration defined by the distribution packages. Next, a new,
:command:`systemd`-based instance will be created with the configuration like
TCP ports and UNIX socket the same as the default Redis Sentinel setup. This
should allow easy creation of additional Redis Sentinel instances when necessary.

Keep in mind that once the :file:`sentinel.conf` configuration file is
generated, the role will not modify it. You should design the required Redis
Sentinel setup in a development environment, and then deploy it in production.
To reconfigure an instance from scratch, you can remove it by setting its state
to ``absent``, and then re-create it again.


Access control and autorization
-------------------------------

The :ref:`debops.redis_server` role configures Redis Server instances with
a randomly generated password, the same for all instances in the same domain.
The password is stored in the :file:`secret/` directory on the Ansible
Controller (see :ref:`debops.secret` role for details).

The :ref:`debops.redis_sentinel` role will use the same password retrieved from
the :file:`secret/` directory for the monitor configuration.

Redis password is also exposed in the Ansible local facts, so that other
Ansible roles can use it to configure access to Redis by other applications.
Run the :file:`/etc/ansible/facts.d/redis_sentinel.fact` script on the remote
host to see the local fact structure and contents.


Example inventory
-----------------

To enable Redis Sentinel configuration on a host, it needs to be added to
a specific Ansible inventory group:

.. code-block:: none

   [debops_service_redis_sentinel]
   hostname

By default Redis listens only for local connections on the ``loopback`` network
interface. If you want to set up a cluster of Redis instances on different
hosts that talk to each other, you should configure the default instance to
bind to all network interfaces, as well as open the TCP ports in the firewall:

.. code-block:: yaml

   # Listen to TCP connections on all interfaces
   redis_sentinel__bind: [ '0.0.0.0', '::' ]

   # Allow connections to Redis from specific subnets
   redis_sentinel__allow: [ '192.0.2.0/24', '2001:db8::/32' ]

You should also tell the default monitor to use the public IP address of a host
instead of ``localhost``, this address is shared between Sentinel instances
- you should ensure that each instance sees has the same "view" of the Redis
cluster:

.. code-block:: yaml

   redis_sentinel__monitors:
     - name: 'redis-ha'
       host: '{{ ansible_fqdn }}'


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.redis_sentinel`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/redis_sentinel.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::redis_sentinel``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.redis_sentinel`` Ansible
role:

- Official `Redis Sentinel documentation <https://redis.io/topics/sentinel>`__
- Example `Redis Sentinel config file <http://download.redis.io/redis-stable/sentinel.conf>`__
