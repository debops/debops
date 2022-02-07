.. Copyright (C) 2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _icinga__ref_deployment:

Deployment guide
================

.. only:: html

   .. contents::
      :local:


Deployment design
-----------------

The Icinga 2 support in DebOps is designed around installation of Icinga Agents
on all hosts and presence of 1 master/director node. The Icinga 2 Director is
not mandatory, without it the ``debops.icinga`` role can be used to configure
Icinga 2 nodes manually, either through Ansible inventory or via role dependent
variables. However, with Icinga Director, the role can register new Icinga
nodes automatically as long as the specified host templates are prepared
beforehand.

It's advisable to test the deployment in a development environment before
applying it in production. This should let you find out possible issues with
DNS and PKI configuration you might encounter.


Icinga 2 inter-node communication and PKI
-----------------------------------------

You might need to allow connections to the Icinga API interface, by default on
port 5665, through the firewall. You can do this by setting the
:envvar:`icinga__allow` or its group or host equivalent in the inventory.
Usually only the master host needs the access opened, unless you plan to
initiate connections from the master to the clients.

Icinga 2 uses X.509 certificates for internal communication between the nodes,
therefore the correct DNS records for the hosts are required. When DNS is not
configured properly beforehand, communication between the cluster nodes can be
disrupted.

At the moment, the :ref:`debops.icinga` role uses the PKI infrastructure
maintained by the :ref:`debops.pki` role to provide X.509 certificates for
Icinga 2 agents. Due to that, automatic registration of the Icinga 2 agents
external to the cluster in the Icinga 2 CA is not possible at this time. It can
be implemented later if there's demand for it.


.. _icinga__ref_dns_config:

DNS SRV records
---------------

The role detects the master and director servers by using
:ref:`dns_configuration_srv` for the following services:

.. code-block:: none

   _icinga-master._tcp.{{ icinga__domain }} (default port 5665)
   _icinga-director._tcp.{{ icinga__domain }} (default port 443)

There can be multiple master and director DNS SRV records. The role will
configure multiple master nodes in the :file:`zones.conf` configuration file,
however only one director node will be used.

.. warning:: The role uses the DNS SRV resource records to determine if a given
             host should be configured as the "master" host, or a client host
             that should regist itself with the "master". Therefore, you should
             create the DNS SRV records *beforehand*, as all the Icinga 2 nodes
             will see themselves as "master" nodes otherwise, and won't connect
             to the "master" node.

For details on how to configure DNS SRV records, see
:ref:`dns_configuration_srv`.


Initial deployment
------------------

This is an example Ansible inventory for deployment of the full Icinga "stack"
in DebOps environment. The :ref:`debops.icinga` role is applied on all hosts in
the environment, however the :ref:`debops.icinga_db` and
:ref:`debops.icinga_web` are applied only on the master host.

.. code-block:: none

   [debops_all_hosts]
   icinga-master
   hostname1
   hostname2

   [debops_service_icinga:children]
   debops_all_hosts

   [debops_service_postgresql_server]
   icinga-master

   [debops_service_icinga_db]
   icinga-master

   [debops_service_icinga_web]
   icinga-master

By default the web interface is configured on the ``icinga.`` subdomain, you
can change this by setting the :envvar:`icinga_web__fqdn` variable.

It's best to start the deployment on the Icinga master node, by setting up the
local Icinga 2 Agent, and the web interface with the Icinga Director. You can
login to the web interface using the ``root`` username and the password stored
in the
:file:`secret/icinga_web/auth/<inventory_hostname>/credentials/root/password`
file (see :ref:`debops.secret` for more details).

After logging in, you should create a new basic host template. By default, the
role will try and register the nodes using the ``generic-host`` template. To
create it, go to the "Icinga Director" -> "Hosts" -> "Host Templates" section
and click on "Add". Enter "generic-host" as the "Hostname", set the "Check
command" option as "hostalive". You should also set a reasonable "Check
interval", "Retry interval' and "Max check attempts" fields, for example with
5 minutes, 30 seconds and 5 tries.

It might be best to add a separate host template for hosts with Icinga 2 Agent
installed, in case that you want to include other hosts as well. For this,
create a new template with a chosen name, and in the "Icinga Agent and zone
settings" section set the "Icinga 2 Agent", "Estabilish connection" and
"Accepts config" options to "Yes". You can define the list of templates
automatically applied during registration using the
``icinga__director_register_*_templates`` default variables.

After this you can apply the :ref:`debops.icinga` role to other hosts. If
everything was configured correctly, the role should automatically register
a new host in Icinga via the Director REST API. Subsequent execution of the
role will not change the status of the host in Icinga, but if you remove the
host from the web interface and re-run the :ref:`debops.icinga` role, the host
will be registered again.
