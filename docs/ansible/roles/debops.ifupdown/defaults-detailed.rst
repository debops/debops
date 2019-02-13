Default variable details
========================

Some of ``debops.ifupdown`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _ifupdown__ref_interfaces:

ifupdown__interfaces
--------------------

The ``ifupdown__*_interfaces`` variables are YAML dictionaries which define
what network interfaces are configured on a host. All dictionaries are
recursively combined together in the order they appear in the
:file:`defaults/main.yml` file.

Each entry in the ``ifupdown__*_interfaces`` dictionaries is a YAML dictionary.
The key of a given entry is either a network interface name (for example
``eth0``, ``br0``, etc.) or a "label" that holds the preferences for a network
interface denoted by the ``iface`` parameter. Configuration parameters in
labeled sections will be merged with the real network interface preferences.

You can also use YAML lists of dictionaries, however you cannot combine both
dictionaries and lists in the same ``ifupdown__*_interfaces`` variable. YAML
dictionaries specified in a list need to have the ``iface`` parameter that
specifies the interface name, otherwise they will be skipped.

Each network interface will have its configuration in a separate file in
:file:`/etc/network/interfaces.d/` directory on the managed hosts (both IPv4
and IPv6 configuration is in the same file).

.. _ifupdown__ref_network_interface_types:

Network interface types
~~~~~~~~~~~~~~~~~~~~~~~

Each network interface has a particular type (ethernet, bridge, VLAN, etc.).
The type can be specified by the ``type`` parameter. If this parameter is not
defined, the role will try to select the correct type based on the interface
name prefix:

``en*`` or ``eth*``
  The Ethernet network interfaces, marked as the ``ether`` type. If not
  configured specifically, this interface type will automatically enable an
  IPv4 DHCP configuration and IPv6 SLAAC configuration. The network interface
  will be configured to be brought up by the hotplug subsystem.

``br*``
  The network bridge interface, marked as the ``bridge`` type. If not
  configured specifically, the role will configure an anonymous bridge without
  any network interfaces connected, which will be started automatically at
  boot. The firewall will be configured to allow network traffic through the
  bridge, without IPv4 NAT.

``vlan*`` or name with a dot (``.``)
  The VLAN interface, marked as the ``vlan`` type.

``bond*``
  The bonding interface, marked as the ``bonding`` type.

``sl*``
  The `Serial Line Internet Protocol <https://en.wikipedia.org/wiki/Serial_Line_Internet_Protocol>`_
  interface, marked as the ``slip`` type.

``wl*``
  The Wireless LAN interface, marked as the ``wlan`` type.

``ww*``
  The `Wireless WAN <https://en.wikipedia.org/wiki/Wireless_WAN>`_ interface,
  marked as the ``wwan`` type.

``tap*``, ``tun*``, ``mesh*``, ``sit*``
  The network tunnel interface, marked as the ``tunnel`` type.

``6to4``
  The `IPv6 to IPv4 transition mechanism <https://en.wikipedia.org/wiki/6to4>`_
  interface, marked as the ``6to4`` type. If not configured specifically, this
  interface will be configured as ``6to4`` tunnel with local IPv6 address based
  on the default network interface IPv4 address.

``mapping``
  The interface configuration is selected dynamically by a specified script.
  See :man:`interfaces(5)` for more details.

Each network interface can have multiple parameters. Some parameters are
specific to a particular interface type.

General interface parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``iface``
  Name of the network interface to configure. If not specified, the network
  interface will be taken from the YAML dictionary key which holds the
  parameters.

  Example Ethernet interface configuration without and with ``iface``
  parameter, and a version specified as a list:

  .. code-block:: yaml

     ifupdown__interfaces:
       'eth0':
         type: 'ether'

     ifupdown__group_interfaces:
       'external':
         iface: 'eth0'
         type: 'ether'

     ifupdown__host_interfaces:
       - iface: 'eth0'
         type: 'ether'

  The ``iface`` parameter can be templated by Jinja, unlike the dictionary key.

