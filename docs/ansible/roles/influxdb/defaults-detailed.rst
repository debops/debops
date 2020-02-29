Default variable details
========================

Some of ``debops.influxdb`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _influxdb__databases:

influxdb__databases
-------------------

List of databases that should be present or absent on a given InfluxDB server.
Each database is defined as a YAML dict with the following keys:

``database`` or ``name``
  Required. Name of the database, required. Names of databases can contain any
  unicode character

``state``
  Optional. If value is ``present``, the database will be created; if ``absent``,
  the database will be removed. It is defaulted to ``present``.

Examples
~~~~~~~~

Create databases, remove some of the existing ones:

.. code-block:: yaml

   influxdb__databases:

     - name: 'dbname'


.. _influxdb__users:

influxdb__users
---------------

List of user accounts that should be present or absent on a given InfluxdDB
server. Each user account is defined as a dict with a set of keys and values.

User account parameters
~~~~~~~~~~~~~~~~~~~~~~~

``user`` or ``name``
  Required. Name of the user.

``password``
  Optional. If specified, the role will set it as the password for the InfluxDB
  account. If not present, a random password will be generated automatically
  and stored in the ``secret/`` directory on the Ansible Controller. Refer to the
  :ref:`debops.secret` role for more details.

``grants``
  Optional. Privileges to grant to this user. Takes a list of dicts containing the
  ``database`` and ``privilege`` keys. If this argument is not provided, the current
  grants will be left alone. If an empty list is provided, all grants for the user
  will be removed. It is added in 2.8.

``admin``
  Optional. Whether the user should be in the admin role or not. Since version 2.8,
  the role will also be updated. It is defaulted to ``no``.

``state``
  Optional. If value is ``present``, the database will be created; if ``absent``,
  the database will be removed. It is defaulted to ``present``.

Examples
~~~~~~~~

Create an user

.. code-block:: yaml

  influxdb__users:
    - name: 'someuser'
      grants:
        - database: 'dbname'
          privilege: 'READ'
