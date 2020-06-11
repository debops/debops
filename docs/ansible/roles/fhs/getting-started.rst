.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

Ansible local facts
-------------------

The :ref:`debops.fhs` role creates a local fact script on the managed hosts
which defines variables under the ``ansible_local.fhs.*`` hierarchy. Other
Ansible roles can use these variables to reference the base directories managed
by the :ref:`debops.fhs` role. This method provides a central place to control
where various data (shared files, binaries, application directories, etc.) is
stored in the filesystem. Furthermore, the role takes extra care to not modify
existing paths once applied, to ensure that the local facts stay consistent.

An example usage of the Ansible local facts defined by the role - define path
to the home directory of an application in the role default variables:

.. code-block:: yaml

   application__user: 'example-app'

   application__home: '{{ (ansible_local.fhs.home | d("/var/local"))
                          + "/" + application__user }}'

Example inventory
-----------------

The :ref:`debops.fhs` role is included in the ``common.yml`` DebOps playbook as
well as the bootstrap playbooks and you don't need to do anything to apply it
on the host.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.fhs`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/fhs.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::fhs``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
