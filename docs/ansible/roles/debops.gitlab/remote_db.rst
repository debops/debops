How to use remote SQL database
==============================

PostgreSQL
----------

If you would like to use the remote PostgreSQL database, on the server side you
need to allow remote connections from the GitLab host. This can be done using
the Ansible inventory variables:

.. code-block:: yaml

   postgresql_server__listen_addresses: [ '*' ]
   postgresql_server__allow: [ '192.0.2.0/24' ]

On the GitLab host, you need to enable the :ref:`debops.postgresql` role by adding
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

MariaDB / MySQL databases are not supported anymore. GitLab's developers
themselves discourage their use: https://docs.gitlab.com/ce/install/requirements.html#database.
