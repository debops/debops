.. _debops.influxdb_server:

debops.influxdb_server
======================

InfluxDB__ is an open-source time series database (TSDB) developed by InfluxData.
It is written in Go and optimized for fast, high-availability storage and
retrieval of time series data in fields such as operations monitoring,
application metrics, Internet of Things sensor data, and real-time analytics.
Ansible roles ``debops.influxdb`` and ``debops.influxdb_server`` allow
you to manage a InfluxDB server and / or access it remotely from other hosts.

``debops.influxdb_server`` role is the "server" part - it installs
``influxdb`` Debian package, and configures access to the database from
``root`` admin account. After that, you can use :ref:`debops.influxdb` role to
manage databases and user accounts on the server.

.. __: https://en.wikipedia.org/wiki/InfluxDB

.. toctree::
   :maxdepth: 2

   getting-started
   defaults-detailed
   defaults/main

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/influxdb_server/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