``type``
  Optional. Specify the interface type. If this parameter is not defined, role
  will try and guess the type based on the interface name (see
  :ref:`ifupdown__ref_network_interface_types`). The interface type affects the
  order in which interfaces are brought up/down and use/requirement of special
  parameters for certain types.

  +-------------+--------+--------------------------------------------------------------+
  |    Type     | Weight | Notes                                                        |
  +=============+========+==============================================================+
  | ``mapping`` | 00     | interface configured dynamically via scripts                 |
  +-------------+--------+--------------------------------------------------------------+
  | ``bonding`` | 10     | virtual bonded interface                                     |
  +-------------+--------+--------------------------------------------------------------+
  | ``ether``   | 20     | Ethernet (physical or virtual) interface                     |
  +-------------+--------+--------------------------------------------------------------+
  | ``slip``    | 30     | Serial Line Internet Protocol interface                      |
  +-------------+--------+--------------------------------------------------------------+
  | ``wlan``    | 30     | Wireless Local Area Network interface (WiFi)                 |
  +-------------+--------+--------------------------------------------------------------+
  | ``wwan``    | 30     | Wireless Wide Area Network interface (mobile networks, GSM)  |
  +-------------+--------+--------------------------------------------------------------+
  | ``vlan``    | 40     | VLAN interface, requires another interface to be attached to |
  +-------------+--------+--------------------------------------------------------------+
  | ``bridge``  | 60     | network bridge                                               |
  +-------------+--------+--------------------------------------------------------------+
  | ``6to4``    | 80     | IPv6 in IPv4 tunnel                                          |
  +-------------+--------+--------------------------------------------------------------+
  | ``tunnel``  | 80     | virtual network tunnel                                       |
  +-------------+--------+--------------------------------------------------------------+

  If the detected interface type is ``vlan``, the role will check what parent
  interface is a given VLAN attached to and change the configuration to reorder
  the ``vlan`` interface after all of the parent interfaces, so that network
  interfaces are processed in the working order. This will only happen if
  ``weight_class`` parameter is not specified. If the interface is overridden,
  the ``weight`` parameter will be set to ``5`` to ensure proper interface
  order.

``weight_class``
  Optional. Override the specified ``type`` for a given interface so that the
  weight of another type will be used instead.

``weight``
  Optional. Positive or negative number (for example ``2`` or ``-2``) which
  will be added to the base weight defined by the interface type. This can be
  used to affect the network interface order.

``state``
  Optional. If not specified or ``present``, the given interface configuration
  file will be created. If ``absent``, the interface configuration will be
  removed. If ``ignore``, the interface configuration won't be modified in any
  way – this is useful if you want to make sure that some network interfaces
  are ignored by the role.

  If you use the ``dynamic`` interface layout, you might need to explicitly set
  the ``br0`` and ``br1`` bridge state to ``present`` because this interface
  layout will try to remove them by default.

``auto``
  Optional, boolean. If ``True``, the network interface will be brought up by
  the ``networking`` service at boot time, which might be not what you actually
  want in the newer, :command:`systemd`-based hosts. By default it will be set
  to ``False``. See also ``allow`` parameter.

``allow``
  Optional, boolean, string or YAML list. If set to ``False``, this option is
  disabled. If ``True``, the hotplug subsystem can bring this interface up or
  down when the hotplug event is detected. You can also specify a list of
  specific conditions at which the interface is brought up, currently
  recognized conditions are:

  - ``auto``: bring the interface up at boot time by the ``networking``
    service. This might not be what you want on newer systems.

  - ``boot``: bring the interface up at boot time by ``iface@.service``
    :command:`systemd` unit. This will put any processes related to a given
    interface in their separate cgroup, which allows for better control over
    the network interface. This is a custom implementation of the ``auto``
    mechanism managed by this Ansible role.

  - ``hotplug``: bring the interface up/down at hotplug events. This condition
    is required to be present for the ``ifup@.service`` :command:`systemd` unit
    to work properly.

  If this parameter is not specified, the role will use the ``boot`` value for
  network interfaces other than physical Ethernet interfaces, which will use
  the ``hotplug`` value by default.

IPv4 and IPv6 configuration parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``inet``
  Optional. IPv4 configuration method used by a given interface. There are many
  configuration methods described in the :man:`interfaces(5)` manual page, most
  commonly used are: ``manual``, ``dhcp``, ``static``. If you set this
  parameter to ``False``, the IPv4 configuration will be disabled.

