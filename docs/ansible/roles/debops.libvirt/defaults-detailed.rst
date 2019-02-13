Default variables: configuration
================================

Some of ``debops.libvirt`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _libvirt__connections:

libvirt__connections
--------------------

This is a dictionary variable which defines ``libvirt`` connections and their
aliases. Each key is an alias of a given connection. Currently only local and
SSH connections are supported by the role.

Examples
~~~~~~~~

Define local and remote ``libvirt`` connections::

    libvirt__connections:
      'localhost':  'qemu:///system'
      'vm-host':    'qemu+ssh://vm.example.org/system'
      'local-lxc':  'lxc:///'
      'lxc-host':   'lxc+ssh://lxc.example.org/'

.. _libvirt__networks:

libvirt__networks
-----------------

This is a list of network definitions specified as YAML dicts. Each dict
defines separate network interface which then can be configured and enabled in
``libvirt``.

List of parameters supported by all network types:

``name``
  Required. Name of the network interface used as a handle in ``virsh`` and
  ``virt-manager``.

``type``
  Required. Specifies what XML template will be used to configure the interface.
  Different templates might require different parameters.

  Currently supported templates are:

  - ``bridge``: Network will be configured as a simple host bridge, all
    configuration is done on the host (outside of ``libvirt``). You need to
    specify ``item.bridge`` parameter as name of the host bridge to use.

  - ``dnsmasq``: Network will be configured as a bridge with ``dnsmasq`` used
    as internal DNS and DHCP server.

``bridge``
  Required. Name of the network interface to use.

``state``
  Specify the state the network should be in. If not specified, interface will
  be defined and started automatically. Known states:

  ``undefined`` or ``absent``:
    Network will be destroyed if active and removed from ``libvirt``
    configuration.

  ``present``:
    Network will be defined in ``libvirt`` but will not actively start at the
    creation time. It might or might not start on boot depending on
    ``item.autostart`` parameter.

  ``active``:
    Network will be defined if not present and automatically started at
    creation time, or if it's inactive.

``autostart``
  Boolean, optional, defaults to ``True``. Specify if a network should start
  (``True``) or not (``False``) at boot time.

``uri``
  Name of the ``libvirt`` connection configured in
  :file:`~/.config/libvirt/libvirt.conf` to use to configure this network. If not
  specified, default connection (most likely ``localhost`` which is an alias
  configured to ``qemu:///system`` by default) is used.

``interface_present``
  Specify a name of a network interface on the host; network will be configured
  only when a specified interface exists. This only works in the "local mode",
  not on remote ``libvirt`` connections.

List of parameters supported by ``dnsmasq`` network type:

``addresses``
  List of IPv4 or IPv6 addresses in ``host/prefix`` format. These IP addresses
  will be configured on the create bridge. If DHCP is enabled, it will be
  configured only on first IPv4 and first IPv6 network specified (``libvirt``
  limitation).

``forward``
  Boolean. If specified, traffic to external networks will be forwarded to the
  upstream interface.

``forward_mode``
  Name of the forward mode to use. If not specified, ``nat`` will be configured
  by default. See `libvirt network documentation
  <http://wiki.libvirt.org/page/VirtualNetworking>`_ for more details.

``dhcp``
  Boolean. If present and ``True``, enable DHCP server for this network. Only
  first subnet of each type (IPv4, IPv6) will have DHCP configured.

``dhcp_range``
  List which specifies start and end of DHCP range offered to hosts in the
  network. If not specified, ``[ '10', '250' ]`` is used by default to fit in
  ``/24`` CIDR network.

``domain``
  DNS domain to sent to hosts by DHCP server.

``domain_local``
  Boolean. Specify if requests that don't exist for local domain in ``dnsmasq``
  should be forwarded to upstream DNS servers (they are forwarded by default).

``bootp``
  Boolean. Enable or disable support for BOOTP/PXE options in DHCP server.

``bootp_file``
  File path sent to the host which instructs them to download a given file from
  TFTP server. If none is specified, :file:`/undionly.kpxe` is used, which is
  default for iPXE.

``bootp_server``
  IP address of the TFTP server to which hosts are redirected by DHCP server.
  If it's not set, DHCP server points hosts to its own IP address.

Examples
~~~~~~~~

