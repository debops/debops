.. Copyright (C) 2024 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2024 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Getting started
===============

Example inventory
-----------------

The role is not active by default. To enable it on a given host, the host needs
to be included in the ``[debops_service_debconf]`` Ansible inventory group:

.. code-block:: none

   [debops_all_hosts]
   hostname

   [debops_service_debconf]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.debconf`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/debconf.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::debconf``
  Main role tag, should be used in the playbook to execute all tasks.

``role::debconf:commands``
  Run specified commands on the remote hosts.
