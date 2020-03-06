.. Copyright (C) 2016-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2016-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:

.. include:: includes/role.rst
   :start-line: 6

Example inventory
-----------------

To manage Apache on a given host or set of hosts, they need to be added
to the ``[debops_service_apache]`` Ansible group in the inventory:

.. code:: ini

   [debops_service_apache]
   hostname

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.apache`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/apache.yml
   :language: yaml
   :lines: 1,5-

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::apache:env``
  Environment role tag, should be used in the playbook to execute a special
  environment role contained in the main role. The environment role prepares
  the environment for other dependency roles to work correctly.

``role::apache``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::apache:pkgs``
  Tasks related to system package management like installing or removing
  packages.

``role::apache:modules``
  Tasks related to Apache modules.

``role::apache:vhosts``
  Tasks related to Apache virtual hosts.
