Getting started
===============

.. contents::
   :local:

Quick start guide
-----------------

Here are some quick examples to get you started if you already know how to use
DebOps roles. These examples are supposed to go into your Ansible inventory,
specifically to the host configuration, for example
:file:`ansible/inventory/host_vars/<hostname>/ifupdown.yml`.

Create an anonymous bridge:

.. code-block:: yaml

   ifupdown__host_interfaces:
     'br2': {}

Create a bridge with static IP address and IPv4 NAT using SNAT translation:

.. code-block:: yaml

   ifupdown__host_interfaces:
     'br2':
       inet: 'static'
       inet6: 'static'
       addresses: [ '192.0.2.1/24', '2001:db8:feed:beef::1/64' ]
       nat: True


Default network configuration
-----------------------------

Without any additional configuration, ``debops.ifupdown`` role will try to
select one of two default interface layouts depending on whether the host is an
OpenVZ/LXC container or not. If it's a container, the role will use the
``dynamic`` interface layout which defines 1 or 2 network interfaces that are
configured via DHCP (IPv4) and SLAAC (IPv6).

If the host is not a container, the role will select the ``bridge`` layout,
which defines 1 or 2 network interfaces with attached bridges that are
configured with DHCP (IPv4) and SLAAC (IPv6). This configuration is beneficial
when a machine is used as a KVM, LXC or even a Docker host. With the bridges
in place you can connect the VMs or containers to your external or internal
network with ease.


Automatic upgrades from older version
-------------------------------------

The ``debops.ifupdown`` role tracks its own version used on a host using the
:ref:`debops.debops_fact` as an intermediary. If the currently applied
version is older than ``0.3.0`` or the version cannot be found, role will
remove the :file:`/etc/network/interfaces.config.d/` directory to make sure
that the network configuration state is consistent. You might want to review
and update your interface configuration in the Ansible inventory before
applying a new version of the role to ensure that it has accurate information
about interfaces present on the host.

Example inventory
-----------------

To enable the :command:`ifupdown` interface management, you need to add the
host to the ``[debops_service_ifupdown]`` Ansible inventory group:

.. code-block:: none

   [debops_service_ifupdown]
   hostname

The role does not check if the host can manage network interfaces, therefore
you should only enable this role on hosts that are allowed to do so. One
of the limiting factors can be the presence of the ``cap_net_admin`` POSIX
capability. Make sure that it is present on the host so that it can manage its
own networking.

.. _ifupdown__ref_example_playbook:

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.ifupdown`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/ifupdown.yml
   :language: yaml
