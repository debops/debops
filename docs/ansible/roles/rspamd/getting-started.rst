.. Copyright (C) 2021 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Example inventory
-----------------

To enable the :command:`rspamd` service on a host, you need to add it to the
``[debops_service_rspamd]`` Ansible inventory group. The host should also be
configured with a Redis server via the :ref:`debops.redis_server` role (see its
documentation for more details), unless a Redis server already exists
somewhere in the network:

.. code-block:: none

   [debops_service_redis_server]
   hostname

   [debops_service_rspamd]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.rspamd`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/rspamd.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::rspamd``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.rspamd`` Ansible role:

- Manual pages: :man:`rspamd(8)`, :man:`rspamc(1)`, :man:`rspamadm(1)` and
  `rspamd_stats(8)`

- The website of the `Rspamd Project`__, in particular the
  `configuration documentation`__

  .. __: https://rspamd.com/
  .. __: https://rspamd.com/doc/configuration/index.html
