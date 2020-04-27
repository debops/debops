.. Copyright (C) 2020 Pedro Luis Lopez <pedroluis.lopezsanchez@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Default variable details
========================

Some of ``debops.prometheus_exporter`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _prometheus_exporter__release_exporters:

prometheus_exporter__release_exporters
--------------------------------------

List of exporters installed from repositories releases that should be present given host.
Each exporter is defined as a YAML dict with the following keys:

``name``
  Required. Name of the exporter. Names of exporters are used to port configuration
  and arguments.

``resource``
  Required. URL where exporter release is present.

``archive``
  Optional, boolean. Defaults to ``False``. If a release exporter is distributed with archived
  mechanism like ``tar.gz``, set to ``True`` for unarchived before install the exporter.

``binary``
  Optional. Exporter binary location inside archived release when you have to use ``archive`` option.

Examples
~~~~~~~~

PHP-FPM and Redis exporter with port configuration:

.. code-block:: yaml

   prometheus_exporter__release_exporters:

     - name: 'phpfpm'
       resource: 'https://github.com/Lusitaniae/phpfpm_exporter/releases/download/v0.5.0/phpfpm_exporter-0.5.0.linux-amd64.tar.gz'
       archive: True
       binary: 'phpfpm_exporter-0.5.0.linux-amd64/phpfpm_exporter'

     - name: 'redis'
       resource: 'https://github.com/oliver006/redis_exporter/releases/download/v1.5.3/redis_exporter-v1.5.3.linux-amd64.tar.gz'
       archive: True
       binary: 'redis_exporter-v1.5.3.linux-amd64/redis_exporter'

   prometheus_exporter__ports_map:

     phpfpm: '9253'
     redis: '9121'

.. _prometheus_exporter__args:

prometheus_exporter__args
-------------------------

List of exporter arguments that should be present on exporter configuration files on a given host.
Each exporter arguments is defined as a YAML dict with the following keys:

``name``
  Required. Name of the exporter. Names of exporters are used to port configuration
  and arguments.

``options``
  Required. YAML dict. Arguments that should be present on exporter configuration file
  with name ``name``. Options values can be a string or a list.

Examples
~~~~~~~~

Arguments for PHP-FPM and Redis exporters:

.. code-block:: yaml

   prometheus_exporter__args:

     - name: 'phpfpm'
       options:
         - phpfpm.socket-paths:
              - '/run/php7.2-fpm.sock'
         - phpfpm.status-path: '/status.php'

     - name: 'redis'
       options:
         - redis.password: '{{ lookup("password", secret + "/redis/clusters/" + ansible_domain + "/password") }}'