``inet6``
  Optional. IPv6 configuration method used by a given interface. There are many
  configuration methods described in the :man:`interfaces(5)` manual page, most
  commonly used are: ``auto``, ``manual``, ``dhcp``, ``static``, ``v4tunnel``,
  ``6to4``. If you set this parameter to ``False``, the IPv6 configuration will
  be disabled.

``address`` or ``addresses``
  Optional. A string or an YAML list of IPv4 and/or IPv6 addresses to set on
  a given network interface, in the form of ``ipaddress/prefix`` or CIDR.
  Remember that you need to specify the host IP address and not the network;
  the ``192.0.2.1/24`` is the correct notation, and ``192.0.2.0/24`` is
  incorrect.

``gateway`` or ``gateways``
  Optional. Specify the IPv4 or IPv6 address of the network gateway to which outgoing
  packets will be directed. If it's a list of addresses, first valid address
  for a network type will be used as the gateway.

DNS nameserver and search parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``dns_nameservers``
  Optional. String or list of IP addresses of the nameservers to configure in
  :file:`/etc/resolv.conf`. Remember that only 3 nameservers are allowed at any
  time. They will be added to the IPv4 section of the network interface
  configuration unless IPv4 is disabled, in which case they will be configured
  in IPv6 section.

``dns_search``
  Optional. String or list of domains which should be searched in the DNS if
  a hostname without a domain is specified. They will be added to the
  :file:`/etc/resolv.conf`. This list will be added to the IPv4 section of the
  network interface configuration unless IPv4 is disabled, in which case they
  will be configured in IPv6 section.

Bonding parameters
~~~~~~~~~~~~~~~~~~

``slaves``
  Optional. String or YAML list of network interfaces to bond together.

``bond_*``
  Optional. If an interface is a bonding, any parameters that have ``bond_``
  prefix will be added to that interface configuration. See the documentation
  included in the ``ifenslave`` package for possible configuration options.

Bridge parameters
~~~~~~~~~~~~~~~~~

``bridge_*``
  Optional. If an interface is a bridge, any parameters that have ``bridge_``
  prefix will be added to that interface configuration. See the
  :man:`bridge-utils-interfaces(5)` manual for more details about possible bridge
  configuration options.

VLAN parameters
~~~~~~~~~~~~~~~

``vlan_device`` or ``vlan_raw_device``
  Name of the network interface on which a VLAN will be configured.  If the
  interface name contains a dot (for example ``eth0.10``), the role will try to
  detect the network interface automatically.

6to4 tunnel parameters
~~~~~~~~~~~~~~~~~~~~~~

``local``
  Optional. Specify the public IPv4 address which will be used to create the
  IPv6 6to4 tunnel.

Mapping parameters
~~~~~~~~~~~~~~~~~~

``script``
  Absolute path to a script which will be used to select a specific interface
  configuration for a mapping dynamically. See :man:`interfaces(5)` manual for
  more details.

DHCP parameters
~~~~~~~~~~~~~~~

``dhcp_ignore``
  Optional. String or list of variable names used by the
  :man:`dhclient-script(8)` script to configure the interface. The specified
  variables representing DHCP options will be unset by the configuration
  script; this can be used to selectively ignore DHCP options on a given
  network interface.

  See :ref:`ifupdown__ref_custom_hooks_filter_dhcp_options` documentation for
  more details.

Custom interface options
~~~~~~~~~~~~~~~~~~~~~~~~

``comment``
  Optional. String or a YAML text block with a comment that will be added to
  a given interface configuration file.

``comment4``
  Optional. String or a YAML text block with a comment that will be added to
  a given interface configuration file near the IPv4 section.

``comment6``
  Optional. String or a YAML text block with a comment that will be added to
  a given interface configuration file near the IPv6 section.

``options``
  Optional. String or a YAML text block with custom options for the network
  interface. It will be added after the IPv4 section, unless IPv4 support is
  disabled in which case it will be added after IPv6 section. If this parameter
  is specified, autogenerated configuration for specific interface types will
  be disabled.

``options4``
  Optional. String or a YAML text block with custom options added to the IPv4
  section of the network interface configuration. If this parameter is present,
  autogenerated configuration for specific interface types will be disabled.

``options6``
  Optional. String or a YAML text block with custom options added to the IPv6
  section of the network interface configuration. If this parameter is present,
  autogenerated configuration for specific interface types will be disabled.

