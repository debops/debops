Getting started
===============

.. contents::
   :local:

Example inventory
-----------------

To install MariaDB on a host, you need to add it to
``[debops_service_mariadb_server]`` Ansible group:

.. code-block:: none

   [debops_service_mariadb_server]
   database-host

This will install ``mariadb-server`` package, configure the server to listen on
``localhost`` for new connections, and install :program:`automysqlbackup` script to
automatically create daily, weekly and monthly backups of the database.

Example playbook
----------------

Here's an example Ansible playbook that uses the ``debops.mariadb_server``
role:

.. literalinclude:: ../../../../ansible/playbooks/service/mariadb_server.yml
   :language: yaml

Remote access to the database
-----------------------------

If you want to allow connections from remote hosts to the MariaDB server, you
need to change the bind address to listen on all network interfaces, and
specify the list of IP addresses or CIDR networks which can connect to the
daemon:

.. code-block:: yaml

   mariadb_server__bind_address: '::'
   mariadb_server__allow: [ '192.0.2.0/24', '2001:db8:3232::/64' ]

Changing the bind address will require the MariaDB daemon to be restarted,
however ``debops.mariadb_server`` does not do that automatically to avoid
disrupting the normal server operations. To restart the service, you can run
this Ansible command:

.. code-block:: console

   user@host:~$ ansible database-host -s -m service -a 'name=mysql state=restarted'

Note the :command:`mysql` service name - MariaDB still uses the old MySQL init files,
configuration and data paths to allow easy compatibility with old MySQL
installations.

Database and user management
----------------------------

``debops.mariadb_server`` is not meant to be used to manage databases and user
accounts. You should use :ref:`debops.mariadb` role instead, which was designed
specifically for this purpose.
