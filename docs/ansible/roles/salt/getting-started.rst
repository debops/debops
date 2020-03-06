.. Copyright (C) 2014-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2014-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Example inventory
-----------------

To enable management of the Salt Master service, a given host needs to be added
to the ``[debops_service_salt]`` Ansible inventory group:

.. code-block:: none

   [debops_service_salt]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.salt`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/salt.yml
   :language: yaml
   :lines: 1,5-
