.. Copyright (C) 2015-2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2016 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:

Example inventory
-----------------

To configure LVM on a host without using other roles, you should add that host
to ``[debops_service_lvm]`` Ansible group::

    [debops_service_lvm]
    hostname

If you use separate host groups, a better idea might be to create a parent group
and add your own host groups to it::

    [servers]
    host1
    host2

    [debops_service_lvm:children]
    servers

Example playbook
----------------

Here's an example playbook which uses ``debops.lvm`` role::

    ---

    - name: Configure Logical Volume Manager
      hosts: [ 'debops_service_lvm' ]
      become: True

      roles:
        - role: debops.lvm
          tags: [ 'role::lvm' ]

