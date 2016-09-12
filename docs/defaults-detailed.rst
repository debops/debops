Default variable details
================================

Some of ``debops.ifupdown`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _ifupdown_interfaces:

ifupdown_interfaces
-------------------

This is a list of dicts, each dict defines a network interface. The basic
configuration is very similar to how :file:`/etc/network/interfaces` is configured,
you can read about it on the Debian Wiki `NetworkConfiguration`_ page.

.. _NetworkConfiguration: https://wiki.debian.org/NetworkConfiguration

Each interface definition requires at least the ``iface`` parameter. Other
parameters are (mostly) optional and usually change how the network interface
is configured. For example, to specify that a given interface is a bridge, you
need to select a specific type::

    - iface: 'br0'
      type: 'bridge'

List of interface parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``iface``
  Name of the interface, required. Multiple interfaces with the same names can
  be configured at the same time (IPv4 and IPv6 interface configuration is
  defined separately).

  Examples: ``eth0``, ``br0``, ``vlan1000``, ``bond0``

``type``
  Interface type, either ``interface``, ``bridge``, ``vlan``, ``bond``, or
  ``mapping``. Each interface type may have their own additional parameters,
  which might be optional or required. If type is not specified, ``interface``
  is used.

``alias``
  Alternative name of the interface type, used in the comments and filename.

``enabled``
  Boolean variable (``True``/``False``). If present, the interface configuration
  can be generated or not depending on a variable, for example::

      - iface: 'br2'
        enabled: '{{ interface_active | bool }}'

``inet`` | ``inet6``
  This parameter determines the "family" of given interface configuration,
  either IPv4 or IPv6 (in ``ifupdown`` each family on a given interface is
  configured in a separate "stanza").

  You should use only one of them for each interface definition. If none are
  used, ``inet`` (IPv4) is assumed. If both are used, ``inet6`` (IPv6) takes
  precedence.

  The value of this parameter specifies what configuration method is used to
  configure given interface. It can be ``dhcp``, ``static``, ``manual`` or
  other methods, depending on what each interface type allows. See
  :manpage:`interfaces(5)` for a list of available methods. If parameter is not
  specified, ``dhcp`` is used as default for IPv4 network.

``auto``
  Boolean variable (``True``/``False``) which determines if a given network
  interface will be brought up automatically at system start. By default all
  interfaces are configured to start automatically (``True``).

``allow``
  Name or list of names of "subsystems" which can enable the interface, for
  example ``hotplug``. By default, if nothing is specified and interface is not
  configured manually, ``allow-hotplug`` will be added automatically so that
  the ``systemd`` ``ifup@.service`` unit can work correctly.

``addresses``
  List of IPv4 or IPv6 addresses in the ``host/prefix`` format which should be
  configured on this interface. You can specify multiple IPv4 or IPv6
  addresses, they will be filtered according to the interface "family" - this
  allows you to keep all of the host IP addresses in one list.

  The IP addresses will be configured in the order they are listed. If the interface is
  configured as ``static``, the first IPv4 address will be the main one, the rest
  will be added with numbered labels. When the interface is configured to get its
  IP address via DHCP, all IPv4 addresses will be added with numbered labels.

``gateway``
  IP address of the gateway configured for this interface; only one gateway can
  be configured at the moment.

``label``
  Specify a string which will be added to the interface name as a label.
  Labeled interface configuration is stored in separate configuration files in
  :file:`/etc/network/interfaces.d/`.

``options``
  YAML text block with additional options added to the interface configuration.
  You can specify here custom commands, nameservers, search domains, etc. See
  :manpage:`interfaces(5)` for more details about what can be configured.

``port``
  Name of other network interface which this interface might depend on. Usage
  depends on the interface type.

  In ``bridge`` interfaces, you can specify the name or list of interfaces to add
  to the bridge.

  In ``vlan`` interfaces, you can define the name of the interface used as
  ``vlan_raw_device``.

  In ``6to4`` interface, you can specify the name of the interface which will be
  checked for IPv4 address to use to configure the IPv6 6to4 tunnel.

``ports`` | ``bridge_ports``
  Alternative names for list of ports to add to a given bridge.

``device`` | ``vlan_device`` | ``vlan_raw_device``
  Alternative names for the name of the interface to use as VLAN raw device.

``port_present``
  If you specify a name of an interface with this parameter,
  ``debops.ifupdown`` will check if that interface exists (usually these are
  physical interfaces like ``eth0``). If the interface exists, the role will
  generate the configuration of an interface with this parameter. If it does
  not, the configuration won't be generated.

``port_active``
  Boolean variable (``True``/``False``) which specifies the state of
  the ``item.port_present`` interface that you want, either active (``True``, port
  has a connection) or inactive (``False``, port does not have connection). If
  the port is not in a given state, then the configuration won't be generated.

``weight``
  Numerical value added at the beginning of the interface configuration file.
  If not specified, a value will be set from ``ifupdown_interface_weight_map``
  variable depending on the type of the interface.

``filename``
  Name of the configuration file to generate. If not specified, an unique
  configuration file name will created, based on the interface type, interface
  name, label and interface family.

``delete``
  If specified and ``True``, the configuration file for a given interface will
  be deleted from :file:`/etc/network/interfaces.d/` and won't be generated again.

``force``
  If specified and ``True`` force the role to generate a specified interface,
  even if various conditions say otherwise.

``auto_ifup``
  By default when the interface configuration changes, the ``debops.ifupdown`` role
  will automatically stop that interface and start it again. If this parameter
  is present and ``True``, the role will stop the interface and generate a script
  in :file:`/tmp` directory which can be used to start it again from another
  Ansible role or manually.

Example interface configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configuration examples can be found in the :file:`var/` directory of the
``debops.ifupdown`` role, or `on GitHub`_. If you want to use them as a base
for your own configuration, add them to the ``ifupdown_interfaces`` list in Ansible’s
inventory, so they can override the defaults.

.. _on GitHub: https://github.com/debops/ansible-ifupdown/tree/master/vars

