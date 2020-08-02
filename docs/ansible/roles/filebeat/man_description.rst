.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Filebeat`__, from `Elastic`__ is part of the Elastic Stack.
Filebeat can be used to parse and "ingest" logs from files,
syslog, and various other sources, parse them and send them off to
Elasticsearch, Logstash or other destinations.

The ``filebeat`` Ansible role configures Filebeat on Debian/Ubuntu hosts. The
software itself will be installed using the :ref:`debops.elastic_co` Ansible
role.

.. __: https://www.elastic.co/beats/filebeat
.. __: https://www.elastic.co/
