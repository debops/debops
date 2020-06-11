.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Example inventory
-----------------

The ``debops.tzdata`` role is included by default in the ``common.yml`` DebOps
playbook; you don't need to add hosts to any Ansible groups to enable it.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.tzdata`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/tzdata.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::tzdata``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.tzdata`` Ansible role:

- Manual pages: :man:`timedatectl(1)`

- `Details about time zone changes on Debian wiki`__

  .. __: https://wiki.debian.org/TimeZoneChanges
