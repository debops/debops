.. Copyright (C) 2021 Pedro Luis Lopez <pedroluis.lopezsanchez@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Getting started
===============

.. only:: html

   .. contents::
      :local:


Default configuration
---------------------

By default it set some parameters for ghostunnel services about timeouts and
log messages. These parameters can be override by each service.

.. code-block:: yaml

   ghostunnel__default_configuration:
      shutdown_timeout: '5m'
      connect_timeout: '10s'
      quiet: 'conns'

SSL and authentication
~~~~~~~~~~~~~~~~~~~~~~

:ref:`debops.pki` role is required and is used to configure a PKI environment,
with default ``domain`` PKI realm enabled, ``debops.ghostunnel`` role will configure
the provided private keys and X.509 certificates to enable SSL connections
by default with certificate authentication.

Example inventory
-----------------

To install Ghostunnel on a host, you need to add it to
``[debops_service_ghostunnel]`` Ansible group:

.. code-block:: none

   [debops_service_ghostunnel]
   target-host

This will install ``ghostunnel`` binary.

Also you can configure systemd services for server mode and client mode.
Next you can find some examples.

Tunneling insecure Elasticsearch TCP connections.

Inventory

.. code-block:: yaml

   [debops_service_elasticsearch]
   elasticsearch-01
   elasticsearch-02

   [debops_service_elasticsearch_lb:children]
   elasticsearch-lb-01

   [debops_service_elasticsearch_tunnel:children]
   debops_service_elasticsearch
   debops_service_elasticsearch_lb

   [debops_service_ghostunnel:children]
   debops_service_elasticsearch_tunnel

Inventory ``debops_service_elasticsearch_tunnel`` group.

.. code-block:: yaml

   netbase__hosts:
     - name: '127.0.0.1'
       value:
           - 'elasticsearch-01-tunnel'
           - 'elasticsearch-02-tunnel'
           - 'elasticsearch-lb-01-tunnel'

   elasticsearch__discovery_hosts:
     - 'elasticsearch-01-tunnel:9302'
     - 'elasticsearch-02-tunnel:9303'

   ghostunnel__configuration:
     shutdown_timeout: '1s'

   ghostunnel__services:

     - name: 'elasticsearch-tcp-tls'
       mode: 'server'
       listen: '{{ inventory_hostname }}:9301'
       target: 'localhost:9300'
       allow_cn: # Certificate authentication
         - 'elasticsearch-01.{{ ansible_domain }}'
         - 'elasticsearch-02.{{ ansible_domain }}'
         - 'elasticsearch-lb-01.{{ ansible_domain }}'

     - name: 'elasticsearch-01-tcp-tls'
       mode: 'client'
       listen: 'localhost:9302'
       target: 'elasticsearch-01.{{ ansible_domain }}:9301'

     - name: 'elasticsearch-02-tcp-tls'
       mode: 'client'
       listen: 'localhost:9303'
       target: 'elasticsearch-02.{{ ansible_domain }}:9301'

     - name: 'elasticsearch-lb-01-tcp-tls'
       mode: 'client'
       listen: 'localhost:9304'
       target: 'elasticsearch-lb-01.{{ ansible_domain }}:9301'

Inventory ``elasticsearch-01``.

.. code-block:: yaml

   elasticsearch__configuration:
     - 'transport.publish_host': '{{ inventory_hostname }}-tunnel'
     - 'transport.publish_port': '9302'

Inventory ``elasticsearch-02``.

.. code-block:: yaml

   elasticsearch__configuration:
     - 'transport.publish_host': '{{ inventory_hostname }}-tunnel'
     - 'transport.publish_port': '9303'

Inventory ``elasticsearch-lb-01``:

.. code-block:: yaml

   elasticsearch__configuration:
     - 'transport.publish_host': '{{ inventory_hostname }}-tunnel'
     - 'transport.publish_port': '9304'

Also support simple TLS HTTPS proxy with firewall security (disabling certificate authentication).
For example HTTP interface of Elasticsearch, ...

.. code-block:: yaml

   ghostunnel__services:

     - name: 'elasticsearch-https'
       mode: 'server'
       listen: '{{ inventory_hostname }}:9201'
       target: 'localhost:9200'
       allow: [ '10.0.0.4' ] # IP of logstash service
       disable_authentication: True # Disabling certificate authentication,
                                    # if allow is empty, nobody can connect
                                    # to the transport port

And now you can use HTTPS interface in a future ``logstash`` role:

.. code-block:: yaml

   logstash__elasticsearch_hosts:
     - 'https://elasticsearch-01.{{ ansible_domain }}:9201'
     - 'https://elasticsearch-02.{{ ansible_domain }}:9201'

Example playbook
----------------

Here's an example Ansible playbook that uses the ``debops.ghostunnel``
role:

.. literalinclude:: ../../../../ansible/playbooks/service/ghostunnel.yml
   :language: yaml

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::ghostunnel``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::ghostunnel:config``
  Configuration role tag, should be used in the playbook to execute only
  configuration tasks.
