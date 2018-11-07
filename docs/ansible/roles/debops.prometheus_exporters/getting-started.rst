Getting started
===============

.. contents::
   :local:


Default configuration
---------------------

By default all exporter only listen on localhost (blocked by firewall).
This can be changed with the following variables:

- :envvar:`prometheus_exporters__nginx` activate secure ports with a nginx proxy
- :envvar:`prometheus_exporters__allow` allow direct tcp connection


Ports
~~~~~

By default the ports are:
- `9100` node
- `9104` mysql
- `9154` postfix

Secure ports are:
- `19100` node
- `19104` mysql
- `19154` postfix


Exporters
~~~~~~~~~

You can define which exporter is going to be installed,
with the :envvar:`prometheus_exporters__exporters` variable.


Example inventory
-----------------

To enable Prometheus exporters on a host,
the host needs to be included in the Ansible inventory in a specific group:

.. code-block:: none

   [debops_service_prometheus_exporters]
   hostname

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.prometheus_exporters`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/prometheus_exporters.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::prometheus_exporters``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
``role::ferm``
  Role tag for configure the firewall ferm.
