Default variable details
========================

Some of ``debops.tinc`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _tinc__ref_networks:

tinc__networks
--------------

The ``tinc__*_networks`` variables is a collection of YAML dictionaries that
define Tinc networks. All dictionaries are recursively combined together in the
order they appear in the :file:`defaults/main.yml` file.

Each entry in the ``tinc__*_networks`` dictionaries is a YAML dictionary. The
key of a given entry is either a network interface name (for example ``mesh0``
or ``tap0``) or a "label" that holds the preferences for a network denoted by
the ``name`` parameter. Configuration parameters in labeled sections will be
merged with the real network preferences.

You can also use YAML lists of dictionaries, however you cannot combine both
dictionaries and lists in the same ``tinc__*_networks`` variable. YAML
dictionaries specified in a list need to have the ``name`` parameter that
specifies the interface name, otherwise they will be skipped.

Each Tinc network is described by specific parameters:

``port``
  Required. TCP and UDP port used by this Tinc VPN.

``name``
  Optional. Name of the mesh network, used as the name of the directory in
  :file:`/etc/tinc/` as well as the ``systemd`` instance argument. If not
  specified, the YAML dictionary key will be used as the network name.

.. _tinc__ref_networks_interface:

``interface``
  Optional. Name of the virtual Ethernet device which will be managed by the
  Tinc VPN.

  If not specified, the role will generate an interface name from the network
  name and device type (``tun`` or ``tap``). If the interface name does not
  start with ``tun`` or ``tap``, the device type will be added as a prefix to
  the generated interface name.

  Using names like ``tunX`` or ``tapX`` will ensure that DNS configuration
  received from the nameserver will be ordered correctly by the ``resolvconf``
  package.

``node_reachable``
  Optional, boolean. Defaults to ``True``. Whether a node should be reachable
  for other nodes or if the node should act in "client mode".
  If the node is in "client mode", the Firewall will not allow other nodes to
  initiate a connection to the Tinc daemon. Furthermore, the Tinc daemon is
  configured to only listen on the loopback interface.

.. _tinc__ref_networks_allow:

``allow``
  Optional. List of IP addresses or CIDR subnets which will be allowed to
  connect to the Tinc VPN port through the firewall. If this list is empty, any
  IP address can connect.

.. _tinc__ref_networks_bridge:

``bridge``
  Optional. Name of the network bridge to which the virtual Ethernet device
  will be connected, if the interface is configured in the "static" mode.
  This should be set on a host that provides the DHCP and DNS services for the
  mesh.

  If the ``bridge`` parameter is specified, and the ``link_type`` parameter is
  not specified, role will automatically enable the ``static`` link type.

.. _tinc__ref_networks_link_type:

``link_type``
  Optional. If empty, ``debops.tinc`` defaults to a standalone network
  interface with :program:`dhclient` requesting network configuration using
  DHCP. Possible values are:

  ``static``
    Set the Tinc interface in a "static" mode with an IP address, optionally
    attached to a network bridge. This should usually be done just on one host
    in the mesh to provide DHCP/DNS services.

.. _tinc__ref_networks_hwaddr:

``hwaddr``
  Optional. By default the ``tinc-up`` script will create the virtual Ethernet
  device with a random, but predictable and not changing MAC address. Using
  ``item.hwaddr`` you can specify your own MAC address (in the format accepted
  by ``ip link`` command).
  Set the MAC address value to ``'*'`` to let the system
  generate a random hardware address.

``metric``
  Optional. Specify the network metric which will affect the Linux routing
  table. If not specified, by default the role will tell :command:`dhclient` to
  set the ``100`` metric which should prevent issues with misconfigured default
  route.

.. _tinc__ref_networks_boot:

``boot``
  Optional, boolean. Enable or disable start of the given Tinc VPN at boot
  time. By default all mesh networks are started at boot.

.. _tinc__ref_networks_user:

``user``
  Optional. Name of the UNIX user account under which the ``tincd`` daemon will
  be running. If not specified, ``tincd`` will be run under ``tinc-vpn``
  account.

.. _tinc__ref_networks_mlock:

``mlock``
  Optional, boolean. If present and ``True``, ``tincd`` will be executed with
  the ``--mlock`` option which will lock the daemon's memory in RAM, preventing
  the system from moving it to the swap space.
  When no connection can be established, it can be tried to set this to ``False``.
  Apparently the "Error while processing METAKEY from" might not be fully
  resolved in Debian Jessie (problem also occurred with 1.0.28 from
  jessie-backports). This usually happens when the amount of RAM reserved for
  locked process memory is too low. See the :envvar:`tinc__ulimit_memlock`
  variable for more details.

``chroot``
  Optional, boolean. If ``True``, the ``tincd`` daemon will be run chrooted to
  the directory with the VPN configuration files.

``state``
  Optional, string. Whether the  mesh should be ``present`` or ``absent``.
  Defaults to ``present``.

``address`` or ``addresses``
  Optional. List of IP addresses in the ``host/prefix`` form which should be
  configured on the Tinc network interface if it's configured statically.

``host_address`` or ``host_addresses``
  Optional. List of FQDN or IP addresses which should be included in the host
  configuration. These addresses will tell other Tinc nodes how to connect to
  a specific host.

  If not specified, the role will use the filtered list of the host's FQDN (if
  the public IP addresses are available) and public IPv4/IPv6 addresses.

.. _tinc__ref_networks_tinc_exclude_addresses:

``exclude_address`` or ``exclude_addresses``
  Optional. List of FQDN or IP addresses which should be excluded from the host
  configuration. This list excludes the IP addresses of the mesh interface as
  well as the bridge interface, so that Tinc doesn't try to connect to remote
  hosts over the VPN connection.

``mode``
  Optional. Specify the Tinc routing mode to use for this network connection
  (``router``, ``switch``, ``hub``). If not specified, the ``switch`` mode is
  used by default. See the :man:`tinc.conf(5)` for more details.

``device_type``
  Optional. Specify the network device type used by Tinc. If not specified,
  ``tap`` is used by default. See the :man:`tinc.conf(5)` for more details.

``cipher``
  Optional. The cipher used to encrypt the connections. If not specified, the
  role will use the AES-256-CBC algorithm.

``digest``
  Optional. The digest algorithm used to authenticate the connections. If not
  specified, the role will use the SHA512 algorithm.

``compression``
  Optional. A level of compression used by Tinc (0-11). By default the
  compression is disabled (0).

``address_family``
  Optional. Specify the address family to use for network connections
  (``ipv4``, ``ipv6``, ``any``). If not specified, ``any`` is used by default.

``hostname``
  Optional. Set the hostname used by this host. If not specified, the value of
  :envvar:`tinc__hostname` will be used automatically.

``inventory_self``
  Optional. List of inventory names that the host is known as. This is used to
  filter out the current host from the list of hosts to connect to. If not
  specified, th :envvar:`tinc__inventory_self` value is used instead.

``inventory_groups``
  Optional. List of names of the Ansible inventory groups that are used to
  manage Tinc networks. This list will be used to create directories required
  by the role in the :file:`secret/` directory on Ansible Controller.

``connect_to``
  Optional. List of hosts which a given Tinc node should connect to, the host
  names are the names of the files in the :file`hosts/` Tinc directory. If not
  specified, and the host is not configured as "static", the global
  :envvar:`tinc__inventory_hosts` list is used to select which hosts to connect
  to.

``add_connect_to``
  Optional. Additional list of hosts to connect to. This can be used to add
  additional connections to the mesh network, for example to external hosts.
  This list will be added to the existing autogenerated list of hosts to
  connect to.

``tinc_options``
  Optional. Dictionary variable which specifies options stored in the
  :file:`/etc/tinc/<network>/tinc.conf` configuration file. Each key of the dict is
  the option name, values can be strings or lists of strings, in which case the
  option will be repeated as many times as there are elements in the list.

  If not specified, Tinc configuration will be autogenerated by the role with
  sensible defaults. If specified, role will use the autogenerated values,
  therefore you need to specify all required Tinc configuration.

  To see the list of available options, check the :man:`tinc.conf(5)` manual page.

``add_tinc_options``
  Optional. Dictionary variable which specifies additional options stored in
  the :file:`/etc/tinc/<network>/tinc.conf` configuration file. Unlike
  ``tinc_options``, this parameter will not "mask" the autogenerated values but
  will add the specified options to the autogenerated ones.

``tinc_host_options``
  Optional. Dictionary variable which specifies options stored in the
  :file:`/etc/tinc/<network>/hosts/<hostname>` configuration file. Each key of the
  dict is the option name, values can be strings or lists of strings, in which
  case the option will be repeated as many times as there are elements in the
  list.

  To see the list of available options, check the :man:`tinc.conf(5)` manual page.

``dns_nameservers``
  Optional. Specify list of DNS nameservers to configure in
  :file:`/etc/resolv.conf`. The configuration will be performed by the
  :command:`resolvconf` command. This option is used only in the "static"
  network interface configuration.

``dns_search``
  Optional. Specify list of DNS search domains to configure in
  :file:`/etc/resolv.conf`. The configuration will be performed by the
  :command:`resolvconf` command. This option is used only in the "static"
  network interface configuration.

``accept_ra``
  Optional. Specify the `accept_ra` value for the configured tinc interface.
  If missing or `True`, defaults to `'1'`. If set to anything else than
  `'0'`, `'1'`, `'2'` or `True`, the value will not be set and behaviour
  will depend on the OS settings.
  See: `ip-sysctl.txt` in the Linux Kernel Documentation.

``post_up``
  Optional. If defined, `debops.tinc` will call this code after setting up
  the interface when it is going up.

``pre_down``
  Optional. If defined, `debops.tinc` will call this code before cleaning up
  the interface when it is going down.

``tinc_up``
  Optional. If defined, `debops.tinc` will not attempt to help you configure
  the interface when it is going up but will try run this instead.
  You will have the same variables available.
  If you use this, make sure you review and understand
  `debops.tinc/templates/etc/tinc/networks/tinc-up.j2`.

``tinc_down``
  Optional. If defined, `debops.tinc` will not attempt to help you configure
  the interface when it is going down but will try to run this instead.
  You will have the same variables available.
  If you use this, make sure you review and understand
  `debops.tinc/templates/etc/tinc/networks/tinc-down.j2`.
