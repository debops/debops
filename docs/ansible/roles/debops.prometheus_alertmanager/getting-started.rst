Getting started
===============

.. contents::
   :local:


Introduction
------------

The Alertmanager handles alerts sent by client applications such as the Prometheus server. It takes care of deduplicating, grouping, and routing them to the correct receiver integration such as email, PagerDuty, or OpsGenie. It also takes care of silencing and inhibition of alerts.

[Source](https://prometheus.io/docs/alerting/alertmanager/)

Usage
-----

By default all exporter only listen on localhost (blocked by firewall).
This can be changed with the following variables:

- :envvar:`prometheus_alertmanager__nginx` activate secure ports with a nginx proxy
- :envvar:`prometheus_alertmanager__allow` allow direct tcp connection

The used port is 9093 or if nginx proxy is activated 19093

Example inventory
-----------------

To enable Prometheus Alertmanager on a host,
the host needs to be included in the Ansible inventory in a specific group:

.. code-block:: none

   [debops_service_prometheus_alertmanager]
   hostname

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.prometheus_alertmanager`` role:

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
``role::ferm``
  Role tag for configure the firewall ferm.
