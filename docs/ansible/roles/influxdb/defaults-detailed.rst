Default variable details
========================

Some of ``debops.influxdb`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _influxdb_database:

influxdb__databases
-------------------

List of databases that should be present or absent on a given InfluxDB server.
Each database is defined as a YAML dict with the following keys:

``database_name``
  Name of the database, required. Should be composed from alphanumeric
  characters and underscore (``_``) only. Max length: 16 for MySQL databases,
  80 for MariaDB databases.

``hostname``
  The hostname or IP address on which InfluxDB server is listening. Defaulted to ``influxdb__fqdn``.

``state``
  Optional. If value is ``present``, the database will be created; if ``absent``,
  the database will be removed. It is defaulted to ``present``.

Examples
~~~~~~~~

Create databases, remove some of the existing ones:

.. code-block:: yaml

   influxdb__databases:

     - database_name: 'dbname'


.. _influxdb_user:

influxdb__users
---------------

List of user accounts that should be present or absent on a given InfluxdDB
server. Each user account is defined as a dict with a set of keys and values.

User account parameters
~~~~~~~~~~~~~~~~~~~~~~~

``admin``
  Whether the user should be in the admin role or not. Since version 2.8, the role will also be updated. It is defaulted to ``no``.

``grants``
  Privileges to grant to this user. Takes a list of dicts containing the ``database`` and ``privilege`` keys.
  If this argument is not provided, the current grants will be left alone. If an empty list is provided, all grants for the user will be removed. It is added in 2.8.

``hostname``
  The hostname or IP address on which InfluxDB server is listening.
  Since Ansible 2.5, defaulted to ``localhost``.

``password``
  Password that will be used to authenticate against InfluxDB server.
  Alias ``login_password`` added in Ansible 2.5.

``state``
  Optional. If value is ``present``, the user will be created; if ``absent``,
  the user will be removed. It is defaulted to ``present``.

``user_name``
  Name of the user, required.

``user_password``
  Password to be set for the user.

``username``
  Username that will be used to authenticate against InfluxDB server.
  Alias ``login_username`` added in Ansible 2.5, defaulted to ``root``.

Examples
~~~~~~~~

Create an user on localhost using default login credentials

.. code-block:: yaml

   influxdb__users:
     - user_name: 'someuser'
       user_password: 'somepassword'

Create an user on remote host

.. code-block:: yaml

  influxdb__users:
    - user_name: 'someuser'
      user_password: 'somepassword'
      grants:
        - database: 'dbname'
          privilege: 'READ'

influxdb__default_configuration
-------------------------------

Controls how the HTTP endpoints are configured. These are the primary
mechanism for getting data into and out of InfluxDB.

.. code-block:: yaml

   influxdb__default_configuration:
   options:
     - bind-address: '":{{ influxdb__port }}"'
       https-enabled: '{{ "true" if influxdb__pki else "false" }}'
       auth-enabled: '{{ "true" if influxdb__auth_enabled else "false" }}'

Syntax
~~~~~~

The variables are YAML lists, each list entry is a YAML dictionary that uses
specific parameters:

``name``
    Required. This parameter defines the option name, and it needs to be unique in a given configuration file

  ``options``
      Optional. A YAML list of :command:`influxdb` configuration options defined in the configuration file.

      Each element of the options list is a YAML dictionary with specific parameters:

      ``auth-enabled``
        Determines whether user authentication is enabled over HTTP/HTTPS.

      ``bind-address``
        The bind address used by the HTTP service.

      ``https-certificate``
        The SSL certificate to use when HTTPS is enabled.

      ``https-private-key``
        Use a separate private key location.

      ``https-enabled``
        Determines whether HTTPS is enabled.

      ``dir``
        The directory where the TSM storage engine stores TSM files.

      ``wal-dir``
        The directory where the TSM storage engine stores WAL files.

      ``series-id-set-cache-size``
        The size of the internal cache used in the TSI index to store previously
        calculated series results. Cached results will be returned quickly from the
        cache rather than needing to be recalculated when a subsequent query with a
        matching tag key-value predicate is executed. Setting this value to ``0`` will
        disable the cache, which may lead to query performance issues. This value
        should only be increased if it is known that the set of regularly

Examples
~~~~~~~~

.. code-block:: yaml

  - name: 'global'
    options:
      - bind-address: '"127.0.0.1:{{ influxdb__port_rpc }}"'

  - name: 'meta'
    options:
      - dir: '"/var/lib/influxdb/meta"'

  - name: 'data'
    options:
      - dir: '"/var/lib/influxdb/data"'
        wal-dir: '"/var/lib/influxdb/wal"'
        series-id-set-cache-size: '100'

  - name: 'coordinator'
    options: []

  - name: 'retention'
    options: []

  - name: 'shard-precreation'
    options: []

  - name: 'monitor'
    options: []

  - name: 'http'
    options:
      - bind-address: '":{{ influxdb__port }}"'
        https-enabled: '{{ "true" if influxdb__pki else "false" }}'
        auth-enabled: '{{ "true" if influxdb__auth_enabled else "false" }}'

  - name: 'logging'
    options: []

  - name: 'subscriber'
    options: []

  - name: 'graphite'
    options: []

  - name: 'collectd'
    options: []

  - name: 'opentsdb'
    options: []

  - name: 'udp'
    options: []

  - name: 'continuous_queries'
    options: []

  - name: 'tls'
    options: []
