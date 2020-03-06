.. Copyright (C) 2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Example inventory
-----------------

``debops.locales`` is included by default in the :file:`common.yml` DebOps
playbook; you don't need to do anything to have it executed.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.locales`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/locales.yml
   :language: yaml
   :lines: 1,5-
