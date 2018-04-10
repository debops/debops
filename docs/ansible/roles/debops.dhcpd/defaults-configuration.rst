Default variables: configuration
================================

Some of ``debops.dhcpd`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _dhcpd_keys:

dhcpd_keys
----------

This list lets you define symmetric keys used to update dynamic DNS with
information configured using DHCP.

``key``
  Name of the key used to select it in specific scope

``algorithm``
  Name of the algorithm to use for key encryption

``secret``
  Encrypted symmetric key shared between DHCP and DNS servers

``comment``
  An optional comment added in the configuration file

Examples::

  # Read the secret key from an external file
  dhcpd_secret_secure_key: '{{ lookup("password",
                               secret + "/" + ansible_domain +
                               "/shared/ddns/keys/secure-key") }}'

  dhcpd_keys:
    - key: "secure-key"
      algorithm: "hmac-md5"
      secret: "{{ dhcpd_secret_secure_key }}"


.. _dhcpd_zones:

dhcpd_zones
-----------

This list lets you define DNS zones used to update dynamic DNS with information
configured using DHCP.

``zone``
  DNS domain name of a zone, needs to end with a dot (``.``)

``primary``
  Address of the primary DNS server serving the specified zone

``key``
  Name of the symmetric key used to authorize Dynamic DNS updates of the
  specified zone

``comment``
  An optional comment added in the configuration file

Examples::

  dhcpd_zones:
    - zone: "example.org."
      primary: "127.0.0.1"
      key: "secure-key"


.. _dhcpd_classes:

dhcpd_classes
-------------

Here you can define host classes and custom options for each class.

``class``
  Name of the host class

``comment``
  Optional comment added in the configuration file

``options``
  Text block with options for a particular class scope

``include``
  Include an external file

``subclass``
  Dict. You can specify matches for a class in two ways:

  - a dict key without a value will create a simple match for that host. You
    need to specify dict key with colon (``:``) at the end to indicate that
    this is a dict key, see examples below

  - a dict with a text block as a value will create an extended match scope
    with options specified in the text block inside that scope

Examples::

  dhcpd_classes:

    - class: 'empty-class'

    - class: 'allocation-class-1'

      options: |
        match pick-first-value (option dhcp-client-identifier, hardware);

      subclass:
        # Simple match
        '00:11:22:33:44:55':

        # Extended match
        '00:11:22:33:22:11': |
          option root-path "samsara:/var/diskless/alphapc";        
          filename "/tftpboot/netbsd.alphapc-diskless";


.. _dhcpd_groups:

dhcpd_groups
------------

Group related configuration together.

``comment``
  Optional comment added in the configuration file

``options``
  Text block with options for a particular group

``include``
  Include an external file

``groups``
  Include another group definition of the group in this group. Child group
  should be defined in a separate YAML dict. Recursion is not allowed.

``hosts``
  List of hosts included in this group. Use the same format as the
  ``dhcpd_hosts`` list.

``subnets``
  List of subnets included in this group. Use the same format as the
  ``dhcpd_subnets`` list.

Examples::

    dhcpd_groups:
      - comment: 'First group'
        hosts: '/etc/dhcp/dhcpd-group1-hosts.conf'
        groups: '{{ dhcpd_group_second }}'
    
    # An example of group nesting
    dhcpd_group_second:
      - comment: 'Second group'
        hosts: '/etc/dhcp/dhcpd-group2-hosts.conf'


.. _dhcpd_shared_networks:

dhcpd_shared_networks
---------------------

List of shared networks which combine specified subnets together.

``name``
  Name of a shared network

``comment``
  A comment added to this shared network in the configuration

``options``
  Custom options in the text block format for this shared network

``include``
  Include an external file in this shared network scope

``subnets``
  List of subnets included in this shared network. Use the same format as the
  ``dhcpd_subnets`` list.

Examples::

    dhcpd_shared_networks:
      - name: 'shared-net'
        comment: "Local shared network"
        subnets: '{{ dhcpd_subnets_local }}'
        options: |
          default-lease-time 600;
          max-lease-time 900;

    dhcpd_subnets_local:
      - subnet: '10.0.30.0'
        netmask: '255.255.255.0'
        routers: [ '10.0.30.1', '10.0.30.2' ]

      - subnet: '10.0.40.0'
        netmask: '255.255.255.0'
        routers: '19.0.40.1'
        options: |
          default-lease-time 300;
          max-lease-time 7200;
        pools:
          - comment: "A pool in a subnet"
            range: '10.0.30.10 10.0.30.20'


.. _dhcpd_subnets:

dhcpd_subnets
-------------

List of subnets included in a specified group.

``subnet``
  IP address of the subnet. If it's IPv4, it should be the first IP address in
  the subnet, if it's IPv6, it should be specified as the IPv6-prefix.

``netmask``
  If the subnet is IPv4, specify it's netmask in "normal" IP address form, not
  the CIDR form.

``ipv6``
  Set to ``True`` if managed subnet is IPv6.

``routers``
  String (if just one), or list (if many) of IP addresses of the routers for
  this subnet

``comment``
  A comment added to this subnet in the configuration

``options``
  Custom options in the text block format for this subnet

``include``
  Include an external file in this subnet scope

``pools``
  List of different address pools within specified subnet. Each pool should be
  specified as a dict, following keys are recognized:

  - ``range``: a string which defines the range of the specific pool, with IP
    addresses of the start and end delimited by space

  - ``comment``: a comment added to this host in the configuration

  - ``options``: custom options in the text block format for this host

  - ``include``: include an external file in this pool

Examples::

    # List of subnets
    dhcpd_subnets: [ '{{ dhcpd_subnet_default }}' ]

    dhcpd_subnet_default:
      subnet: '{{ ansible_default_ipv4.network }}'
      netmask: '{{ ansible_default_ipv4.netmask }}'
      comment: 'Generated automatically by Ansible'

    # An IPv6 subnet
    example_ipv6_subnet:
      subnet: 'dead:be:ef::/64'
      ipv6: True
      routers: 'dead:be:ef::1'
      comment: "Example IPv6 subnet"
      options: |
        default-lease-time 300;
        max-lease-time 7200;
  
.. _dhcpd_hosts:

dhcpd_hosts
-----------

String or list. If string, include an external file with host list in this
place of the configuration. If list, specify a list of dicts describing the
hosts. Each dict can have following keys:

``hostname``
  Name of the host

``ethernet``
  Ethernet address of this host, if host has multiple aggregated(bonded) links
  you may specify their ethernet addresses as a list.

``address``
  IP address of this host

``comment``
  A comment added to this host in the configuration

``options``
  Custom options in the text block format for this host

Examples::

  # External file with list of hosts
  dhcpd_hosts: '/etc/dhcp/dhcp-hosts.conf'

  # List of hosts
  dhcpd_hosts:
    - hostname: 'examplehost'
      address: '10.0.10.1'
      ethernet: '00:00:00:00:00:00'
    - hostname: 'bondedhost'
      address: '10.0.10.2'
      ethernet:
        - '00:00:00:00:00:01'
        - '00:00:00:00:00:02'

.. _dhcpd_includes:

dhcpd_includes
--------------

List of external files to include in DHCP configuration. Use absolute paths for
the files.

Examples::

    dhcpd_includes:
      - '/etc/dhcp/other-options.conf'

.. _dhcpd_failovers:

dhcpd_failovers
---------------

Each 'failover pair' declaration consists of primary and secondary host,
no more than two nodes failover is currently allowed by ``isc-dhcpd``.

You must specify which failover pair each pool should use by specifying
a 'failover peer' statement under an ``options`` block in each pool
declaration. e.g::

    dhcpd_failovers:
      - failover: "my-failover"
        primary: '10.0.30.1'
        secondary: '10.0.30.2'
        ...

    dhcpd_subnets:
      - subnet: ...
        ...
        pools:
          - comment: "My pool with failover"
            range: '10.0.30.10 10.0.30.20'
            options: |
              failover peer "my-failover";

Each failover declaration has a set of mandatory fields, which is:

``primary``
  Ansible inventory name of a primary DHCP host, if you need failover to work
  on different IP, see ``primary_fo_addr`` option below.

``secondary``
  Ansible inventory name of a secondary DHCP host, if you need failover to work
  on different IP, see secondary_fo_addr option below.

Ansible inventory name is either IP or hostname specified in inventory file.

``mclt``
  Max Client Lead Time. The maximum amount of time that one server can extend
  a lease for a DHCP client beyond the time known by the partner server.

  Default value: ``3600``

Split configuration between two failover DHCP servers:

``split``
  Percentage value between ``0`` and ``255``.
  
  Specifies the split between the primary and secondary servers for the
  purposes of load balancing. Whenever a client makes a DHCP request, the DHCP
  server runs a hash on the client identification, resulting in value from 0 to
  255. This is used as an index into a 256 bit field. If the bit at that index
  is set, the primary is responsible. If the bit at that index is not set, the
  secondary is responsible. Instead of ``split``, you can use ``hba``.

``hba``
  32 character string in the regexp: ``([0-9a-f]{2}:){32}``

  Specifies the split between the primary and secondary as a bitmap rather than
  a cutoff, which theoretically allows for finer-grained control. In practice,
  there is probably no need for such fine-grained control, however.

You must use either 'split' or 'hba' statement. Split has a preference, so
if it's defined, 'hba' will be omitted by configuration template.

``max_response_delay``
  Tells the DHCP server how many seconds may pass without receiving a message
  from its failover peer before it assumes that connection has failed. This is
  mandatory according to ``dhcpd.conf`` man page.

  Default value: ``5``

``max_unacked_updates``
  Tells the remote DHCP server how many ``BNDUPD`` messages it can send before
  it receives a ``BNDACK`` from the local system. This is mandatory according
  to ``dhcpd.conf`` man page.

  Default value: ``10``

Optional fields are mostly described in ``dhcpd.conf`` man page:

``port``
  Specifies port on which primary and secondary nodes will listen for failover
  connection. Different ports for primary and secondary are currently
  unsupported.

  Default value: ``647``

``primary_fo_addr``
  IP/Hostname of a primary DHCP host. This option is used if you need the
  failover address to be different from ansible inventory IP/hostname. If
  omitted, then ``primary`` is used.

``secondary_fo_addr``
  IP/Hostname of a secondary DHCP host. This option is used if you need the
  failover address to be different from ansible inventory IP/hostname. If
  omitted, then ``secondary`` is used.

``auto_partner_down``
  Number of seconds to start serving partners IPs after the partner's failure.

Other parameters::

  load_balance_max_seconds: 5
  max_lease_misbalance: 15
  max_lease_ownership: 10
  min_balance: 60
  max_balance: 3600

Examples::

  # Full cluster configuration
  dhcpd_failovers:
  - failover: 'failover-localsubnet'
    primary: '10.0.10.1'
    primary_fo_addr: '10.5.10.1'
    secondary: '10.0.10.2'
    secondary_fo_addr: '10.5.10.2'
    port: 1337
    split: 128
    hba: aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa
    max_response_delay: 5
    max_unacked_updates: 10
    load_balance_max_seconds: 5
    auto_partner_down: 0
    max_lease_misbalance: 15
    max_lease_ownership: 10
    min_balance: 60
    max_balance: 3600
  
  # Minimal cluster configuration
  dhcpd_failovers:
  - failover: 'failover-san'
    primary: '10.0.10.1'
    secondary: '10.0.10.2'
    mclt: 3600
    split: 128
    max_response_delay: 5
    max_unacked_updates: 10

