.. Copyright (C) 2021 Dr. Serge Victor <https://dr.sergevictor.eu/>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Getting started
===============

.. only:: html

   .. contents::
      :local:

Real world use
==============

Telegraf requires at least one input and output defined. Default
``debops.telegraf`` configuration will include a few basic input plugins (cpu,
mem, disk, etc.) but output will be discarded by default using the
``outputs.discard`` plugin.

You can check the :file:`/etc/telegraf/telegraf.conf.sample` file on a host
with installed Telegraf for many examples of input and output plugins available
as well as documentation of the supported configuration options. The
configuration is written using TOML format, however it's very easy to convert
it to a format usable in DebOps, either directly including it as YAML text
blocks, or converting it into a YAML format.


Example inventory
-----------------

To install a Telegraf agent on a host, you need to add it to
``[debops_service_telegraf]`` Ansible group:

.. code-block:: none

   [debops_service_telegraf]
   agent-host

This will install ``telegraf`` package and create basic configuration required
by the service.

You can also configure Telegraf to be installed on all DebOps hosts in the inventory:

.. code-block:: none

   [debops_all_hosts]
   hostname1
   hostname2
   hostname3

   [debops_service_telegraf:children]
   debops_all_hosts


Example playbook
----------------

Here's an example Ansible playbook that uses the ``debops.telegraf``
role:

.. literalinclude:: ../../../../ansible/playbooks/service/telegraf.yml
   :language: yaml
   :lines: 1,7-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::telegraf``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.telegraf`` Ansible role:

- Official `Telegraf documentation page`__

  .. __: https://docs.influxdata.com/telegraf/
