.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _prometheus_exporter__ref_guide_database:

Guide: database exporters (postgres, redis)
===========================================

Database exporters need credentials. Keep them out of world-readable files
by passing them via ``environment`` (rendered into a ``0600`` environment
file loaded by the systemd drop-in). When an exporter can read the password
only from its configuration file, see the ``config_mode``, ``config_group``
and ``config_no_log`` parameters in :ref:`prometheus_exporter__ref_exporters`.

PostgreSQL example. Create a least-privilege monitoring role with the
``pg_monitor`` built-in role (via :ref:`debops.postgresql`):

.. code-block:: yaml

   postgresql__roles:
     - name: 'prometheus_exporter'
       flags: [ 'LOGIN', 'INHERIT' ]
       password: '{{ lookup("password", secret + "/postgresql/prometheus_exporter_password chars=ascii_letters,digits length=32") }}'

   postgresql__groups:
     - roles: [ 'prometheus_exporter' ]
       groups: [ 'pg_monitor' ]
       database: 'postgres'

Then the exporter:

.. code-block:: yaml

   prometheus_exporter__group_exporters:

     - name: 'postgres'
       environment:

         - name: 'DATA_SOURCE_NAME'
           value: 'host=127.0.0.1 port=5432 user=prometheus_exporter password={{ lookup("password", secret + "/postgresql/prometheus_exporter_password chars=ascii_letters,digits length=32") }} dbname=postgres sslmode=disable'

Redis example (password via environment). On a host managed by
:ref:`debops.redis_server`, use the password that role publishes in its
local facts, so that both always match:

.. code-block:: yaml

   prometheus_exporter__group_exporters:

     - name: 'redis'
       args: [ '--redis.addr=redis://127.0.0.1:6379' ]
       environment:

         - name: 'REDIS_PASSWORD'
           value: '{{ ansible_local.redis_server.password }}'
