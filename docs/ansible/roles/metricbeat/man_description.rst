.. Copyright (C) 2022 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Metricbeat`__, from `Elastic`__ is part of the Elastic Stack.  Metricbeat can
be used to gather various metrics (CPU usage, disk I/O, application status,
etc.) from host and services and send them to Elasticsearch database for
processing.

The ``metricbeat`` Ansible role configures Metricbeat on Debian/Ubuntu hosts.
The software itself will be installed using the :ref:`debops.extrepo`
Ansible role.

.. __: https://www.elastic.co/beats/metricbeat
.. __: https://www.elastic.co/
