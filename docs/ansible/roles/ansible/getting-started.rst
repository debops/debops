.. Copyright (C) 2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Example inventory
-----------------

To install Ansible on a host, it needs to be added to a specific Ansible
inventory group:

.. code-block:: none

   [debops_service_ansible]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.ansible`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/ansible.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::ansible``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
