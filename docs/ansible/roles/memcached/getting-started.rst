.. Copyright (C) 2015-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Example inventory
-----------------

To install the ``memcached`` service on a host, you can add it in the ``[debops_service_memcached]``
Ansible inventory group:

.. code-block:: none

    [debops_service_memcached]
    hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.memcached`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/memcached.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::memcached``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
