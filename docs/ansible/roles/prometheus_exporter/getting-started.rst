.. Copyright (C) 2026 Patryk Sciborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


What does this role do?
-----------------------

The role installs Prometheus exporters from Debian packages and manages
each one via a systemd drop-in override. Exporters listen on the loopback
interface; a local :ref:`debops.vmagent` instance scrapes them.


Minimal inventory
-----------------

Add hosts to the ``[debops_service_prometheus_exporter]`` group and declare
the exporters in a leaf group (not in the service group itself, to avoid
variable precedence collisions):

.. code-block:: yaml

   # inventory groups
   debops_service_prometheus_exporter:
     children:
       my_hosts:

   # group_vars/my_hosts/prometheus_exporter.yml
   prometheus_exporter__group_exporters:
     - name: 'node'

This installs ``prometheus-node-exporter`` and writes a drop-in so the
service listens on ``127.0.0.1:9100``.


Example playbook
----------------

.. literalinclude:: ../../../../ansible/playbooks/service/prometheus_exporter.yml
   :language: yaml
   :lines: 1,6-


Ansible tags
------------

``role::prometheus_exporter``
  Main role tag.

``skip::prometheus_exporter``
  Skip the main role tasks.
