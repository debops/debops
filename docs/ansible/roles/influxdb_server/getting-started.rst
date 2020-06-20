.. Copyright (C) 2020 Pedro Luis Lopez <pedroluis.lopezsanchez@gmail.com>
.. Copyright (C) 2020 Innobyte Bechea Leonardo <https://www.innobyte.com/>
.. Copyright (C) 2020 Innobyte Alin Alexandru <https://www.innobyte.com/>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Getting started
===============

.. only:: html

   .. contents::
      :local:

Example inventory
-----------------

To install InfluxDB on a host, you need to add it to
``[debops_service_influxdb_server]`` Ansible group:

.. code-block:: none

   [debops_service_influxdb_server]
   database-host

This will install ``influxdb`` package, configure the server to listen on
all interfaces for new connections, and install :program:`autoinfluxdbbackup` script to
automatically create daily, weekly and monthly backups of the database.

Example playbook
----------------

Here's an example Ansible playbook that uses the ``debops.influxdb_server``
role:

.. literalinclude:: ../../../../ansible/playbooks/service/influxdb_server.yml
   :language: yaml
   :lines: 1,7-

Remote access to the database
-----------------------------

If you want to allow connections from remote hosts to the InfluxDB server, you
need specify the list of IP addresses or CIDR networks which can connect to the
daemon:

.. code-block:: yaml

   influxdb_server__allow: [ '192.0.2.0/24', '2001:db8:3232::/64' ]

Database and user management
----------------------------

``debops.influxdb_server`` is not meant to be used to manage databases and user
accounts. You should use :ref:`debops.influxdb` role instead, which was designed
specifically for this purpose.
