.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _prometheus_exporter__ref_guide_vmagent:

Guide: scraping exporters with vmagent
======================================

By default the exporters listen on ``127.0.0.1`` and are scraped by
a :command:`vmagent` instance on the same host, managed by the
:ref:`debops.vmagent` role, which sends the samples to a remote storage. The
scrape targets have to match the ``listen_address`` of each exporter, or
:envvar:`prometheus_exporter__default_listen_host` and the known port.

Send the samples to the remote storage and scrape the ``node`` exporter on
all hosts:

.. code-block:: yaml

   vmagent__remote_write_urls:
     - 'https://vmetrics.example.org/api/v1/write'

   vmagent__scrape_configs:

     - job_name: 'node'
       static_configs:
         - targets: [ '127.0.0.1:9100' ]

Scrape the ``postgres`` exporter on the database servers, in the inventory
group of these hosts:

.. code-block:: yaml

   vmagent__group_scrape_configs:

     - job_name: 'postgres'
       static_configs:
         - targets: [ '127.0.0.1:9187' ]

The jobs with the same ``job_name`` are merged together, so a list on
a higher level can change a job defined on a lower one, see
:ref:`vmagent__ref_scrape_configs`. The ``host`` label in
:envvar:`vmagent__external_labels` tells the hosts apart, since the targets
have the same address on all of them.
