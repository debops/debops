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

This is a list of mesh networks managed by the ``debops.tinc`` role. Each
network is described by a YAML dictionary which should have the following keys:

``name``
  Required. Name of the mesh network, used as the name of the directory in
  :file:`/etc/tinc/` as well as the ``systemd`` instance argument.

.. _tinc__ref_networks_interface:

``interface``
  Required. Name of the virtual Ethernet device which will be managed by the
  Tinc VPN. Using names like ``tunX`` or ``tapX`` will ensure that DNS
  configuration received from the nameserver will be ordered correctly by
  the ``resolvconf`` package.

``port``
  Required. TCP and UDP port used by this Tinc VPN.

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

.. _tinc__ref_networks_boot:

``boot``
  Optional, boolean. Enable or disable start of the given Tinc VPN at boot
  time. By default all mesh networks are started at boot.

.. _tinc__ref_networks_user:

``user``
  Optional. Name of the UNIX user account under which the ``tincd`` daemon will
  be running. If not specified, ``tincd`` will be run under ``root`` account.

``mlock``
  Optional, boolean. If present and ``True``, ``tincd`` will be executed with
  the ``--mlock`` option which will lock the daemon's memory in RAM, preventing
  the system from moving it to the swap space.

``chroot``
  Optional, boolean. If ``True``, the ``tincd`` daemon will be run chrooted to
  the directory with the VPN configuration files.

``state``
  Optional, string. Whether the  mesh should be ``present`` or ``absent``
  absent. Defaults to ``present``.

.. _tinc__ref_networks_tinc_exclude_addresses:

``tinc_exclude_addresses``
  Optional. List of FQDN or IP addresses which should be excluded from the public key file
  of a given host. This list excludes the IP addresses of the mesh interface as
  well as the bridge interface, so that Tinc doesn't try to connect to remote
  hosts over the VPN connection.

``tinc_options``
  Required. Dictionary variable which specifies options stored in the
  :file:`/etc/tinc/<network>/tinc.conf` configuration file. Each key of the dict is
  the option name, values can be strings or lists of strings, in which case the
  option will be repeated as many times as there are elements in the list.

  To see the list of available options, check the :manpage:`tinc.conf(5)` manual page.

``tinc_host_options``
  Optional. Dictionary variable which specifies options stored in the
  :file:`/etc/tinc/<network>/hosts/<hostname>` configuration file. Each key of the
  dict is the option name, values can be strings or lists of strings, in which
  case the option will be repeated as many times as there are elements in the
  list.

  To see the list of available options, check the :manpage:`tinc.conf(5)` manual page.

Examples
~~~~~~~~

Minimal configuration of a default Tinc ``mesh0`` VPN::

    tinc__networks: [ '{{ tinc__network_mesh0 }}' ]

    tinc__network_mesh0:
      name: 'mesh0'
      interface: 'tap0'
      port: '655'
      tinc_options:
        Mode: 'switch'
        DeviceType: 'tap'
