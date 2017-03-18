Remote database
===============

Postgresql
----------

If you would like to use remote database you need to allow remote connection on the server:

postgresql_server_listen_addresses: [ '*' ]
postgresql_server_allow: [ '10.0.0.0/24' ]

You also have tell GitLab role to use Postgres and connect to remote host:

gitlab__database: 'postgresql'
postgresql_server: 'fqdn.of.postgres.server'

MariaDB/MySQL
-------------

TBD

