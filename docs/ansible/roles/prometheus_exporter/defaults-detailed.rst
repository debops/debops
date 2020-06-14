.. Copyright (C) 2020 Pedro Luis Lopez <pedroluis.lopezsanchez@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Default variable details
========================

Some of ``debops.prometheus_exporter`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _prometheus_exporter__exporters:

prometheus_exporter__exporters
------------------------------

List of exporters that should be present given host.
Each exporter is defined as a YAML dict. It uses ``debops.golang`` role for installation.
You can see all options for installation in :ref:`debops.golang` role.
Also you must to define the following options:

``private_port``
  Required if :ref:`debops.pki` role is used. In this case, exporter will be configured
  to listen on ``localhost:<private_port>`` and Ghostunnel will be configured to
  listen on ``{{ prometheus_exporter__bind }}:<public_port>``.

``public_port``
  Required. Exporter will be configured to listen on ``{{ prometheus_exporter__bind }}:<public_port>``
  if :ref:`debops.pki` role is not used.

Examples
~~~~~~~~

PHP-FPM and Redis exporter with port configuration:

.. code-block:: yaml

   prometheus_exporter__exporters:

     - name: 'nginx'
       private_port: '3113'
       public_port: '9113'
       apt_packages: 'prometheus-nginx-exporter'

     - name: 'phpfpm'
       private_port: '3253'
       public_port: '9253'
       upstream_type: 'url'
       url:
         - src: 'https://github.com/Lusitaniae/phpfpm_exporter/releases/download/v0.5.0/phpfpm_exporter-0.5.0.linux-amd64.tar.gz'
           dest: 'releases/linux-amd64/Lusitaniae/phpfpm_exporter/0.5.0/phpfpm_exporter-0.5.0.linux-amd64.tar.gz'
           checksum: 'sha256:3eb1af2d8f107e9aa43467e8a5e823bd7da8b1c600f61e020708de29746b6c40'
           unarchive: True
           unarchive_creates: 'releases/linux-amd64/Lusitaniae/phpfpm_exporter/0.5.0/phpfpm_exporter-0.5.0.linux-amd64/phpfpm_exporter'

       url_binaries:
         - src: 'releases/linux-amd64/Lusitaniae/phpfpm_exporter/0.5.0/phpfpm_exporter-0.5.0.linux-amd64/phpfpm_exporter'
           dest: 'prometheus-phpfpm-exporter'
           notify: [ 'Restart prometheus exporters' ]

.. _prometheus_exporter__apm_exporters:

prometheus_exporter__apm_exporters
----------------------------------

List of services that provides metrics for prometheus that should be present given host.
Each APM exporter is defined as a YAML dict:

``name``
  Required. Name of the service that provides metrics for prometheus.

``private_port``
  Required if :ref:`debops.pki` role is used. In this case, Ghostunnel will be configured
  to read from ``localhost:<private_port>`` (where service listen on) and listen on
  ``{{ prometheus_exporter__bind }}:<public_port>``.

``public_port``
  Required. Port where service listen on if :ref:`debops.pki` role is not used.

Examples
~~~~~~~~

.. code-block:: yaml

   prometheus_exporter__apm_exporters:

     - name: 'service'
       private_port: '3070'
       public_port: '9070'

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
