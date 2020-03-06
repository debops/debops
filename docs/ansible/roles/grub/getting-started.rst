.. Copyright (C) 2015 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2015-2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2015-2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:

Example inventory
-----------------

To manage GRUB on a given host or a set of hosts, they need to be added to the
``[debops_service_grub]`` Ansible group in the inventory:

.. code:: ini

   [debops_service_grub]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.grub`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/grub.yml
   :language: yaml
   :lines: 1,7-


Password protection
-------------------

To enable password protection, simply define a superuser like this:

.. code:: yaml

   grub__users:
     - name: 'su'
       password: 'NBLWAThUq5'
       superuser: True

The password will be hashed and salted on the Ansible controller and only the
salted hash will be configured in the GRUB configuration.

With this change, GRUB will require authentication when attempting to change
boot options or invoking a recovery shell. Booting menu entries will not
require authentication so this configuration should be safe for normal
operation.
