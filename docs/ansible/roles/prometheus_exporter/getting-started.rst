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

   prometheus_exporter__default_exporters:

     - name: 'node'
       private_port: '3100'
       public_port: '9100'
       apt_packages: 'prometheus-node-exporter'

Listen address
~~~~~~~~~~~~~~

Default web listen address for all exporters.

.. code-block:: yaml

   prometheus_exporter__default_args:

     - name: 'common'
         options:
           - web.listen-address: '{{ ("localhost" if prometheus_exporter__pki|bool else prometheus_exporter__bind) + ":" +
                                     (item.private_port if prometheus_exporter__pki|bool else
                                     item.public_port) }}'

SSL and authentication
~~~~~~~~~~~~~~~~~~~~~~

If :ref:`debops.pki` role is used to configure a PKI environment, with default
``domain`` PKI realm enabled, ``debops.prometheus_exporter`` role will configure
the provided private keys and X.509 certificates to enable SSL connections from
Prometheus server by default with certificate authentication.

``debops.prometheus_exporter`` will configure SSL tunneling using Ghostunnel__,
a simple TLS proxy with mutual authentication support for securing non-TLS backend
applications. In this case, exporter will be configured to listen on ``localhost:<private_port>``
and Ghostunnel will be configured to listen on ``{{ prometheus_exporter__bind }}:<public_port>``.
Also Ghostunnel will enable certificate authentication for Prometheus server name
defined in ``{{ prometheus_exporter__server }}``.

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

   prometheus_exporter__exporters:

     - name: 'nginx'
       private_port: '3113'
       public_port: '9113'
       apt_packages: 'prometheus-nginx-exporter'

     - name: 'mysqld'
       private_port: '3104'
       public_port: '9104'
       apt_packages: 'prometheus-mysqld-exporter'

     - name: 'mongodb'
       private_port: '3216'
       public_port: '9216'
       apt_packages: 'prometheus-mongodb-exporter'

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

     - name: 'redis'
       private_port: '3121'
       public_port: '9121'
       upstream_type: 'url'
       url:
         - src: 'https://github.com/oliver006/redis_exporter/releases/download/v1.7.0/redis_exporter-v1.7.0.linux-amd64.tar.gz'
           dest: 'releases/linux-amd64/oliver006/redis_exporter/1.7.0/redis_exporter-v1.7.0.linux-amd64.tar.gz'
           checksum: 'sha256:70f634088b0bd5e9c5d724ee834c220468c321b479786244192419c41c57db78'
           unarchive: True
           unarchive_creates: 'releases/linux-amd64/oliver006/redis_exporter/1.7.0/redis_exporter-v1.7.0.linux-amd64/redis_exporter'

       url_binaries:
         - src: 'releases/linux-amd64/oliver006/redis_exporter/1.7.0/redis_exporter-v1.7.0.linux-amd64/redis_exporter'
           dest: 'prometheus-redis-exporter'
           notify: [ 'Restart prometheus exporters' ]

     - name: 'rabbitmq'
       private_port: '3419'
       public_port: '9419'
       upstream_type: 'url'
       url:
         - src: 'https://github.com/kbudde/rabbitmq_exporter/releases/download/v1.0.0-RC7/rabbitmq_exporter-1.0.0-RC7.linux-amd64.tar.gz'
           dest: 'releases/linux-amd64/kbudde/rabbitmq_exporter/1.0.0-RC7/rabbitmq_exporter-1.0.0-RC7.linux-amd64.tar.gz'
           unarchive: True
           unarchive_creates: 'releases/linux-amd64/kbudde/rabbitmq_exporter/1.0.0-RC7/rabbitmq_exporter-1.0.0-RC7.linux-amd64/rabbitmq_exporter'

       url_binaries:
         - src: 'releases/linux-amd64/kbudde/rabbitmq_exporter/1.0.0-RC7/rabbitmq_exporter-1.0.0-RC7.linux-amd64/rabbitmq_exporter'
           dest: 'prometheus-rabbitmq-exporter'
           notify: [ 'Restart prometheus exporters' ]

   prometheus_exporter__args:

     # Rabbitmq exporter doesn't support web.listen-address parameter.
     # Include this option in other exporters in the same host.
     - name: 'common'
       state: 'absent'

     - name: 'node'
       options:
         - web.listen-address: '{{ ("localhost" if prometheus_exporter__pki|bool else prometheus_exporter__bind) + ":" +
                                   (item.private_port if prometheus_exporter__pki|bool else
                                   item.public_port) }}'

     - name: 'phpfpm'
       options:
         - web.listen-address: '{{ ("localhost" if prometheus_exporter__pki|bool else prometheus_exporter__bind) + ":" +
                                   (item.private_port if prometheus_exporter__pki|bool else
                                   item.public_port) }}'
         - phpfpm.socket-paths:
              - '/run/php7.2-fpm.sock'
         - phpfpm.status-path: '/status.php'

     - name: 'redis'
       options:
         - web.listen-address: '{{ ("localhost" if prometheus_exporter__pki|bool else prometheus_exporter__bind) + ":" +
                                   (item.private_port if prometheus_exporter__pki|bool else
                                   item.public_port) }}'
         - redis.password: '{{ lookup("password", secret + "/redis/clusters/" + ansible_domain + "/password") }}'

   prometheus_exporter__env:

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
