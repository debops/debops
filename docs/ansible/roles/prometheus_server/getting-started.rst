.. Copyright (C) 2020 Pedro Luis Lopez <pedroluis.lopezsanchez@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Getting started
===============

.. only:: html

   .. contents::
      :local:


Default configuration
---------------------

The configuration is split into 6 basic parameters,
this is because of YAML limitations and easier representation.

- :envvar:`prometheus_server__global_configuration`
- :envvar:`prometheus_server__rule_files_configuration`
- :envvar:`prometheus_server__alerting_configuration`
- :envvar:`prometheus_server__*_scrape_configs_configuration`
- :envvar:`prometheus_server__remote_write_configuration`
- :envvar:`prometheus_server__remote_read_configuration`

By default it configures node exporter and Alertmanager scrape configurations
with file-based service discovery mechanism that is used by
:ref:`debops.prometheus_exporter` and :ref:`debops.prometheus_alertmanager`
roles.

.. code-block:: yaml

   prometheus_server__alerting_configuration:

     alert_relabel_configs:

       - source_labels: ['__address__']
         separator:     ':'
         # Get hostname from address
         regex:         '([^.:]*)[.].*:(.*)'
         target_label:  'instance'
         replacement:   '${1}:${2}'

     alertmanagers:

       - scheme: '{{ "https" if prometheus_server__pki|bool else "http" }}'
         tls_config: '{{ prometheus_server__tls_config if prometheus_server__pki|bool else {} }}'
         file_sd_configs:
           - files:
               - '/etc/prometheus/file_sd_configs.d/alertmanager.*.json'

   prometheus_server__default_server_scrape_config_configuration:

     - job_name: 'prometheus'
       scrape_interval: '5s'
       scrape_timeout: '5s'
       static_configs:
         - targets: [ '{{ ("localhost" if prometheus_server__bind == "0.0.0.0" else
                           prometheus_server__bind) + ":" + prometheus_server__port }}' ]
       relabel_configs:
         - target_label:  'instance'
           replacement:   '{{ ansible_hostname }}:{{ prometheus_server__port }}'

   prometheus_server__default_scrape_configs_configuration:

     - job_name: 'node'
       scheme: '{{ "https" if prometheus_server__pki|bool else "http" }}'
       tls_config: '{{ prometheus_server__tls_config if prometheus_server__pki|bool else {} }}'
       file_sd_configs:
         - files:
             - '/etc/prometheus/file_sd_configs.d/node.*.json'
       relabel_configs:
         - source_labels: ['__address__']
           separator:     ':'
           # Get hostname from address
           regex:         '([^.:]*)[.].*:(.*)'
           target_label:  'instance'
           replacement:   '${1}:${2}'

     - job_name: 'alertmanager'
       scheme: '{{ "https" if prometheus_server__pki|bool else "http" }}'
       tls_config: '{{ prometheus_server__tls_config if prometheus_server__pki|bool else {} }}'
       file_sd_configs:
         - files:
             - '/etc/prometheus/file_sd_configs.d/alertmanager.*.json'
       relabel_configs:
         - source_labels: ['__address__']
           separator:     ':'
           # Get hostname from address
           regex:         '([^.:]*)[.].*:(.*)'
           target_label:  'instance'
           replacement:   '${1}:${2}'

TLS and authentication for scrape configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the :ref:`debops.pki` role is used to configure a PKI environment, with default
``domain`` PKI realm enabled, ``debops.prometheus_server`` role will configure
the provided private keys and X.509 certificates to enable TLS connections to
the exporters and Alertmanagers by default with certificate authentication.

:ref:`debops.prometheus_exporter` and :ref:`debops.prometheus_alertmanager`
will configure TLS tunneling using Ghostunnel__, a simple TLS proxy with mutual
authentication support for securing non-TLS backend applications.

If the PKI environment is not configured or disabled, connections to the
Prometheus server will be performed in cleartext, so you might want to consider
securing them by deploying the server on a separate internal network, or
accessing it over a VPN connection. You can use ``debops.subnetwork``,
:ref:`debops.tinc` and :ref:`debops.dnsmasq` Ansible roles to set up a VPN internal
network to secure communication between hosts.

.. __: https://github.com/square/ghostunnel

Example inventory
-----------------

To install Prometheus on a host, you need to add it to
``[debops_service_prometheus_server]`` Ansible group:

.. code-block:: none

   [debops_service_prometheus_server]
   prometheus-host