``add_options``
  Optional. String or a YAML text block with custom options for the network
  interface. It will be added after the IPv4 section, unless IPv4 support is
  disabled in which case it will be added after IPv6 section. You can use this
  parameter to add options to the autogenerated configuration, which will be
  still included.

``add_options4``
  Optional. String or a YAML text block with custom options added to the IPv4
  section of the network interface configuration. You can use this parameter to
  add options to the autogenerated configuration, which will be still included.

``add_options6``
  Optional. String or a YAML text block with custom options added to the IPv6
  section of the network interface configuration. You can use this parameter to
  add options to the autogenerated configuration, which will be still included.

``debug``
  Optional, boolean. If ``True``, the role will add commented out debug
  information to the generated interface configuration file. It can be used to
  check what the role thinks the interface configuration should be like.

Firewall parameters
~~~~~~~~~~~~~~~~~~~

``forward``
  Optional, boolean. If absent and an interface is a bridge, or present and
  ``True``, the role will generate configuration for the :ref:`debops.ferm` and
  the :ref:`debops.sysctl` roles to enable packet forwarding for a given
  interface.

``forward_ipv6``
  Optional, boolean. Only makes sense with the ``forward`` parameter present.
  By default the role will enable forwarding on IPv6 networks, you can use this
  parameter to disable it by setting it to ``False``.

``forward_ipv4``
  Optional, boolean. Only makes sense with the ``forward`` parameter present.
  By default the role will enable forwarding on IPv4 networks, you can use this
  parameter to disable it by setting it to ``False``.

``accept_ra``
  Optional, by default not defined. If ``0``, the SLAAC Router Advertisements
  on IPv6 networks will be ignored by this interface. If ``1``, this interface
  will accept the SLAAC Router Advertisements when forwarding is disabled,
  ignore when forwarding is enabled. If ``2``, SLAAC Router Advertisements
  received on this interface will be accepted even when forwarding is enabled.

``forward_interface_ferm_rule_enabled``
  Optional, boolean. Should a Firewall rule be configured which matches new
  connection attempts entering the interface?
  If disabled using ``False``, the default Firewall policy will apply.
  Defaults to ``True``.

``forward_interface_ferm_rule``
  Optional, string. Default action or any custom ferm configuration.
  Defaults to ``ACCEPT``.

``forward_outerface_ferm_rule_enabled``
  Optional, boolean. Should a Firewall rule be configured which matches new
  connection attempts exiting the interface?
  If disabled using ``False``, the default Firewall policy will apply.
  Defaults to ``True``.

``forward_outerface_ferm_rule``
  Optional, string. Default action or any custom ferm configuration.
  Defaults to ``ACCEPT``.

``nat``
  Optional, boolean. If present and ``True``, the firewall configuration for
  a given interface (usually a bridge) will include the IPv4 NAT rules. The
  default gateway IPv4 address will be used in the Source NAT configuration.

``nat_masquerade``
  Optional, boolean. If present and ``True``, the role will use the
  ``MASQUERADE`` rule in the firewall configuration instead of the ``SNAT``
  rule. This is useful when the host has no fixed default IP address, for
  example on a laptop.
  Defaults to :envvar:`ifupdown__default_nat_masquerade`.

``nat_snat_address``
  Optional. Specify the ``SNAT`` IPv4 address to use for the NAT on a given
  bridge. If not specified, the role will use the host's default IPv4 address
  as the ``SNAT`` IP address.

``nat_snat_interface``
  Optional. If specified, the IPv4 address on a given network interface will be
  used to generate the ``SNAT`` firewall rules.

Configuration examples
~~~~~~~~~~~~~~~~~~~~~~

The examples below are based on the `Debian Network Configuration <https://wiki.debian.org/NetworkConfiguration>`_
and `Debian IPv6 configuration <https://wiki.debian.org/DebianIPv6>`_
pages to make comparison between :file:`/etc/network/interfaces` configuration
and ``debops.ifupdown`` configuration easier. Examples are verbose to reflect
the examples from the wiki page, but some of the parameters can be omitted to
let the role autogenerate them.

Keep in mind that the ``auto`` parameter, included in the examples for
completeness, usually should be avoided in the newer OS releases (Jessie+,
Trusty+) on ``systemd``-based hosts. This is done so that the additional
processes related to a given network interfaces are put in their own
``ifup@.service`` cgroup instead of being grouped together under
the ``networking.service`` cgroup.

