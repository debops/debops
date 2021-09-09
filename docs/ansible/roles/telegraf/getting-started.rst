.. Copyright (C) 2021 Dr. Serge Victor <https://dr.sergevictor.eu/>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Getting started
===============

.. only:: html

   .. contents::
      :local:

Example inventory
-----------------

To install a Telegraf agent on a host, you need to add it to
``[debops_service_telegraf]`` Ansible group:

.. code-block:: none

   [debops_service_telegraf]
   agent-host

This will install ``telegraf`` package and configure a dummy input and output
plugins which are required to run the service.

Example playbook
----------------

Here's an example Ansible playbook that uses the ``debops.telegraf``
role:

.. literalinclude:: ../../../../ansible/playbooks/service/telegraf.yml
   :language: yaml
   :lines: 1,7-
