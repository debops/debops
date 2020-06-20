.. Copyright (C) 2020 Pedro Luis Lopez <pedroluis.lopezsanchez@gmail.com>
.. Copyright (C) 2020 Innobyte Bechea Leonardo <https://www.innobyte.com/>
.. Copyright (C) 2020 Innobyte Alin Alexandru <https://www.innobyte.com/>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Getting started
===============

.. only:: html

   .. contents::
      :local:

``debops.influxdb`` role is only the "client" part. To have a working
InfluxDB installation, you also need to setup the ``debops.influxdb_server``
role somewhere. It can be either on the same host, or on a separate host.
See the ``debops.influxdb_server`` documentation to learn how to install the
database server itself.

Local database server
~~~~~~~~~~~~~~~~~~~~~

If the database server is installed locally, it will be automatically detected
and used by the ``debops.influxdb`` role without any additional configuration. Also,
if a remote server was used previously, and a local one was installed, it will
automatically override the remote configuration. You might need to recreate the
databases and user accounts in that case.

Remote database server
~~~~~~~~~~~~~~~~~~~~~~

If your InfluxDB server is configured on a remote host and you don't have
a local installation, ``debops.influxdb`` will detect that and won't manage the
databases/user accounts without a server specified. To point it to a server,
you need to set a variable in the inventory:

.. code-block:: yaml

   influxdb__server: 'influxdb.example.org'

This needs to be a FQDN address of a host with InfluxDB server installed. DNS
name is required because this access is via a HTTP(S) API. Currently only 1
server at a time is supported by the role.

If :ref:`debops.pki` role is used to configure a PKI environment, with default
``domain`` PKI realm enabled, ``debops.influxdb_server`` role will configure
the provided private keys and X.509 certificates to enable TLS connections to
the database by default.

If the PKI environment is not configured or disabled, connections to the
database server will be performed in cleartext, so you might want to consider
securing them by configuring server on a separate internal network, or
accessing it over a VPN connection. You can use ``debops.subnetwork``,
:ref:`debops.tinc` and :ref:`debops.dnsmasq` Ansible roles to set up a VPN internal
network to secure communication between hosts.

Example inventory
~~~~~~~~~~~~~~~~~

To enable InfluxDB client support on a host, you need to add that host to
``[debops_service_influxdb]`` Ansible group:

.. code-block:: none

   [debops_service_influxdb]
   hostname

When InfluxDB server is properly configured, or installed locally, you can
create user accounts and databases using inventory variables:

.. code-block:: yaml

   influxdb__databases:

     - name: 'application_production'

   influxdb__users:

     - name: 'application'
       grants:
          - database: 'application_production'
            privilege: 'ALL'

Example playbook
~~~~~~~~~~~~~~~~

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.influxdb`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/influxdb.yml
   :language: yaml
   :lines: 1,7-

Ansible tags
~~~~~~~~~~~~

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::influxdb``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
