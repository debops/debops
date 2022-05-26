.. Copyright (C) 2022 Julien Lecomte <julien@lecomte.at>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

Default configuration
---------------------

The service will be configured to only reboot if necessary unless forced via
a variable.

Caveat
------

If *display_skipped_hosts* is set to *False* in your *ansible.cfg*, the playbook
will print the task reboot information after the reboot.

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.reboot`` role:

.. literalinclude:: ../../../../ansible/playbooks/reboot.yml
   :language: yaml
   :lines: 1,5-