Create host bridge network, only if a given bridge exists::

    libvirt__networks:
      - name: 'external'
        type: 'bridge'
        bridge: 'br0'
        interface_present: 'br0'

Create a NAT network on remote ``libvirt`` host::

    libvirt__networks:
      - name: 'nat'
        type: 'dnsmasq'
        bridge: 'virbr0'
        addresses: [ '192.0.2.1/24', '2001:db8:ab::1/64' ]
        forward: True
        dhcp: True
        uri: 'vm-host'

.. _libvirt__pools:

libvirt__pools
--------------

This is a list of storage pool definitions specified as YAML dicts. Each dict
defines separate storage pool which then can be configured and enabled in
``libvirt``.

List of parameters supported by all storage pool types:

``name``
  Required. Name of the storage pool used as a handle in ``virsh`` and
  ``virt-manager``.

``type``
  Required. Specifies what XML template will be used to configure the pool.
  Different templates might require different parameters.

  Currently supported templates are:

  ``dir``:
    Storage pool will be configured as a directory in existing filesystem. You
    need to specify an absolute path to a directory using ``item.path``
    parameter.

    Directory should already exist before storage pool can be activated,
    otherwise you can create it using the ``build`` command.

  ``nfs``:
    Storage pool is a directory exported from a NFS server, which will be
    mounted on a given path. See below for supported parameters.

  - ``logical``:
    Storage pool is a LVM volume group which can be located on local or remote
    block device(s). See below for supported parameters.

``state``
  Specify the state the storage pool should be in. If not specified, pool will
  be defined and started automatically. Known states:

  ``deleted``:
    Storage pool contents will be erased (this is a destructive
    operation), and it will be undefined afterwards.

  - ``undefined`` or ``absent``: storage pool will be destroyed if active and
    removed from ``libvirt`` configuration.

  - ``present``: storage pool will be defined in ``libvirt`` but will not
    actively start at the creation time. It might or might not start on boot
    depending on ``item.autostart`` parameter. Storage pool might need to be
    built before it can be activated, which can be done using ``build``
    command.

  - ``inactive``: storage pool will be stopped if present.

  - ``active``: storage pool will be defined if not present and automatically
    started at creation time, or if it's inactive.

``autostart``
  Boolean, optional, defaults to ``True``. Specify if a storage pool should
  start (``True``) or not (``False``) at boot time.

``uri``
  Name of the ``libvirt`` connection configured in
  ``~/.config/libvirt/libvirt.conf`` to use to configure this storage pool. If
  not specified, default connection (most likely ``localhost`` which is an
  alias configured to ``qemu:///system`` by default) is used.

List of parameters supported by ``nfs`` storage pool type:

``host``
  IP address or hostname of NFS server which holds the exported filesystem.

``src``
  Path on the NFS server with exported filesystem, for example :file:`/srv/nfs`.

``path``
  Path in the local filesystem where remote NFS share should be mounted, for
  example :file:`/media/nfs/remote-vm`. If this directory does not exist, it will
  be created by ``debops.libvirt`` role automatically.

List of parameters supported by ``logical`` storage pool type:

``name``
  Name of the storage pool will be used as name of the LVM Volume Group.

``devices``
  List of block devices which should be used to create LVM Volume Group. If
  this list is defined, ``debops.libvirt`` will run the ``build`` command to
  attempt and create new Volume Group. If it's not specified, existing Volume
  Group will be configured instead (it can be created beforehand using LVM
  commands).

Examples
~~~~~~~~

Create a directory storage pool on local machine (default ``libvirt`` storage pool::

    libvirt__pools:
      - name: 'default'
        type: 'dir'
        path: '/var/lib/libvirt/images'

Create a NFS-based storage pool on remote ``libvirt`` host::

    libvirt__pools:
      - name: 'nfs-pool'
        type: 'nfs'
        host: 'nfs.example.org'
        src:  '/srv/nfs'
        path: '/media/nfs/libvirt'
        uri:  'vm-host'

Create a LVM-based storage pool from existing Volume Group::

    libvirt__pools:
      - name: 'vg_kvm'
        type: 'logical'

.. meta::
   :description: Documentation for specific debops.libvirt variables
   :keywords: libvirt, libvirt storage, libvirt storage pools,
              network, libvirt network, libvirt networks,
              libvirt connection, libvirt connections