Use DHCP and SLAAC to `automatically configure the network interface <https://wiki.debian.org/NetworkConfiguration#Using_DHCP_to_automatically_configure_the_interface>`_:

.. code-block:: yaml

   ifupdown__interfaces:
     'eth0':
       auto: True
       allow: 'hotplug'
       inet: 'dhcp'
       inet6: 'auto'

`Configure the network interface manually <https://wiki.debian.org/NetworkConfiguration#Configuring_the_interface_manually>`_
using static IPv4 and IPv6 configuration:

.. code-block:: yaml

   ifupdown__interfaces:
     'static-eth0':
       iface: 'eth0'
       auto: True
       inet: 'static'
       inet6: 'static'
       addresses: [ '192.0.2.7/24', '2001:db8::c0ca:1eaf/64' ]
       gateways:  [ '192.0.2.254', '2001:db8::1ead:ed:beef' ]

Configure an interface `without an IP address <https://wiki.debian.org/NetworkConfiguration#Bringing_up_an_interface_without_an_IP_address>`_:

.. code-block:: yaml

   ifupdown__interfaces:

     'eth0':
       inet: 'manual'
       options: |
         pre-up ifconfig $IFACE up
         post-down ifconfig $IFACE down

    'eth0.99':
      inet: 'manual'
      options: |
        post-up ifconfig $IFACE up
        pre-down ifconfig $IFACE down

Configure `DNS nameservers and search domains <https://wiki.debian.org/NetworkConfiguration#The_resolvconf_program>`_
with an autogenerated default interface:

.. code-block:: yaml

   ifupdown__interfaces:
     'external':
       iface: '{{ ifupdown__external_interface }}'
       inet: 'dhcp'
       dns_nameservers: [ '12.34.56.78', '12.34.56.79' ]
       dns_search: 'example.com'

Configure `static bridge <https://wiki.debian.org/NetworkConfiguration#Bridging>`_
between two Ethernet interfaces:

.. code-block:: yaml

   ifupdown__interfaces:

     'eth0':
       inet: 'manual'
       inet6: False

     'eth1':
       inet: 'manual'
       inet6: False

     'br0':
       inet: 'static'
       address: '10.10.0.15/24'
       gateway: '10.10.0.1'
       bridge_ports: [ 'eth0', 'eth1' ]
       bridge_stp: 'on'

Create a `static VLAN interface on an Ethernet interface <https://wiki.debian.org/NetworkConfiguration#Network_init_script_config>`_:

.. code-block:: yaml

   ifupdown__interfaces:
     'eth0.222':
       auto: True
       inet: 'static'
       address: '10.10.10.1/24'
       vlan_raw_device: 'eth0'

Connect `a bridge to a VLAN on an Ethernet interface <https://wiki.debian.org/NetworkConfiguration#Caveats_when_using_bridging_and_vlan>`_:

.. code-block:: yaml

   ifupdown__interfaces:

     'eth0':
       auto: True
       inet: 'static'
       inet6: False
       address: '192.168.1.1/24'

     'eth0.110':
       inet: 'manual'
       vlan_device: 'eth0'

     'br0':
       auto: True
       inet: 'static'
       address: '192.168.110.1/24'
       bridge_ports: 'eth0.110'
       bridge_stp: 'on'
       bridge_maxwait: '10'

Create `a bonded interface <https://wiki.debian.org/NetworkConfiguration#A.2Fetc.2Fnetwork.2Finterfaces>`_
using two Ethernet interfaces and attached VLANs:

.. code-block:: yaml

   ifupdown__interfaces:

     'bond0':
       auto: True
       inet: 'manual'
       slaves: [ 'eth1', 'eth0' ]
       options: |
         up ifconfig bond0 0.0.0.0 up

     'vlan10':
       auto: True
       inet: 'static'
       address: '10.10.10.12/16'
       gateway: '10.10.0.1'
       vlan_raw_device: 'bond0'
       dns_nameservers: '10.10.0.2'
       dns_search: 'hup.hu'

     'vlan20':
       auto: True
       inet: 'static'
       address: '10.20.10.12/16'
       vlan_raw_device: 'bond0'

     'vlan30':
       auto: True
       inet: 'static'
       address: '10.30.10.12/16'
       vlan_raw_device: 'bond0'

