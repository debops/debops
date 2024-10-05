.. Copyright (C) 2024 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2024 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Getting started
===============

.. only:: html

   .. contents::
      :local:

Default configuration
---------------------

The default installation deploys InfluxDBv2 behind the :command:`nginx`
webserver using the :ref:`debops.nginx` role, with automatic HTTPS support
provided by the :ref:`debops.pki` role. By default the user interface will be
deployed on the host's FQDN, controlled by the :envvar:`influxdb2__fqdn`
default variable.


Example inventory
-----------------

To install InfluxDBv2 on a host, you need to add it to
the ``[debops_service_influxdb2]`` Ansible group:

.. code-block:: none

   [debops_service_influxdb2]
   database-host

This will install the ``influxdb2`` and ``influxdb2-cli`` packages from the
InfluxData repositories (InfluxDB v2.x is currently not available in Debian).

After role deployment, users need to initialize the service and create an
initial user account and organization. This can be done by using the web
interface or, preferably, by logging in to the :command:`influx setup` command.
The command line option will automatically create a corresponding
:file:`~/.influxdbv2/configs` configuration file and make latter use of the
:command:`influx` commands easier.


Example playbook
----------------

Here's an example Ansible playbook that uses the ``debops.influxdb2`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/influxdb2.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::influxdb2``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``skip::influxdb2``
  Main role tag, should be used in the playbook to skip all of the role tasks.
