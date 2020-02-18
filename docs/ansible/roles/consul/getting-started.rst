Getting started
===============

.. only:: html

   .. contents::
      :local:


Example inventory
-----------------

To install Consul on a host, it needs to be added to a specific Ansible
inventory group:

.. code-block:: none

   [debops_service_consul]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.consul`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/consul.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::consul``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
