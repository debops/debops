Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

To install and manage DHCP Probe on a host, it needs to be included in the
``[debops_service_dhcp_probe]`` Ansible inventory group:

.. code-block:: none

   [debops_service_dhcp_probe]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.dhcp_probe`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/dhcp_probe.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::dhcp_probe``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.dhcp_probe`` Ansible
role:

- Manual pages: :man:`dhcp_probe(8)`, :man:`dhcp_probe.cf(5)`
