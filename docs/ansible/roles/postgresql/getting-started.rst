.. Copyright (C) 2015-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:

``debops.postgresql`` role is only the *client* part. For a working PostgreSQL
installation, ``debops.postgresql_server`` also needs to run somewhere.
It can be either on the same host, or on a separate one.

See the :ref:`debops.postgresql_server` documentation to learn how to install
the database server itself.

The PostgreSQL version installed by the role will be a default version offered
by the distribution. If you want PostgreSQL 9.4 on Debian Wheezy, or an
upstream version of the server, you can enable the upstream APT repository by
adding in inventory:

.. code-block:: yaml

   postgresql__upstream: True

Check :ref:`postgresql__ref_preferred_version` to learn more about
selecting custom PostgreSQL versions.

Server configuration
--------------------

The role supports different modes of operation, depending on the presence of a
PostgreSQL server installed locally or not.

Local database server
~~~~~~~~~~~~~~~~~~~~~

If the database server is installed locally, it will be automatically detected
and used by the ``debops.postgresql`` role without any additional
configuration.

If a remote server was used previously, and then a local one was installed,
it will automatically override the remote configuration.
You might need to recreate the databases and user accounts in that case.

Remote database server
~~~~~~~~~~~~~~~~~~~~~~

If your PostgreSQL server is configured on a remote host and
``debops.postgresql`` does not detect a local installation, it won't manage
databases or user accounts without a server specified.

To point it to a server, you need to set a variable in the inventory:

    postgresql__server: 'db.example.org'

This needs to be a FQDN address or an IP address of a host with the PostgreSQL
server installed. This host will be accessed by Ansible using task delegation,
so it needs to be accessible and managed by Ansible. Currently the role only
supports one server at a time.

If you use :ref:`debops.pki` to manage SSL certificates and you configured
PostgreSQL server with them, remote connections to the database will be
automatically encrypted. The default server configuration requires remote
connections to be done over SSL, otherwise the connection is dropped.

Example inventory
-----------------

To enable PostgreSQL client support on a host, you need to add that host to
``[debops_service_postgresql]`` Ansible group:

    [debops_service_postgresql]
    hostname

When PostgreSQL server is properly configured, or installed locally, you can
create user accounts and databases using inventory variables:

.. code-block:: yaml

   postgresql__roles:

     - name: 'application'

     - name: 'application_production'
       flags: [ 'NOLOGIN' ]

   postgresql__databases:

     - database: 'application_production'
       owner:    'application_production'

   postgresql__groups:

     - roles:  [ 'application' ]
       groups: [ 'application_production' ]
       database: 'application_production'

   postgresql__pgpass:

     - owner: 'application'

The above set of variables will create the PostgreSQL roles ``application`` and
``application_production``, which is meant to manage the database and cannot
directly be logged into.

The ``application_production`` PostgreSQL database will be created on the server
and the ``application_production`` role will be its owner.

The ``application`` role will be granted access to the
``application_production`` role and all of its objects.

Next, Ansible will ensure that the local system group and user account
``application`` exists, and will create ``~/.pgpass`` with PostgreSQL user and
password stored for easier access.


Example playbook
----------------

Here's an example Ansible playbook that uses the ``debops.postgresql`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/postgresql.yml
   :language: yaml
   :lines: 1,5-

Local Ansible facts, custom tasks
---------------------------------

Role creates a set of local Ansible facts which can be used by other roles to
create database management tasks that work both with local and remote
PostgreSQL servers. These facts are:

- ``ansible_local.postgresql.delegate_to``

- ``ansible_local.postgresql.server``

- ``ansible_local.postgresql.port``

- ``ansible_local.postgresql.user``

- ``ansible_local.postgresql.version``

These variables can be used in Ansible tasks to provide correct values pointing
to the correct PostgreSQL server. An example set of tasks to create a role and
database:

.. code-block:: yaml

   - name: Create database role
     postgresql_user:
       name: '{{ application_database_user }}'
       password: '{{ application_database_password }}'
       state: 'present'
     delegate_to: '{{ ansible_local.postgresql.delegate_to }}'

   - name: Create application database
     postgresql_db:
       name: '{{ application_database_name }}'
       owner: '{{ application_database_user }}'
       state: 'present'
     delegate_to: '{{ ansible_local.postgresql.delegate_to }}'
     register: application_register_database
