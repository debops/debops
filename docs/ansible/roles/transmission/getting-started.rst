.. Copyright (C) 2021 Julien Lecomte <julien@lecomte.at>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

Default configuration
---------------------

The service will be configured to download files into the default
:file:`/var/lib/transmission/Downloads` directory.

Example inventory
-----------------

To enable transmission service on a host it needs to be included in the specific Ansible
inventory group:

.. code-block:: none

   [debops_service_transmission]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.transmission`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/transmission.yml
   :language: yaml
   :lines: 1,5-
