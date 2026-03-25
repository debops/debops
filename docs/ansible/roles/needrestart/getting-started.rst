.. Copyright (C) 2026 seven-beep <ebn@entreparentheses.xyz>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:

Example inventory
-----------------

``debops.needrestart`` is included by default in the :file:`common.yml`
DebOps playbook; you don't need to do anything to have it installed.

If you want to remove DebOps :program:`needrestart` configurations on a host or
set of hosts, you can do this by the setting variable:

.. code:: YAML

   needrestart__enabled: false

in Ansible's inventory. The ``needrestart`` package won't be installed.
If it is already present on the host, it won't be removed, but its
configuration will be reset to the distribution defaults.

Example playbook
----------------

Here's an example playbook that can be used to enable and manage the
``needrestart`` service on a set of hosts:

.. literalinclude:: ../../../../ansible/playbooks/service/needrestart.yml
   :language: yaml
   :lines: 1,5-
