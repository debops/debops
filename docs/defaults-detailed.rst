Default variables: configuration
================================

Some of ``debops.tinc`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _tinc__networks:

tinc__networks
--------------

This is a list of mesh networks managed by ``debops.tinc`` role. Each network
is described by a YAML dictionary which should have the following keys:

``name``
  Required. Name of the mesh network, used as the name of the directory in
  ``/etc/tinc/`` as well as the ``systemd`` instance argument.

``interface``
  Required. Name of the virtual Ethernet device which will be managed by the
  Tinc VPN. Using names like ``tunX`` or ``tapX`` will ensure that DNS
  configuration received from the nameserver will be ordered correctly by
  ``resolvconf`` package.

``port``
  Required. TCP and UDP port used by this Tinc VPN.

``allow``
  Optional. List of IP addresses or CIDR subnets whould be allowed to connect
  to this VPN port through the firewall. If the list is not specified or empty,
  any host or network can connect.

``bridge``
  Optional. Name of the network bridge to which the virtual Ethernet device
  will be connected, if the interface is configured in the "static" mode.

``link_type``
  Optional. Specify a special interface mode which should be used on a given
  mesh host. By default, if this argument is not specified, node will ask the
  mesh for the network configuration via DHCP. If you set it to ``static``,
  a static IP address will be configured on the interface.

``hwaddr``
  Optional. By default the ``tinc-up`` script will create the virtual Ethernet
  device with a random, but predictable and not changing MAC address. Using
  ``item.hwaddr`` you can specify your own MAC address (in the format accepted
  by ``ip link`` command). If you specify the MAC address as ``*``, a random
  one will be generated.

``boot``
  Optional, boolean. Enable or disable start of the given Tinc VPN at boot
  time. By default all mesh networks are started at boot.

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

``tinc_options``
  Required. Dictionary variable which specifies options stored in the
  ``/etc/tinc/<network>/tinc.conf`` configuration file. Each key of the dict is
  the option name, values can be strings or lists of strings, in which case the
  option will be repeated as many times as there are elements in the list.

  To see the list of available options, check the ``tinc.conf(5)`` manual page.

``tinc_host_options``
  Optional. Dictionary variable which specifies options stored in the
  ``/etc/tinc/<network>/hosts/<hostname>`` configuration file. Each key of the
  dict is the option name, values can be strings or lists of strings, in which
  case the option will be repeated as many times as there are elements in the
  list.

  To see the list of available options, check the ``tinc.conf(5)`` manual page.

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

