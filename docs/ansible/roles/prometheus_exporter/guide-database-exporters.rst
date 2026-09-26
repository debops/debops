.. Copyright (C) 2026 Patryk Sciborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _prometheus_exporter__ref_guide_database:

Guide: database exporters (postgres, redis)
===========================================

Database exporters need credentials. Keep them out of world-readable files
by passing them via ``environment`` (rendered into the ``0600`` drop-in).

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
         DATA_SOURCE_NAME: 'host=127.0.0.1 port=5432 user=prometheus_exporter password={{ lookup("password", secret + "/postgresql/prometheus_exporter_password chars=ascii_letters,digits length=32") }} dbname=postgres sslmode=disable'

Redis example (password via environment):

.. code-block:: yaml

   prometheus_exporter__group_exporters:
     - name: 'redis'
       args: [ '--redis.addr=redis://127.0.0.1:6379' ]
       environment:
         REDIS_PASSWORD: '{{ lookup("password", secret + "/redis/exporter_password") }}'
