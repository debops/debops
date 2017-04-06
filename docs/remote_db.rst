How to use remote SQL database
==============================

.. include:: includes/all.rst

PostgreSQL
----------

If you would like to use the remote PostgreSQL database, on the server side you
need to allow remote connections from the GitLab host. This can be done using
the Ansible inventory variables:

.. code-block:: yaml

   postgresql_server__listen_addresses: [ '*' ]
   postgresql_server__allow: [ '192.0.2.0/24' ]

On the GitLab host, you need to enable the debops.postgresql_ role by adding
the host to its respective Ansible inventory group:

.. code-block:: none

   [debops_service_postgresql]
   hostname

The PostgreSQL client role also needs to be pointed to the remote database
server, it can be done using the Ansible inventory variables:

.. code-block:: yaml

   postgresql__server: 'sqldb.example.org'

The ``debops.gitlab`` role should detect the PostgreSQL configuration
automatically. If not, you can force the use of the PostgreSQL server through
the Ansible inventory:

.. code-block:: yaml

   gitlab__database: 'postgresql'


MariaDB/MySQL
-------------

If you would like to use the remote MariaDB or MySQL database, on the server
side you need to allow remote connections from the GitLab host. This can be
done using the Ansible inventory variables:

.. code-block:: yaml

   mariadb_server__bind_address: '0.0.0.0'
   mariadb_server__allow: [ '192.0.2.0/24' ]

On the GitLab host, you need to enable the debops.mariadb_ role by adding
the host to its respective Ansible inventory group:

.. code-block:: none

   [debops_service_mariadb]
   hostname

The MariaDB client role also needs to be pointed to the remote database server,
it can be done using the Ansible inventory variables:

.. code-block:: yaml

   mariadb__server: 'sqldb.example.org'

The ``debops.gitlab`` role should detect the MariaDB configuration
automatically. If not, or if the PostgreSQL client is also configured on the
GitLab host, you can force the use of the MariaDB server through the Ansible
inventory:

.. code-block:: yaml

   gitlab__database: 'mariadb'
