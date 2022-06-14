.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2017-2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

Example inventory
-----------------

To setup the dropbear ssh server in initramfs of a given host or a set of hosts, they need to
be added in the specific Ansible inventory group ``debops_service_dropbear_initramfs``:

.. code:: ini

   [debops_service_dropbear_initramfs]
   hostname

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.dropbear_initramfs`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/dropbear_initramfs.yml
   :language: yaml
   :lines: 1,5-

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

``skip::dropbear_initramfs``
  Tag used to skip the playbook in a run.

``role::dropbear_initramfs:pkgs``
  Tasks related to system package management like installing or
  removing packages.
