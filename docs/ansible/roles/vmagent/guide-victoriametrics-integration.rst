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

This guide describes the most common use of ``debops.vmagent``: one
:command:`vmagent` instance on each host, which scrapes local
Prometheus-compatible exporters and sends the samples to a central
VictoriaMetrics server. The same role can be used for an instance which
scrapes many remote targets, or which sends the samples to several
VictoriaMetrics servers.

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
               |       remote write (HTTPS) |
               +-------------+--------------+
                             v
              +----------------------------+
              | vmetrics.example.org       |
              | (VictoriaMetrics)          |
              +----------------------------+


Server-side prerequisites
-------------------------

This role does not install the VictoriaMetrics server. Install it first, for
example as a container managed by the :ref:`debops.docker_compose_service`
role, and make sure that its remote write endpoint
(``http://<host>:8428/api/v1/write`` on a single-node server) is reachable from
the hosts which run :command:`vmagent`.


Scrape local exporters on each host
-----------------------------------

In the :file:`group_vars/all/vmagent.yml` file:

.. code-block:: yaml

   vmagent__remote_write_urls:
     - 'https://vmetrics.example.org/api/v1/write'

   vmagent__scrape_configs:
     - job_name: 'node'
       static_configs:
         - targets: [ '127.0.0.1:9100' ]

This creates the ``vmagent@default.service`` instance on each host, started
with the following command line:

.. code-block:: none

   /usr/local/bin/vmagent \
       -promscrape.config=/etc/vmagent/default.yml \
       -remoteWrite.tmpDataPath=/var/lib/vmagent/default \
       -remoteWrite.url=https://vmetrics.example.org/api/v1/write \
       -httpListenAddr=127.0.0.1:8429 \
       -remoteWrite.maxDiskUsagePerURL=1GB

Exporters present only on some hosts can be added in the group or host
variables, without repeating the jobs defined for all hosts:

.. code-block:: yaml

   # host_vars/db01.example.org/vmagent.yml
   vmagent__host_scrape_configs:
     - job_name: 'postgres'
       static_configs:
         - targets: [ '127.0.0.1:9187' ]


Monitoring the VictoriaMetrics host
-----------------------------------

When :command:`vmagent` runs on the same host as VictoriaMetrics, it can send
the samples directly to the local port and skip the reverse proxy. In the
:file:`host_vars/vmetrics.example.org/vmagent.yml` file:

.. code-block:: yaml

   vmagent__remote_write_urls:
     - 'http://127.0.0.1:8428/api/v1/write'


Authenticated remote write
--------------------------

When the remote write endpoint is behind an authenticating reverse proxy or
``vmauth``, enable the bearer token for the ``default`` instance. The entry is
merged with the ``default`` instance defined by the role:

.. code-block:: yaml

   vmagent__host_instances:

     - name: 'default'
       bearer_token: True

Put the token in the :file:`secret/vmagent/instances/default/bearer_token`
file on the Ansible Controller. The role copies it to
:file:`/etc/vmagent/default.token` on the host and passes it to
:command:`vmagent` with the ``-remoteWrite.bearerTokenFile`` flag.


Sending samples to several servers
----------------------------------

:command:`vmagent` sends all samples to each of the configured URLs, with
a separate persistent queue for each one:

.. code-block:: yaml

   vmagent__remote_write_urls:
     - 'https://vmetrics-primary.example.org/api/v1/write'
     - 'https://vmetrics-backup.example.org/api/v1/write'


Scraping remote targets
-----------------------

A host can run an additional instance which scrapes remote targets, for
example network devices through an SNMP exporter and HTTP endpoints through
the Blackbox exporter, next to the ``default`` instance. The additional
instance needs its own HTTP listen address:

.. code-block:: yaml

   vmagent__host_instances:

     - name: 'probes'
       remote_write_urls:
         - 'https://vmetrics.example.org/api/v1/write'
       flags:
         httpListenAddr: '127.0.0.1:8430'
       scrape_configs:
         - job_name: 'snmp'
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

See :ref:`vmagent__ref_instances` for the parameters of the instances.
