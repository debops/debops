.. Copyright (C) 2020 Pedro Luis Lopez <pedroluis.lopezsanchez@gmail.com>
.. Copyright (C) 2020 Innobyte Bechea Leonardo <https://www.innobyte.com/>
.. Copyright (C) 2020 Innobyte Alin Alexandru <https://www.innobyte.com/>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Default variable details
========================

Some of ``debops.influxdb`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _influxdb__databases:

influxdb__databases
-------------------

List of databases that should be present or absent on a given InfluxDB server.
Each database is defined as a YAML dict with the following keys:

``database`` or ``name``
  Required. Name of the database. Names of databases can contain any
  unicode character

``state``
  Optional. If value is ``present``, the database will be created; if ``absent``,
  the database will be removed. It is defaulted to ``present``.

``proxies``
  Optional. Defaults to ``{{ omit }}``. Dict of HTTP(S) proxy to use for Requests
  to connect to InfluxDB server. Overrides ``influxdb__proxies``.

``validate_certs``
  Optional, boolean. Defaults to ``True``. If set to ``False``, the SSL certificates
  will not be validated. This should only set to no used on personally controlled
  sites using self-signed certificates. Overrides ``influxdb__validate_certs``.

Examples
~~~~~~~~

Create databases, remove some of the existing ones:

.. code-block:: yaml

   influxdb__databases:

     - name: 'dbname'


.. _influxdb__retention_policies:

influxdb__retention_policies
----------------------------

List of retention policies that should be present on a given InfluxDB server database.
Each retention policy is defined as a YAML dict with the following keys:

``policy`` or ``name``
  Required. Name of the retention policy.

``database``
  Required. Name of the database. Names of databases can contain any
  unicode character

``duration``
   Required. Determines how long InfluxDB keeps the data. The ``duration`` is a
   duration literal or ``INF`` (infinite). The minimum duration for a retention
   policy is one hour and the maximum duration is INF.

``replication``
   Required. Determines how many independent copies of each point are stored in
   the cluster. If the replication factor is set to 2, each series is stored on
   2 separate nodes. If the replication factor is equal to the number of data
   nodes, data is replicated on each node in the cluster.

``default``
   Optional. Defaults to ``False``. Sets the new retention policy as the default
   retention policy for the database.

``proxies``
  Optional. Defaults to ``{{ omit }}``. Dict of HTTP(S) proxy to use for Requests
  to connect to InfluxDB server. Overrides ``influxdb__proxies``.

``validate_certs``
  Optional, boolean. Defaults to ``True``. If set to ``False``, the SSL certificates
  will not be validated. This should only set to no used on personally controlled
  sites using self-signed certificates. Overrides ``influxdb__validate_certs``.

Examples
~~~~~~~~

Create retention policies:

.. code-block:: yaml

   influxdb__retention_policies:

     - name: 'fourweeks'
       database: 'dbname'
       duration: '4w'
       replication: 1
       default: True


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
  will be removed. It is added in Ansible 2.8.

``admin``
  Optional. Whether the user should be in the admin role or not. Since Ansible 2.8,
  the role will also be updated. It is defaulted to ``no``.

``state``
  Optional. If value is ``present``, the database will be created; if ``absent``,
  the database will be removed. It is defaulted to ``present``.

``proxies``
  Optional. Defaults to ``{{ omit }}``. Dict of HTTP(S) proxy to use for Requests
  to connect to InfluxDB server. Overrides ``influxdb__proxies``.

``validate_certs``
  Optional, boolean. Defaults to ``True``. If set to ``False``, the SSL certificates
  will not be validated. This should only set to no used on personally controlled
  sites using self-signed certificates. Overrides ``influxdb__validate_certs``.

Examples
~~~~~~~~

Create an user

.. code-block:: yaml

  influxdb__users:
    - name: 'someuser'
      grants:
        - database: 'dbname'
          privilege: 'READ'
