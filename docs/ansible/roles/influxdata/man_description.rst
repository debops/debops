Description
===========

The ``debops.influxdata`` Ansible role can be used to configure APT
repositories maintained by the `InfluxData <https://www.influxdata.com/about/>`_
company on Debian and Ubuntu hosts. The APT repositories are used to distribute
``influxdb``, ``telegraf``, ``chronograf`` and ``kapacitor`` APT packages.
The role allows only for installation of packages, additional configuration
and management of the installed software is performed by other Ansible roles.
