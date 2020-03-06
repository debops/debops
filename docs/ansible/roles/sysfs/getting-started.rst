.. Copyright (C) 2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Default configuration
---------------------

The ``sysfs`` configuration will not be applied by default in a container
environment (LXC, OpenVZ), since these environments usually have the ``/sys``
filesystem mounted read-only. You can control this using the
:envvar:`sysfs__enabled` variable.


Example inventory
-----------------

To configure the ``/sys`` kernel filesystem on a host by the ``debops.sysfs``
role, that host needs to be added to the ``[debops_service_sysfs]`` Ansible
inventory group:

.. code-block:: none

   [debops_service_sysfs]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.sysfs`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/sysfs.yml
   :language: yaml
   :lines: 1,5-
