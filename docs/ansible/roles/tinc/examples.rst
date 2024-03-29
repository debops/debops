.. Copyright (C) 2015-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2015-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Examples
========

Minimal
-------

Minimal configuration of a default Tinc ``mesh0`` VPN:

.. code-block:: yaml

   tinc__networks:
     'mesh0':
       port: '655'


Per-group VPN
-------------

Create a separate Tinc network with a specific group of hosts included in the
``[tinc_vpn]`` Ansible inventory group:

.. code-block:: yaml

   # inventory/group_vars/tinc_vpn/tinc.yml
   tinc__group_networks:
     'vpn0':
       port: '656'
       inventory_groups: 'tinc_vpn'
       connect_to: '{{ groups.tinc_vpn }}'


Star network
------------

Create a star network with 192.0.2.0/24 with the master connecting to the slaves:

.. code-block:: yaml

   # master node:
   tinc__host_networks:
     'star0':
       address: "192.0.2.254/24"
       connect_to: 'slave01'
       connect_to: 'slave02'
       bridge: [ 'br0' ]

   # slave01 node:
   tinc__host_networks:
     'star0':
       address: "192.0.2.1/24"
       host_address: "{{ ansible_host }}"

   # slave02 node:
   tinc__host_networks:
     'star0':
       address: "192.0.2.2/24"
       host_address: "{{ ansible_host }}"


IPv6 over IPv4 tunnel
---------------------

Obtain IPv6 connectivity while in an IPv4-only network.

This assumes a ``[tinc_dualstack]`` group with IPv4-accessible hosts and a
``[tinc_ipv4only]`` group for hosts that need a tunnel.

Hosts in ``[tinc_dualstack]`` should have the `tap` interface bridged via
`br0` to an interfaces that is receiving router advertisements.
See :ref:`debops.ifupdown` for information on how to do that and
:ref:`debops.radvd` if you need to set up router advertisement.

Note that if you bridge the `tap` interface to a wired interface in the
``[tinc_ipv4only]`` hosts, you may be providing IPv6 to the whole network.

.. code-block:: yaml

   # inventory/group_vars/tinc_dualstack/tinc.yml
   'six_tunnel':
      port: '49180'
      link_type: 'static'
      bridge: 'br0'

   # inventory/group_vars/tinc_ipv4only/tinc.yml
   'six_tunnel':
      port: '49180'
      link_type: 'dynamic'
      connect_to: '{{ groups.tinc_dualstack }}'
