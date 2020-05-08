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

By default it configures node exporter with file-based service discovery
mechanism that is used by :ref:`debops.prometheus_server` role.

.. code-block:: yaml

   prometheus_exporter__default_exporters: [ 'node' ]

Ports
~~~~~

Default ports for exporters installed from Debian packages are:

.. code-block:: yaml

   prometheus_exporter__default_ports_map:
     apache:  '9117:3117'
     bind: '9119:3119'
     bird: '9324:3324'
     blackbox: '9110:3110'
     haproxy: '9101:3101'
     mongodb: '9216:3216'
     mysqld: '9104:3104'
     nginx: '9113:3113'
     node: '9100:3100'
     pgbouncer: '9127:3127'
     postgres: '9187:3187'
     process: '9256:3256'
     snmp: '9116:3116'
     sql: '9237:3237'
     squid: '9301:3301'
     trafficserver: '9548:3548'
     varnish: '9131:3131'

Listen address
~~~~~~~~~~~~~~

Default web listen address for all exporters.

.. code-block:: yaml

   prometheus_exporter__default_args:

     - name: 'common'
       options:
         - web.listen-address: '{{ ("localhost" if prometheus_exporter__pki|bool else prometheus_exporter__bind) + ":" +
                                   (prometheus_exporter__combined_ports_map[item].split(":")[1] if
                                   prometheus_exporter__pki|bool else
                                   prometheus_exporter__combined_ports_map[item].split(":")[0]) }}'

SSL and authentication
~~~~~~~~~~~~~~~~~~~~~~

If :ref:`debops.pki` role is used to configure a PKI environment, with default
``domain`` PKI realm enabled, ``debops.prometheus_exporter`` role will configure
the provided private keys and X.509 certificates to enable SSL connections from
Prometheus server by default with certificate authentication.

``debops.prometheus_exporter`` will configure SSL tunneling using Ghostunnel__,
a simple TLS proxy with mutual authentication support for securing non-TLS backend
applications. In this case, exporter will be configured to listen on ``localhost:3xxx``
and Ghostunnel will be configured to listen on ``{{ prometheus_exporter__bind }}:9xxx``.
Also Ghostunnel will enable certificate authentication for Prometheus server name
defined in ``{{ prometheus_exporter__server }}``.

Example: Node exporter port is 9100. If pki is enabled, this role will configure
node exporter to listen on ``localhost:3100`` and Ghostunnel will be configured to
listen on ``{{ prometheus_exporter__bind }}:9100`` for SSL connections from
Prometheus server.

If the PKI environment is not configured or disabled, connections to the
Prometheus server will be performed in cleartext, so you might want to consider
securing them by configuring server on a separate internal network, or
accessing it over a VPN connection. You can use ``debops.subnetwork``,
:ref:`debops.tinc` and :ref:`debops.dnsmasq` Ansible roles to set up a VPN internal
network to secure communication between hosts.

.. __: https://github.com/square/ghostunnel

Example inventory
-----------------

To install Prometheus node exporter on a host, you need to add it to
``[debops_service_prometheus_exporter]`` Ansible group:

.. code-block:: none

   [debops_service_prometheus_exporter]
   target-host

This will install ``prometheus-node-exporter`` package and configure the server to
discover node exporter target using file-based service discovery mechanism.

To allow collect it from a Prometheus server, you need to set two variables in the inventory:

.. code-block:: yaml

   prometheus_exporter__server: 'prometheus.domain.com'

   prometheus_exporter__allow: [ '<IP prometheus server>' ]

This needs to be a FQDN address of a host with Prometheus server installed. DNS
name is required because this access is via a HTTP(S) API. Currently only 1
server at a time is supported by the role.

Also you can install and configure other exporters from Debian packages, releases in
repositories or built-in exporters. Next you can find some examples.

Debian packages examples.

.. code-block:: yaml

   prometheus_exporter__exporters: [ 'nginx', 'mysqld', 'mongodb' ]

   prometheus_exporter__args:

     - name: 'nginx'
       options:
         - nginx.scrape-uri: 'https://{{ nginx_fqdn }}/nginx_status'

     - name: 'mongodb'
       options:
         - mongodb.uri: '{{ """mongodb://monitor:" +
                            lookup("password", secret + "/mongodb/" + ansible_fqdn + "/credentials/monitor/password") +
                            "@localhost:27017""" }}'

Release packages examples (PHP-FPM exporter needs access to socket, so you can
add ``prometheus`` user to ``www-data`` group).

.. code-block:: yaml

   prometheus_exporter__append_groups: [ 'www-data' ]

   prometheus_exporter__release_exporters:

     - name: 'phpfpm'
       resource: 'https://github.com/Lusitaniae/phpfpm_exporter/releases/download/v0.5.0/phpfpm_exporter-0.5.0.linux-amd64.tar.gz'
       archive: True
       binary: 'phpfpm_exporter-0.5.0.linux-amd64/phpfpm_exporter'

     - name: 'redis'
       resource: 'https://github.com/oliver006/redis_exporter/releases/download/v1.5.3/redis_exporter-v1.5.3.linux-amd64.tar.gz'
       archive: True
       binary: 'redis_exporter-v1.5.3.linux-amd64/redis_exporter'

     - name: 'rabbitmq'
       resource: 'https://github.com/kbudde/rabbitmq_exporter/releases/download/v1.0.0-RC6.1/rabbitmq_exporter-1.0.0-RC6.1.linux-amd64.tar.gz'
       archive: True
       binary: 'rabbitmq_exporter-1.0.0-RC6.1.linux-amd64/rabbitmq_exporter'

   prometheus_exporter__ports_map:

     phpfpm: '9253:3253'
     redis: '9121:3121'
     rabbitmq: '9419:3419'

   prometheus_exporter__args:

     - name: 'phpfpm'
       options:
         - phpfpm.socket-paths:
              - '/run/php7.2-fpm.sock'
         - phpfpm.status-path: '/status.php'

     - name: 'redis'
       options:
         - redis.password: '{{ lookup("password", secret + "/redis/clusters/" + ansible_domain + "/password") }}'

     - name: 'rabbitmq'
       options:
         - RABBIT_USER: 'monitor'
           RABBIT_PASSWORD: '{{ lookup("password", secret + "/rabbitmq_server/accounts/monitor/password") }}'
           PUBLISH_ADDR: '{{ "localhost" if prometheus_exporter__pki|bool else prometheus_exporter__bind }}'
           PUBLISH_PORT: '{{ "3419" if prometheus_exporter__pki|bool else "9419" }}'

Example playbook
----------------

Here's an example Ansible playbook that uses the ``debops.prometheus_exporter``
role:

.. literalinclude:: ../../../../ansible/playbooks/service/prometheus_exporter.yml
   :language: yaml

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::prometheus_exporter``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::prometheus_exporter:config``
  Configuration role tag, should be used in the playbook to execute only
  configuration tasks.
