.. Copyright (C) 2016-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2021 Julien Lecomte <julien@lecomte.at>
.. Copyright (C) 2016-2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:

Description
-----------

The role is meant to be a simple way to remove packages from hosts.

Example inventory
-----------------

The ``debops.apt_uninstall`` role is included by default in the :file:`common.yml`
DebOps playbook. You don't need to configure anything in the inventory to
enable it.

The role provides a set of default variables to specify what packages should be
installed on hosts, depending on the inventory level:

:envvar:`apt_uninstall__packages`
  This variable should be used in
  :file:`ansible/inventory/group_vars/all/apt_uninstall.yml` file and is meant to
  specify packages absent on all hosts in the inventory.

:envvar:`apt_uninstall__group_packages`
  This variable should be used in
  :file:`ansible/inventory/group_vars/<group-name>/apt_uninstall.yml` files and is
  meant to contain packages that should be removed from hosts in different
  Ansible groups. Only one level of this variable is supported, so you should
  be careful about your inventory design. Or, you can use it as a master list
  that contains different per-group variables.

:envvar:`apt_uninstall__host_packages`
  This variable should be used in
  :file:`ansible/inventory/host_vars/<hostname>/apt_uninstall.yml` files and is meant
  to contain list of packages that should be removed from specific hosts.

Example playbook
----------------

``debops.apt_uninstall`` is designed to be used from a playbook or a role as role
dependency. Here's an example configuration:

.. literalinclude:: ../../../../ansible/playbooks/service/apt_uninstall.yml
   :language: yaml
   :lines: 1,6-
