Getting started
===============

.. contents::
   :local:

Because most of the time hosts that are configured by Ansible are remote, the
highest priority for the ``debops.ifupdown`` role is to not lose the network
connectivity. That does not mean that network connection can't ever be stopped
(which it most certainly is), but that network configuration must be in
a consistent, known state at all times.

Default network configuration
-----------------------------

Without any additional configuration, ``debops.ifupdown`` tries to recognize
several different environments and configure them as needed. The parameters
taken into account are:

- if ``cap_net_admin`` POSIX capability is not present when capabilities are
  enabled, network configuration is skipped;

- if network configuration is presumed to be "static" (``static`` anywhere in
  ``/etc/network/interfaces``), network configuration is not performed;

- if NetworkManager is detected, ``debops.ifupdown`` will not configure default
  set of network interfaces, but will work as a role dependency if used in that
  way;

If above conditions are not met, ``debops.ifupdown`` will select one of
available network configurations in ``vars/`` directory based on condition it
detects. Basic network configuration is designed to configure one or two
network interfaces (public network and private network), each one with their
own bridge, getting the required configuration via DHCP requests. If an LXC
guest is detected, normal network interfaces will be configured instead, also
using DHCP.

Example inventory
-----------------

if you are using official DebOps playbooks, ``debops.ifupdown`` role is part of
the ``common.yml`` playbook, which means that it's run by default on all hosts,
and there's no specific host group set to enabled it.

By default ``eth0`` and ``eth1`` network interfaces will be configured with
``br0`` (public network) and ``br1`` (private network) bridges respectively. If
on a given host these ports are reversed or different, you can specify the
correct ones in two variables::

    ifupdown_external_interface: 'eth0'
    ifupdown_internal_interface: 'eth1'

Bridges will be configured to ask DHCP server for their configuration. You can
easily add static IP addresses to selected interfaces if needed, for example
for NAT or virtual IP addresses. To do that, you can use separate dict variable
with IP addresses specified in 'host/prefix' format::

    ifupdown_map_interface_addresses:
      'br0': [ '192.0.2.1/24', '2001:db8:feed:dd05::32/64' ]

Unfortunately you cannot use variables as keys in above dict, only strings;
because of that it's better to correctly specify external/internal interfaces
(which can change) and then configure IP addresses on their respective bridges
(which should have static names).

If you want to define your own interface layout, you can put it in
``ifupdown_interfaces`` list. It will override the automatic selection by the
role, which is very handy when role is used as a dependency::

    ifupdown_interfaces:

      - iface: '{{ ifupdown_external_interface }}'
        type: 'interface'

If, instead, you want to add more interfaces to the set configured
automatically by ``debops.ifupdown``, you can put them in a separate list and
combine two lists together::

    ifupdown_interfaces: '{{ ifupdown_default_interfaces + ifupdown_custom_interfaces }}'

    ifupdown_custom_interfaces:

      - iface: 'tap0'
        type: 'interface'
        options: |
          address 0.0.0.0

Example playbook
----------------

You can use ``debops.ifupdown`` in your own playbooks and roles, as
a dependency. For example, below playbook will configure a new bridge without
adding any network interfaces to it::

    ---

    - name: Configure network interfaces
      hosts: all
      sudo: True

      roles:
        - role: debops.ifupdown
          ifupdown_interfaces:

            - iface: 'br2'
              type: 'bridge'
              inet: 'static'
              addresses: '{{ "10.10.1.0/24" | ipaddr(host_index | int) }}'
              gateway: '10.10.1.1'
              bridge_ports: [ 'eth0', 'eth1' ]
              options: |
                bridge_stp on
                bridge_fd 0

And then, in each host inventory, set its specific index::

    host_index: 2

Above configuration can be seen as crude implementation of DHCP using
semi-automatic incrementing IP addresses. Setting up proper DHCP server, for
example with ``debops.dnsmasq`` or ``debops.dhcpd`` might be easier and more
benefical in the long run.