Create `advanced bonding configuration <https://wiki.debian.org/NetworkConfiguration#How_to_set_the_MTU_.28Max_transfer_unit_.2F_packet_size.29_with_VLANS_over_a_bonded__interface>`_
with MTU and other parameters:

.. code-block:: yaml

   ifupdown__interfaces:

     'bond0':
       auto: True
       inet: 'manual'
       bond_slaves: [ 'eth0', 'eth1' ]
       bond_mode: '4'
       bond_miimon: '100'
       bond_downdelay: '200'
       bond_updelay: '200'
       bond_lacp_rate: '1'
       bond_xmit_hash_policy: 'layer2+3'
       options: |
         up ifconfig lacptrunk0 0.0.0.0 up
         post-up ifconfig eth0 mtu 9000 && ifconfig eth1 mtu 9000 && ifconfig bond0 mtu 9000

     'vlan101':
       auto: True
       inet: 'static'
       address: '10.101.60.123/24'
       gateway: '10.155.60.1'
       vlan_device: 'bond0'

     'vlan151':
       auto: True
       inet: 'static'
       address: '192.168.1.1/24'
       vlan_device: 'bond0'

Configure `multiple IP addresses on an interface <https://wiki.debian.org/NetworkConfiguration#iproute2_method>`_
using the "manual approach" method:

.. code-block:: yaml

   ifupdown__interfaces:
     'eth0':
       allow: [ 'auto', 'hotplug' ]
       addresses:
         - '192.168.1.42/24'
         - '192.168.1.43/24'
         - '192.168.1.44/24'
         - '10.10.10.14/24'
       gateway: '192.168.1.1'

Configure `a 6to4 tunnel <https://wiki.debian.org/DebianIPv6#IPv6_6to4_Configuration>`_
using your public, default IPv4 address (role will autogenerate most of the
required configuration):

.. code-block:: yaml

   ifupdown__interfaces:
     '6to4': {}

Configure a restricted bridge network:

.. code-block:: yaml

   ifupdown__interfaces:
     'br2':
       type: 'bridge'
       inet6: 'static'
       inet: 'static'
       nat: True
       forward_interface_ferm_rule: 'outerface (br0 br2) ACCEPT'
       forward_outerface_ferm_rule_enabled: False
       addresses:
         - '2001:db8::23/64'
         - '192.0.2.23/24'

Hosts attached to the ``br2`` bridge are allowed to talk to each other.
Additionally, the hosts can initiate connections to the outside world thought
``br0``. No connections can be initiated from the outside world to the hosts
behind ``br2``. SNAT is used for IPv4. For IPv6 it is expected that the prefix
is routed to the host so that the host can forward packets to ``br2``.

.. _ifupdown__ref_custom_files:

ifupdown__custom_files
----------------------

The ``ifupdown__*_custom_files`` list variables can be used to place custom
scripts or other configuration files on the remote hosts needed for network
configuration (for example mapping scripts). Each list element is a YAML
dictionary with specific parameters:

``dest`` or ``path``
  Required. Absolute path to the destination file on remote host.

``src``
  Optional. Path to the source file on the Ansible Controller which will be
  copied to the remote host. Shouldn't be used with the ``content`` parameter.

``content``
  Optional. An YAML text block with the file contents which should be put in
  the specified destination file on the remote host. Shouldn't be used with the
  ``src`` parameter.

``owner``
  Optional. Specify the UNIX user account which will be an owner of the file.
  If not specified, ``root`` will be the owner.

``group``
  Optional. Specify the UNIX group which will be the primary group of the file.
  If not specified, ``root`` will be the primary group.

``mode``
  Optional. Specify the file mode which should be set for a given file. If not
  specified, ``0644`` mode will be set.

``force``
  Optional, boolean. If not specified or ``True``, the role will ensure that
  the file contents are up to date on each run. If ``False``, existing files
  won't be changed if they are different.

Examples
~~~~~~~~

Create an interface mapping script:

.. code-block:: yaml

   ifupdown__custom_files:
     - dest: '/usr/local/lib/ifupdown-map-wlan.sh'
       owner: 'root'
       group: 'root'
       mode: '0755'
       content: |
         #!/bin/sh
         # Script contents ...
         exit 0
