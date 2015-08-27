Getting started
===============

.. contents::
   :local:

Example inventory
-----------------

To manage GRUB configuration on a given host with DebOps you should add it to the
``[debops_grub]`` Ansible host group::

    [debops_grub]
    hostname


Example playbook
----------------

Here's an example playbook which uses ``debops.grub`` role::

    ---

    - name: Configure GRUB
      hosts: debops_grub
      sudo: True

      roles:
        - role: debops.grub
          tags: grub
