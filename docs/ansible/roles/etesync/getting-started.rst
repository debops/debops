.. Copyright (C) 2020 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:

Example inventory
-----------------

To configure EteSync on a given remote host, it needs to be added to the
``[debops_service_etesync]`` Ansible inventory group:

.. code-block:: none

   [debops_service_etesync]
   hostname


Example playbook
----------------

Here's an example playbook that can be used to manage EteSync:

.. literalinclude:: ../../../../ansible/playbooks/service/etesync.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::etesync``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::etesync:config``
  Run tasks related to EteSync configuration.

``role::etesync:show_url``
  Print URL entry point if EteSync is deployed on a subpath.
