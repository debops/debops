.. Copyright (C) 2026 Patryk Sciborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _prometheus_exporter__ref_guide_vmagent:

Guide: scraping exporters with vmagent
======================================

By default exporters listen on ``127.0.0.1``. Scrape targets must match
each exporter's ``listen_address`` (or the default
:envvar:`prometheus_exporter__default_listen_host` plus the known port).
Add a matching scrape job to the local :ref:`debops.vmagent` instance,
for example:

.. code-block:: yaml

   vmagent__default_remote_write_urls:
     - 'https://vmetrics.example.org/api/v1/write'

   vmagent__default_scrape_configs: '{{ [{
       "job_name": "node",
       "static_configs": [ { "targets": [ "127.0.0.1:9100" ] } ]
     }] + vmagent__extra_scrape_configs }}'

   vmagent__extra_scrape_configs: []

Per-group extra scrape jobs (e.g. for postgres on database hosts):

.. code-block:: yaml

   vmagent__extra_scrape_configs:
     - job_name: 'postgres'
       static_configs:
         - targets: [ '127.0.0.1:9187' ]
