.. Copyright (C) 2021 Julien Lecomte <julien@lecomte.at>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

Default configuration
---------------------

The role does not specify any DLNA media directories by default. You will need
to configure them using the provided variable :envvar:`minidlna__media_dirs`.

Example inventory
-----------------

To enable MiniDLNA service on a host it needs to be included in the specific Ansible
inventory group:

.. code-block:: none

   [debops_service_minidlna]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.minidlna`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/minidlna.yml
   :language: yaml
   :lines: 1,5-
