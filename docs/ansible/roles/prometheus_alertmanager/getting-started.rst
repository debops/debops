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

The configuration is split into 5 basic parameters,
this is because of limitation of YAML and easier representation.

- prometheus_alertmanager__global_configuration
- prometheus_alertmanager__templates_configuration
- prometheus_alertmanager__route_configuration
- prometheus_alertmanager__receivers_configuration
- prometheus_alertmanager__inhibit_rules_configuration

By default it configures a ``default-receiver``.

.. code-block:: yaml

   prometheus_alertmanager__route_configuration:

     receiver: 'default-receiver'

   prometheus_alertmanager__receivers_configuration:

     - name: 'default-receiver'

Alertmanager arguments
~~~~~~~~~~~~~~~~~~~~~~

Default arguments for Prometheus alertmanager.

.. code-block:: yaml

   prometheus_alertmanager__args:

     - name: 'config.file'
       value: '/etc/prometheus/alertmanager.yml'

     - name: 'web.listen-address'
       value: '{{ ("127.0.0.1" if prometheus_alertmanager__pki|bool else prometheus_alertmanager__bind) + ":" +
                  ("3" + prometheus_alertmanager__port[1:] if
                  prometheus_alertmanager__pki|bool else prometheus_alertmanager__port) }}'

     - name: 'cluster.listen-address'
       value: '{{ ("127.0.0.1" if prometheus_alertmanager__pki|bool else prometheus_alertmanager__cluster_bind) + ":" +
                  ("3" + prometheus_alertmanager__cluster_port[1:] if
                  prometheus_alertmanager__pki|bool else prometheus_alertmanager__cluster_port) }}'

     - name: 'web.external-url'
       value: 'https://{{ prometheus_alertmanager__fqdn }}'

SSL and authentication
~~~~~~~~~~~~~~~~~~~~~~

If :ref:`debops.pki` role is used to configure a PKI environment, with default
``domain`` PKI realm enabled, ``debops.prometheus_alertmanager`` role will configure
the provided private keys and X.509 certificates to enable SSL connections from
Prometheus server by default with certificate authentication.

``debops.prometheus_alertmanager`` will configure SSL tunneling using Ghostunnel__,
a simple TLS proxy with mutual authentication support for securing non-TLS backend
applications. In this case, alertmanager will be configured to listen on ``localhost:3093``
and Ghostunnel will be configured to listen on ``{{ prometheus_alertmanager__bind }}:9093``.
Also Ghostunnel will enable certificate authentication for Prometheus server name
defined in ``{{ prometheus_alertmanager__server }}``.

If the PKI environment is not configured or disabled, connections to the
Prometheus server will be performed in cleartext, so you might want to consider
securing them by configuring server on a separate internal network, or
accessing it over a VPN connection. You can use ``debops.subnetwork``,
:ref:`debops.tinc` and :ref:`debops.dnsmasq` Ansible roles to set up a VPN internal
network to secure communication between hosts.

.. __: https://github.com/square/ghostunnel

Example inventory
-----------------

To install Prometheus alertmanager on a host, you need to add it to
``[debops_service_prometheus_alertmanager]`` Ansible group:

.. code-block:: none

   [debops_service_prometheus_alertmanager]
   alertmanager-host

This will install ``prometheus-alertmanager`` package, configure the server to
discover alertmanager target using file-based service discovery mechanism and
configure ``nginx`` to access the web interface with basic authentication.

To allow connect it from a Prometheus server, you need to set two variables in the inventory:

.. code-block:: yaml

   prometheus_alertmanager__server: 'prometheus.domain.com'

   prometheus_alertmanager__allow: [ '<IP prometheus server>' ]

This needs to be a FQDN address of a host with Prometheus server installed. DNS
name is required because this access is via a HTTP(S) API. Currently only 1
server at a time is supported by the role.

Also you can add other configurations to Prometheus alertmanager.

.. code-block:: yaml

   prometheus_alertmanager__global_configuration:

     smtp_from: 'prometheus@domain.com'
     smtp_smarthost: '...'
     smtp_auth_username: '...'
     smtp_auth_password: '...'

   prometheus_alertmanager__receivers_configuration:

     - name: 'default-receiver'
       email_configs:
         - to: 'op@domain.com'

Example playbook
----------------

Here's an example Ansible playbook that uses the ``debops.prometheus_alertmanager``
role:

.. literalinclude:: ../../../../ansible/playbooks/service/prometheus_alertmanager.yml
   :language: yaml

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::prometheus_alertmanager``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::prometheus_alertmanager:config``
  Configuration role tag, should be used in the playbook to execute only
  configuration tasks.
