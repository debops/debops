.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _vmagent__ref_guide_victoriametrics:

Guide: VictoriaMetrics integration
==================================

.. only:: html

   .. contents::
      :local:


Overview
--------

This guide describes the most common pattern for ``debops.vmagent``: one
vmagent instance per managed host, scraping local Prometheus-compatible
exporters and remote-writing the resulting samples to a central
VictoriaMetrics single-node instance. The same role can also be used as
an aggregator scraping many remote targets, or as a fan-out point
duplicating writes to multiple VictoriaMetrics clusters.

.. code-block:: text

    +---------------------+      +---------------------+
    | host: app01         |      | host: app02         |
    |                     |      |                     |
    | node_exporter:9100  |      | node_exporter:9100  |
    |          |          |      |          |          |
    |          v          |      |          v          |
    | vmagent@default     |      | vmagent@default     |
    +----------+----------+      +----------+----------+
               |                            |
               |       remoteWrite (HTTPS)  |
               +-------------+--------------+
                             v
              +----------------------------+
              | vmetrics.example.org:8428  |
              | (VictoriaMetrics)          |
              +----------------------------+


Server-side prerequisites
-------------------------

This role does **not** install or configure the VictoriaMetrics server
itself. Bring up the server first - either as a native binary, as a
container managed by :ref:`debops.docker_service`, or via any other
mechanism - and make sure that its remote-write endpoint
(``http://<host>:8428/api/v1/write``) is reachable from every host that
will run vmagent.


Default host: scrape local node_exporter, write to central VM
-------------------------------------------------------------

In ``group_vars/all/vmagent.yml``:

.. code-block:: yaml

   vmagent__default_remote_write_urls:
     - 'https://vmetrics.example.org/api/v1/write'

   vmagent__default_scrape_configs:
     - job_name: 'node'
       static_configs:
         - targets: [ '127.0.0.1:9100' ]

This creates a single ``vmagent@default.service`` on every host with the
following effective command line::

   /usr/local/bin/vmagent \
       -promscrape.config=/etc/vmagent/default.yml \
       -remoteWrite.tmpDataPath=/var/lib/vmagent/default \
       -remoteWrite.url=https://vmetrics.example.org/api/v1/write \
       -httpListenAddr=127.0.0.1:8429 \
       -loggerLevel=INFO \
       -loggerFormat=default \
       -remoteWrite.maxDiskUsagePerURL=1GB


Self-monitoring on the VictoriaMetrics host
-------------------------------------------

When vmagent runs on the same host as VictoriaMetrics, point it at
``localhost`` to skip the reverse proxy round-trip. In
``host_vars/vmetrics.example.org/vmagent.yml``:

.. code-block:: yaml

   vmagent__remote_write_urls:
     - 'http://localhost:8428/api/v1/write'


Authenticated remote write
--------------------------

When the VictoriaMetrics endpoint is behind an authenticated reverse
proxy (or fronted by ``vmauth``), define a per-host instance that uses a
bearer token sourced from the DebOps secret store. In
``host_vars/<host>/vmagent.yml``:

.. code-block:: yaml

   vmagent__host_instances:
     - name: 'default'
       remote_write_urls:
         - 'https://vmetrics.example.org/api/v1/write'
       bearer_token: True

Place the token at
``secret/vmagent/instances/default/bearer_token`` on the Ansible
Controller. The role will copy it into
:file:`/var/lib/vmagent/default/bearer_token` with mode ``0400`` and
pass ``-remoteWrite.bearerTokenFile=...`` to ``vmagent``.


Multi-target fan-out
--------------------

vmagent can write the same samples to multiple endpoints in parallel.
Add more entries to ``remote_write_urls``:

.. code-block:: yaml

   vmagent__instances:
     - name: 'default'
       remote_write_urls:
         - 'https://vmetrics-primary.example.org/api/v1/write'
         - 'https://vmetrics-backup.example.org/api/v1/write'


Aggregator pattern
------------------

For a host that scrapes remote targets (not just localhost), define an
instance with explicit static or service-discovery targets:

.. code-block:: yaml

   vmagent__instances:
     - name: 'aggregator'
       remote_write_urls:
         - 'https://vmetrics.example.org/api/v1/write'
       scrape_configs:
         - job_name: 'switches'
           static_configs:
             - targets:
                 - 'switch01.example.org:9116'
                 - 'switch02.example.org:9116'
         - job_name: 'blackbox'
           metrics_path: '/probe'
           params:
             module: [ 'http_2xx' ]
           static_configs:
             - targets: [ 'https://app01.example.org/health' ]
           relabel_configs:
             - source_labels: [ '__address__' ]
               target_label: '__param_target'
             - target_label: '__address__'
               replacement: '127.0.0.1:9115'

A second ``vmagent`` instance on the same host can keep collecting local
metrics independently - see :envvar:`vmagent__instances` for the
multi-instance pattern.
