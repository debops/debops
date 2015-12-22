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


Password protection
-------------------

To enable password protection, simply define a superuser like this::

    grub_users:
      - name: 'su'
        password: 'NBLWAThUq5'
        superuser: True

The password will be hashed and salted on the Ansible controller and only the
salted hash will be configured in the GRUB configuration.

With this change, GRUB will require authentication when attempting to change
boot options or invoking a recovery shell. Booting menu entires will not
require authentication so this configuration should be safe for normal
operation.
