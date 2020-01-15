Getting started
===============

.. contents::
   :local:

``debops.mariadb`` role is only the "client" part. To have working a
MariaDB/MySQL installation, you also need to setup ``debops.mariadb_server``
role somewhere. It can be either on the same host, or on a separate host.
See the ``debops.mariadb_server`` documentation to learn how to install the
database server itself.

Server configuration
--------------------

The role supports different modes of operation, depending on the presence of a
MariaDB or MySQL server installed locally or not, or presence of a tunneled
connection to a remote server.

Local database server
~~~~~~~~~~~~~~~~~~~~~

If the database server is installed locally, it will be automatically detected
and used by the ``debops.mariadb`` role without any additional configuration. Also,
if a remote server was used previously, and a local one was installed, it will
automatically override the remote configuration. You might need to recreate the
databases and user accounts in that case.

Remote database server
~~~~~~~~~~~~~~~~~~~~~~

If your MariaDB server is configured on a remote host and you don't have
a local installation, ``debops.mariadb`` will detect that and won't manage the
databases/user accounts without a server specified. To point it to a server,
you need to set a variable in the inventory:

.. code-block:: yaml

   mariadb__server: 'db.example.org'

This needs to be a FQDN address or an IP address of a host with MariaDB server
installed. This host will be accessed by Ansible using task delegation, so it
needs to be accessible and managed by Ansible. Currently only 1 server at
a time is supported by the role.

If :ref:`debops.pki` role is used to configure a PKI environment, with default
``domain`` PKI realm enabled, role will configure the provided private keys and
X.509 certificates to enable SSL connections to the database by default.
Support for client-side X.509 authentication will depend on a given user having
access to the PKI private keys - see the documentation of :ref:`debops.pki` role
for more details.

If the PKI environment is not configured or disabled, connections to the
database server will be performed in cleartext, so you might want to consider
securing them by configuring server on a separate internal network, or
accessing it over a VPN connection. You can use ``debops.subnetwork``,
:ref:`debops.tinc` and :ref:`debops.dnsmasq` Ansible roles to set up a VPN internal
network to secure communication between hosts.

Remote database server over a SSL tunnel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If local MariaDB installation is not detected, but port ``3306`` is active and
awaiting connections, ``debops.mariadb`` role assumes that MariaDB server is
accessible over a VPN connection. In this case you need to specify the remote
host in inventory for Ansible to delegate its tasks:

.. code-block:: yaml

   mariadb__server: 'db.example.org'

User accounts will automatically be configured with ``localhost`` as the "host"
part of the account.

If you want to use tunneled connection to a MariaDB server, you can use
:ref:`debops.stunnel` Ansible role to configure a SSL tunnel, although it might be
more complex than using a VPN network.

Example inventory
-----------------

To enable MariaDB client support on a host, you need to add that host to
``[debops_service_mariadb]`` Ansible group:

.. code-block:: none

   [debops_service_mariadb]
   hostname

When MariaDB server is properly configured, or installed locally, you can
create user accounts and databases using inventory variables:

.. code-block:: yaml

   mariadb__databases:

     - name: 'application_production'

   mariadb__users:

     - name: 'application'
       owner: 'application'

Above set of variables will create local system UNIX account ``application`` if
it doesn't already exist, with a supplementary UNIX group of the same name,
grant all privileges to ``application.*`` and ``application\_%.*`` databases,
create a ``~/.my.cnf`` configuration file with database credentials and
finally, create a database ``application_production`` on the database server.

Example playbook
----------------

Here's an example Ansible playbook that uses the ``debops.mariadb`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/mariadb.yml
   :language: yaml

Usage as a role dependency
--------------------------

``debops.mariadb`` role can be used by another Ansible role as a dependency.
The easiest way to do so is to have a separate set of variables for an user
account, group, home directory, and MariaDB user. ``debops.mariadb`` will the
create MariaDB user account, as wall as local UNIX account with
a ``~/.my.cnf`` configuration file as needed.

Database creation is best left for the application role, since then you can use
the state change to perform other actions, like importing or initializing the
database. See the next section for details.

Example usage as a role dependency:

.. code-block:: yaml

   dependencies:

     - role: debops.mariadb
       mariadb__dependent_users:

         - user: '{{ application__database_user }}'
           database: '{{ application__database_name }}'
           owner: '{{ application__user }}'
           group: '{{ application__group }}'
           home: '{{ application__home }}'
           system: True
           priv_aux: False

Password to the database user account can either be retrieved directly from the
``secret/`` directory by the application role using :ref:`debops.secret` role, or
set by the application role and provided as:

.. code-block:: yaml

   mariadb__dependent_users:

     - user: '{{ application__database_user }}'
       password: '{{ application__database_password }}'

In that case it's best to use :ref:`debops.secret` role to store the password
securely in a separate directory.

Local Ansible facts, custom tasks
---------------------------------

Role creates a set of local Ansible facts which can be used by other roles to
create database management tasks that work both with local and remote MariaDB
servers. These facts are:

- ``ansible_local.mariadb.client``

- ``ansible_local.mariadb.delegate_to``

- ``ansible_local.mariadb.host``

- ``ansible_local.mariadb.port``

- ``ansible_local.mariadb.server``

These variables can be used in Ansible tasks to provide correct values pointing
to the correct MariaDB server. An example set of tasks to create user account
and database:

.. code-block:: yaml

   - name: Create database user
     mysql_user:
       name: '{{ application__database_user }}'
       host: '{{ ansible_local.mariadb.host }}'
       password: '{{ application__database_password }}'
       priv: '{{ application__database_name }}.*:ALL'
       state: 'present'
     delegate_to: '{{ ansible_local.mariadb.delegate_to }}'

   - name: Create application database
     mysql_db:
       name: '{{ application__database_name }}'
       state: 'present'
     delegate_to: '{{ ansible_local.mariadb.delegate_to }}'
     register: application__register_database
