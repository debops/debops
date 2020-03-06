.. Copyright (C) 2013-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2014-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Example inventory
-----------------

The ``debops.auth`` role is included in the :file:`common.yml` DebOps playbook
and doesn't need to be specifically activated.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.auth`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/auth.yml
   :language: yaml
   :lines: 1,5-
