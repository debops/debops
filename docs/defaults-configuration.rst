Default variables: configuration
================================

some of ``debops.tgt`` default variables have more extensive configuration than
simple strings or lists, here you can find documentation and examples for them.

.. contents::
   :local:
   :depth: 1

.. _tgt_targets:

tgt_targets
-----------

This is a list of iSCSI Targets configured on the host. Each iSCSI Target can
have multiple backing stores with custom configuration. Examples of options
which can be passed to the ``tgt`` configuration can be found in
``/usr/share/doc/tgt/examples/targets.conf.example.gz``.

List of recognized iSCSI Target parameters:

``name``
  Required. Target name, added after ``tgt_iqn_base`` string, used also as the
  filename of the configuration file in ``/etc/tgt/conf.d/*.conf`` if
  ``item.filename`` is not specified.

``filename``
  Alternative name of the configuration file.

``iqn``
  Custom IQN string used instead of the default one.

``options``
  ``tgt`` options added to a given target, in YAML text block format.

``backing_stores``
  List of volumes present in a given iSCSI Target (see below).

``direct_stores``
  List of "passthrough" volumes present in a given iSCSI Target (see below).

``delete``
  If present and ``True``, this iSCSI Target configuration will be removed from
  the configuration directory; if a given target is not used at the moment of
  deletion, it will also be removed from the server.

iSCSI backing/direct stores
---------------------------

To provide a given volume through iSCSI, you need to specify it in a given
target as either a ``backing-store`` or ``direct-stre``. Direct stores read
some metadata from storage devices and are more suited to export real hardware
storage media, backing stores are more suited to export logical volumes, block
devices or files.

To configure a set of stores, you can specify them directly in ``item.options``
parameter::

    tgt_targets:

      - name: 'hostname.data'
        options: |
          backing-store /dev/sdc
          backing-store /dev/sdd

There are also available separate lists, ``backing_stores`` and
``direct_stores``. Using these, you can specify a YAML list of block devices or
files to add to the iSCSI Target::

    tgt_targets:

      - name: 'hostname.data'
        backing_stores: [ '/dev/sdc', '/dev/sdd' ]

If you need to specify additional per-store options, you can specify them as
dicts instead::

    tgt_targets:

      - name: 'hostname.data'
        backing_stores:

          - store: '/dev/sdc'
            options: |
              lun 1

          - store: '/dev/sdd'
            options: |
              lun 2

**Warning**: you need to make sure to only use one of these definition types in
an iSCSI Target, ie. either a simple list of stores or a list of dicts which
define stores. Never mix them, otherwise the ``tgt`` configuration parser won't
be able to correctly parse the configuration files.

Other examples
--------------

How to create an iSCSI Target with an image file presented as a CD/DVD drive::

    tgt_targets:

      - name: 'install.debian.wheezy'

        backing_stores:
          - '/srv/tgt/image/install/debian-7.8.0-amd64-i386-netinst.iso'

        options: |
          device-type cd
          readonly 1
          MaxConnections 10

