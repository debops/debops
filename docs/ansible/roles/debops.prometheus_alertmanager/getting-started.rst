Getting started
===============

.. contents::
   :local:


Default configuration
---------------------




Example inventory
-----------------

To enable Prosody server support on a host, it needs to be included in the Ansible inventory in a specific group:

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
