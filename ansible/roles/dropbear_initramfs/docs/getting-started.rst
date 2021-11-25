.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. include:: includes/all.rst

.. contents::
   :local:


Example inventory
-----------------

To setup the dropbear ssh server in initramfs of a given host or a set of hosts, they need to
be added to the ``[debops_service_dropbear_initramfs]`` Ansible group in the inventory:

.. code:: ini

   [debops_service_dropbear_initramfs]
   hostname

Example playbook
----------------

Here's an example playbook that uses the ``debops-contrib.dropbear_initramfs`` role:

.. literalinclude:: playbooks/dropbear_initramfs.yml
   :language: yaml
   :lines: 1,5-

The playbook is shipped with this role under
:file:`./docs/playbooks/dropbear_initramfs.yml` from which you can symlink it
to your playbook directory.
In case you use multiple `DebOps Contrib`_ roles, consider using the
`DebOps Contrib playbooks`_.

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::dropbear_initramfs``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::dropbear_initramfs:pkgs``
  Tasks related to system package management like installing or
  removing packages.