This will install ``prometheus`` package, configure the server to discover node
exporter and Alertmanager targets with file-based service discovery mechanism
and configure ``nginx`` to access the server with basic authentication.

Also you can add other Prometheus server configuration like scrape configurations
and / or rules:

.. code-block:: yaml

   prometheus_server__scrape_configs_configuration:

     - job_name: 'nginx'
       scheme: '{{ "https" if prometheus_server__pki|bool else "http" }}'
       tls_config: '{{ prometheus_server__tls_config if prometheus_server__pki|bool else {} }}'
       file_sd_configs:
         - files:
           - '/etc/prometheus/file_sd_configs.d/nginx.*.json'
       relabel_configs:
         - source_labels: ['__address__']
           separator:     ':'
           regex:         '([^.:]*)[.].*:(.*)' # Get hostname from address
           target_label:  'instance'
           replacement:   '${1}:${2}'

     - job_name: 'phpfpm'
       scheme: '{{ "https" if prometheus_server__pki|bool else "http" }}'
       tls_config: '{{ prometheus_server__tls_config if prometheus_server__pki|bool else {} }}'
       file_sd_configs:
         - files:
           - '/etc/prometheus/file_sd_configs.d/phpfpm.*.json'
       relabel_configs:
         - source_labels: ['__address__']
           separator:     ':'
           regex:         '([^.:]*)[.].*:(.*)' # Get hostname from address
           target_label:  'instance'
           replacement:   '${1}:${2}'

     - job_name: 'mysqld'
       scheme: '{{ "https" if prometheus_server__pki|bool else "http" }}'
       tls_config: '{{ prometheus_server__tls_config if prometheus_server__pki|bool else {} }}'
       file_sd_configs:
         - files:
           - '/etc/prometheus/file_sd_configs.d/mysqld.*.json'
       relabel_configs:
         - source_labels: ['__address__']
           separator:     ':'
           regex:         '([^.:]*)[.].*:(.*)' # Get hostname from address
           target_label:  'instance'
           replacement:   '${1}:${2}'

     - job_name: 'redis'
       scheme: '{{ "https" if prometheus_server__pki|bool else "http" }}'
       tls_config: '{{ prometheus_server__tls_config if prometheus_server__pki|bool else {} }}'
       file_sd_configs:
         - files:
           - '/etc/prometheus/file_sd_configs.d/redis.*.json'
       relabel_configs:
         - source_labels: ['__address__']
           separator:     ':'
           regex:         '([^.:]*)[.].*:(.*)' # Get hostname from address
           target_label:  'instance'
           replacement:   '${1}:${2}'

     - job_name: 'mongodb'
       scheme: '{{ "https" if prometheus_server__pki|bool else "http" }}'
       tls_config: '{{ prometheus_server__tls_config if prometheus_server__pki|bool else {} }}'
       file_sd_configs:
         - files:
           - '/etc/prometheus/file_sd_configs.d/mongodb.*.json'
       relabel_configs:
         - source_labels: ['__address__']
           separator:     ':'
           regex:         '([^.:]*)[.].*:(.*)' # Get hostname from address
           target_label:  'instance'
           replacement:   '${1}:${2}'

     - job_name: 'rabbitmq'
       scheme: '{{ "https" if prometheus_server__pki|bool else "http" }}'
       tls_config: '{{ prometheus_server__tls_config if prometheus_server__pki|bool else {} }}'
       file_sd_configs:
         - files:
           - '/etc/prometheus/file_sd_configs.d/rabbitmq.*.json'
       relabel_configs:
         - source_labels: ['__address__']
           separator:     ':'
           regex:         '([^.:]*)[.].*:(.*)' # Get hostname from address
           target_label:  'instance'
           replacement:   '${1}:${2}'

   prometheus_server__rules:

     - name: 'example'
       rules:
         - alert: PrometheusTargetMissing
           expr: up == 0
           for: 5m
           labels:
             severity: error
           annotations:
             summary: !unsafe "Prometheus target missing (instance {{ $labels.instance }})"
             description: !unsafe "A Prometheus target has disappeared. An exporter might be crashed.\n  VALUE = {{ $value }}\n  LABELS: {{ $labels }}"

Example playbook
----------------

Here's an example Ansible playbook that uses the ``debops.prometheus_server``
role:

.. literalinclude:: ../../../../ansible/playbooks/service/prometheus_server.yml
   :language: yaml

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::prometheus_server``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::prometheus_server:config``
  Configuration role tag, should be used in the playbook to execute only
  configuration tasks.
