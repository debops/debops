.. Copyright (C) 2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Example inventory
-----------------

To enable Green Unicorn service on a host, that host should be added to to
a specific Ansible inventory group:

.. code-block:: none

   [debops_service_gunicorn]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.gunicorn`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/gunicorn.yml
   :language: yaml
   :lines: 1,5-
