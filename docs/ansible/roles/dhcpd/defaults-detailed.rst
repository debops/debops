.. Copyright (C) 2014-2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2020 CipherMail B.V. <https://www.ciphermail.com/>
.. Copyright (C) 2014-2018, 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variables: configuration
================================

Some of the ``debops.dhcpd`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _dhcpd__ref_classes:

dhcpd__classes
--------------

Here you can define host classes and custom options for each class.

``name``
  Required. Name of the host class.

``comment``
  Optional. Comment added in the configuration file.

``options``
  Optional. Text block with options for a particular class scope.

``subclasses``
  Optional. List of subclasses. Each list item should be specified as a dict,
  the following keys are recognized:

    - ``submatch``: Required. A hashed submatch expression.
    - ``comment``: Optional. Comment added to the configuration file.
    - ``options``: Optional. Text block with options for a particular subclass
      scope.

Examples::

  dhcpd__classes:

    - name: 'empty-class'

    - name: 'allocation-class-2'

      options: |
        match pick-first-value (option dhcp-client-identifier, hardware);

      subclasses:

        - submatch: '1:8:0:2b:a9:cc:e3'

        - submatch: '1:08:00:2b:a1:11:31'
          options: |
            option root-path "samsara:/var/diskless/alphapc";
            filename "/tftpboot/netbsd.alphapc-diskless";

.. _dhcpd__ref_failovers:

dhcpd__failovers
----------------

Each 'failover pair' declaration consists of a primary and secondary host. No
more than two nodes are allowed in an ISC DHCP failover cluster.

You must specify which failover pair each pool should use by listing the name of
the failover in each pool declaration, for example::

    dhcpd__failovers:
      - name: 'my-failover'
        primary: '192.0.2.1'
        secondary: '192.0.2.2'
        split: 128

    dhcpd__subnets:
      - subnet: '192.0.2.0/24'
        routers: [ '192.0.2.1' ]
        pools:
          - comment: 'My pool with failover'
            failover: 'my-failover'
            ranges: [ '192.0.2.3 192.0.2.254' ]

Each failover declaration has a set of mandatory fields, which are:

``primary``
  IPv4 address of the primary DHCP server.

``secondary``
  IPv4 address of the secondary DHCP server.

``mclt``
  Max Client Lead Time. This is the maximum amount of time that one server can
  extend a lease for a DHCP client beyond the time known by the partner server.

  Default value: ``3600``

Split configuration between two failover DHCP servers (you must specify one of
'split' or 'hba', never both):

``split``
  Split value between ``0`` and ``255``.

  Specifies the split between the primary and secondary servers for the purpose
  of load balancing. Whenever a client makes a DHCP request, the DHCP server
  runs a hash on the client identification, resulting in a value from 0 to 255.
  This is used as an index into a 256 bit field. If the bit at that index is
  set, the primary is responsible. If the bit at that index is not set, the
  secondary is responsible.

``hba``
  32 character string in the regexp: ``([0-9a-f]{2}:){32}``

  Specifies the split between the primary and secondary as a bitmap rather than
  a cutoff, which theoretically allows for finer-grained control. In practice
  however, there is probably no need for such fine-grained control.

You must use either the 'split' or the 'hba' statement. Split has a preference,
so if it's defined, 'hba' will be omitted by the configuration template.

``max_response_delay``
  Tells the DHCP server how many seconds may pass without receiving a message
  from its failover peer before it assumes that the connection has failed.

  Default value: ``60``

``max_unacked_updates``
  Tells the remote DHCP server how many ``BNDUPD`` messages it can send before
  it receives a ``BNDACK`` from the local system.

  Default value: ``10``

Optional fields are mostly described in :man:`dhcpd.conf(5)`:

``load_balance_max_seconds``
  A cutoff after which load balancing is disabled.

  Default value: ``5``

``auto_partner_down``
  Number of seconds to wait after a communications failure until the server
  starts allocating leases from the partner's free lease pool. This feature is
  disabled by default.

``max_lease_misbalance``
  Configures the percentage of allowed misbalance between the failover pools. If
  the "Leases to Send" value exceeds this percentage, the leases are moved to
  the other server.

  Default value: ``15``

``max_lease_ownership``
  Percentage that defines the lower boundary of the allowed misbalance. This
  value should be lower than the value selected in ``max_lease_misbalance``.

  Default value: ``10``

``min_balance``
  Minimum number of seconds to wait before rebalancing.

  Default value: ``60``

``max_balance``
  Maximum number of seconds to wait before rebalancing.

  Default value: ``3600``

The role specifies additional templating options:

``comment``
  A comment to add in the configuration file.

``options``
  Text block containing custom options for this failover configuration.

Examples::

  dhcpd__failovers:
  - failover: 'my-failover'
    primary: '192.0.2.1'
    secondary: '192.0.2.2'
    split: 128

.. _dhcpd__ref_groups:

dhcpd__groups
-------------

Group related configuration together.

``comment``
  Optional. Comment added in the configuration file.

``options``
  Optional. Text block with options for a particular group.

``hosts``
  Optional. List of hosts to include in this group. Use the same format as the
  ``dhcpd__hosts`` list.

``groups``
  Optional. List of groups to include in this group.

``subnets``
  Optional. List of subnets to include in this group. Use the same format as the
  ``dhcpd__subnets`` list.

``shared_networks``
  Optional. List of shared networks to include in this group. Use the same format as the
  ``dhcpd__shared_networks`` list.

Examples::

    dhcpd__groups:
      - comment: 'First group'
        options: |
          filename "Xncd19r";
          next-server ncd-booter;
        hosts:
          - name: 'ncd1'
            ethernet: '00:c0:c3:49:2b:57'
            address4: '192.0.2.3'
        groups: '{{ dhcpd__group_second }}'

    # An example of group nesting
    dhcpd__group_second:
      - comment: 'Second group'
        hosts:
          - name: 'ncd2'
            ethernet: '00:c0:c3:88:2d:81'
            address4: '192.0.2.4'

.. _dhcpd__ref_hosts:

dhcpd__hosts
------------

Define hosts with static lease assignments.

``hostname``
  Required. The hostname.

``ethernet``
  Required if ``address4`` is set. Ethernet address of this host.

``address4``
  Optional. IPv4 address of this host.

``address6``
  Optional. IPv6 address of this host.

``comment``
  Optional. A comment added in the configuration file.

``options``
  Optional. Text block containing custom options for this host.

Examples::

  dhcpd__hosts:
    - hostname: 'ncd1'
      address4: '192.0.2.3'
      address6: '2001:db8::3'
      ethernet: '00:c0:c3:49:2b:57'

.. _dhcpd__ref_keys:

dhcpd__keys
-----------

This list lets you define symmetric keys used to update DNS zones with
information configured using DHCP.

``name``
  Required. Name of the key.

``algorithm``
  Required. Name of the algorithm to use, for example ``hmac-sha256``.

``secret``
  Required. Symmetric key shared between the DHCP and DNS servers.

``comment``
  Optional. A comment added in the configuration file.

``options``
  Optional. Text block containing custom options for this key.

Examples::

  dhcpd__keys:
    - name: 'secure-key'
      algorithm: 'hmac-sha256'
      secret: '{{ lookup("file", secret + "/dhcpd/tsig-keys/secure-key") }}'

.. _dhcpd__ref_shared_networks:

dhcpd__shared_networks
----------------------

List of shared networks which combine specified subnets together.

``name``
  Required. Name of the shared network.

``subnets``
  Required. List of subnets included in this shared network. Use the same format
  as the :ref:`dhcpd__ref_subnets` list.

``comment``
  Optional. A comment added in the configuration file.

``options``
  Optional. Text block containing custom options for this shared network.

Examples::

    dhcpd__shared_networks:
      - name: 'shared-net'
        comment: 'Local shared network'
        options: |
          default-lease-time 600;
          max-lease-time 900;
        subnets:
          - subnet: '192.0.2.0/24'
            routers: [ '192.0.2.1' ]

          - subnet: '198.51.100.0/24'
            routers: [ '198.51.100.1', '198.51.100.2' ]
            options: |
              default-lease-time 300;
              max-lease-time 7200;
            pools:
              - comment: "A pool in a subnet"
                ranges: [ '198.51.100.3 198.51.100.254' ]

.. _dhcpd__ref_subnets:

dhcpd__subnets
--------------

List of subnets.

``subnet``
  Required. The subnet, in CIDR notation (e.g. ``192.0.2.0/24`` or
  ``2001:db8::/64``).

``comment``
  Optional. A comment added in the configuration file.

``options``
  Optional. Text block containing custom options for this subnet.

``routers``
  Optional. List of IP addresses of the routers for this subnet. This option is
  not applicable to IPv6 subnets as NDP is used there to discover the routers.

``ranges``
  Optional. List of address ranges for dynamic lease assignment. The format of
  each range item is '<first address><space><last address>' for both IPv4 and
  IPv6, but you can use CIDR notation for IPv6 as well.

``pools``
  Optional. List of address pools within the subnet. Each pool must be specified
  as a dict, the following keys are recognized:

  - ``comment``: a comment added in the configuration file.

  - ``options``: text block containing custom options for this pool.

  - ``ranges``: list of address ranges for dynamic lease assignment. The format
    of each range item is '<first address><space><last address>' for both IPv4
    and IPv6, but you can use CIDR notation for IPv6 as well.

Examples::

    dhcpd__subnets:
      - subnet: '192.0.2.0/24'
        comment: 'Example IPv4 subnet'
        pools:
          - comment: 'Reserved for static assignments'
            options: |
              deny unknown-clients;
            ranges: [ '192.0.2.2 192.0.2.49' ]

          - comment: 'Pool for dynamic clients'
            ranges: [ '192.0.2.50 192.0.2.254' ]

      - subnet: '2001:db8::/64'
        comment: 'Example IPv6 subnet'
        pools:
          - ranges:
              - '2001:db8::1:0 2001:db8::1:ffff'
              - '2001:db8::2:0/112'

.. _dhcpd__ref_zones:

dhcpd__zones
------------

This list lets you define DNS zones to update with information configured using
DHCP.

``zone``
  Required. DNS domain name of a zone, needs to end with a dot (``.``)

``primary``
  Required. IP address of the primary DNS server for the specified zone.

``key``
  Required. Name of the symmetric key (specified in :ref:`dhcpd__ref_keys`) used
  to authorize DNS updates for this zone.

``comment``
  Optional. A comment added in the configuration file.

``options``
  Optional. Text block containing custom options for this zone.

Examples::

  dhcpd__zones:
    - zone: "example.org."
      primary: "192.0.2.1"
      key: "secure-key"
