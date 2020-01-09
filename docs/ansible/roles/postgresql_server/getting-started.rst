Getting started
===============

.. contents::
   :local:

General configuration
---------------------

On a new host, PostgreSQL server will be configured with a default cluster
``main`` running on port ``5432``. Cluster will only listen to connections from
``localhost``, Ansible management account and ``root`` account will be able to
login to the PostgreSQL server using ``postgres`` role, for example:

.. code-block:: console

   user@host:~$ psql -U postgres

The PostgreSQL version installed by the role will be a default version offered
by the distribution. If you want PostgreSQL 9.4 on Debian Wheezy, or an
upstream version of the server, you can enable the upstream APT repository by
adding in inventory:

.. code-block:: yaml

   postgresql_server__upstream: True

Check :ref:`postgresql_server__ref_preferred_version` to learn more about
selecting custom PostgreSQL versions.

After installation you can use :ref:`debops.postgresql` role to configure
PostgreSQL roles and databases.

Remote access to the database
-----------------------------

PostgreSQL server listens only for connections on ``localhost`` by default. To
enable remote access, you need to change the
:envvar:`postgresql_server__listen_addresses` list to specify either IP addresses of
the interfaces you want your host to listen on or ``*`` for all interfaces.
Because firewall by default blocks all connections to PostgreSQL server, you
will also need to specify IP addresses or CIDR subnets which should be able to
connect to the clusters. Example configuration of variables in inventory:

.. code-block:: yaml

   postgresql_server__listen_addresses: [ '*' ]
   postgresql_server__allow: [ '192.0.2.0/24', '2001:db8::/32' ]

Default set of Host-Based Authentication rules permit connections from remote
hosts that are in the same subnet as the server, only over SSL, and require the
correct password to be provided to accept connections. If you want to allow
connections from other subnets than the server, you will need to add your own
HBA entries to the PostgreSQL cluster configuration. Example for the default
cluster:

.. code-block:: yaml

   postgresql_server__cluster_main:
     name: 'main'
     port: '5432'

     hba:
       - type: 'hostssl'
         database: 'samerole'
         user: 'all'
         address: [ '192.0.2.0/24', '2001:db8::/32' ]
         method: 'md5'

The ``debops.postgresql_server`` role is designed to use the PKI infrastructure
managed by :ref:`debops.pki` role. See its documentation for more details.

Example inventory
-----------------

To install and configure PostgreSQL server on a host, you need to add the host
to the ``[debops_service_postgresql_server]`` Ansible host group::

    [debops_service_postgresql_server]
    hostname

Example playbook
----------------

Here's an example playbook which uses the ``debops.postgresql_server`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/postgresql_server.yml
   :language: yaml

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after the host is first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::postgresql_server``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::postgresql_server:packages``
  Run tasks related to package installation

``role::postgresql_server:config``
  Run tasks related to PostgreSQL Server configuration.

``role::postgresql_server:auto_backup``
  Run tasks that configure AutoPostgreSQLBackup scripts.
