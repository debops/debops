Getting started
===============

.. include:: ../../../includes/global.rst

.. contents::
   :local:

Default configuration
---------------------

By default, the role configures :command:`dnsmasq` to act as a caching and
forwarding DNS server for the local machine. Additional configuration like
support for Consul DNS service and LXC subdomain managed by the
:ref:`debops.lxc` role is enabled when detected.

The initial configuration is designed with nested hierarchy of DNS servers in
mind: by default answers about private IP addresses from external DNS servers
are blocked to avoid rebinding, but the hosts' own domain, as well as its
parent domain are exempt from this, as long as the parent domain has 3 or more
levels. The filtering of PTR requests will be disabled when the upstream
nameservers are located in a private IP address ranges, or local LXC
configuration is detected, to allow revDNS requests to be resolved.

If the host has the ``br2`` network interface, it is assumed to be a local
private network, and DHCP/DNS/PXE services are configured for it. The role will
automatically create relevant configuration based on the IP addresses defined
on the interface, as well as publish a DNS domain based on the interface name;
this can be controlled using the :ref:`dnsmasq__ref_interfaces` configuration
variables. The role will automatically configure support for iPXE service
managed by :ref:`debops.ipxe` role to allow customized PXE boot menus.


Example inventory
-----------------

Hosts added to the ``debops_service_dnsmasq`` inventory group will have the
``dnsmasq`` installed and configured.

.. code:: ini

   [debops_service_dnsmasq]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.dnsmasq`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/dnsmasq-plain.yml
   :language: yaml

If you are using this role without DebOps, here's an example Ansible playbook
that uses ``debops.dnsmasq`` together with the :ref:`debops.persistent_paths`:

.. literalinclude:: ../../../../ansible/playbooks/service/dnsmasq-persistent_paths.yml
   :language: yaml

If you are using this role without DebOps, here's an example Ansible playbook
that uses ``debops.dnsmasq`` together with the ``debops-contrib.apparmor`` role:

.. literalinclude:: examples/dnsmasq-apparmor.yml
   :language: yaml


:ref:`debops.persistent_paths` support
--------------------------------------

In case the host in question happens to be a TemplateBasedVM on `Qubes OS`_ or
another system where persistence is not the default, it should be absent in
``debops_service_dnsmasq`` and instead be added to the
``debops_service_dnsmasq_persistent_paths`` Ansible inventory group
so that the changes can be made persistent:

.. code:: ini

   [debops_service_dnsmasq_persistent_paths]
   hostname

The :envvar:`dnsmasq__base_packages` are expected to be present (typically
installed in the TemplateVM).

Note that you will need to set ``core__unsafe_writes`` to ``True`` when you
attempt to update the configuration on a system that uses bind mounts for
persistence. You can set ``core__unsafe_writes`` directly in your inventory
without the need to run the ``debops.core`` role for this special case.
Refer to `Templating or updating persistent files`_ for details.

.. _Templating or updating persistent files: https://docs.debops.org/en/latest/ansible/roles/debops.persistent_paths/guides.html#templating-or-updating-persistent-files


Other resources
---------------

List of other useful resources related to the ``debops.dnsmasq`` Ansible role:

- Manual pages: :man:`dnsmasq(8)`, :man:`dhcp-options(5)`
