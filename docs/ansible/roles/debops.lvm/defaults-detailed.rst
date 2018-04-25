Default variables: configuration
================================

Some of ``debops.lvm`` default variables have more extensive configuration than
simple strings or lists, here you can find documentation and examples for them.

.. contents::
   :local:
   :depth: 1

.. _lvm__volume_groups:

lvm__volume_groups
------------------

This is a list of LVM Volume Groups, each one defined by a YAML dict. Volume
Group is a set of Physical Volumes that create a single unit which can then be
divided into Logical Volumes. Dict parameters are mapped to the ``lvg`` Ansible
module options.

List of required parameters:

``vg``
  Name of a Volume Group, should only have alphanumeric characters and
  underscores.

``pvs``
  String (if single PV) or a list of Physical Volumes to use for a given Volume
  Group. Should be absolute paths to devices in :file:`/dev` directory tree, for
  example :file:`/dev/sda`.

List of optional parameters:

``state``
  Specifies if a given Volume Group should exist (``present``) or not
  (``absent``). If not specified, defaults to ``present``.

``force``
  Boolean. If present and set to ``True``, allows you to remove a Volume Group if
  it has any Logical Volumes present.

``pesize``
  Size of the physical extent, in megabytes, must be a power of 2. By default,
  4 MB extents are created. You cannot change the extent size of already
  existing Volume Groups.

``options``
  String with additional options passed to :command:`vgcreate`.

Examples
~~~~~~~~

Create a Volume Group using 1 Physical Volume::

    lvm__volume_groups:

      - vg: 'vg_alpha'
        pvs: '/dev/sda'

Create a Volume Group with multiple Physical Volumes::

    lvm__volume_groups:

      - vg: 'vg_multi'
        pvs: [ '/dev/sdb', '/dev/sdc' ]

.. _lvm__logical_volumes:

lvm__logical_volumes
--------------------

This is a list of LVM Logical Volumes, each one defined as a YAML dict. Logical
Volumes are slices of a Volume Group which can then be formatted with
a filesystem and mounted, or used as a block device. Dict parameters are mapped
to ``lvol``, ``filesystem`` and ``mount`` Ansible module options.

List of required parameters:

``lv``
  Name of a Logical Volume, should only have alphanumeric characters and
  underscores. Do not use hyphens (``-``) in the name.

``vg``
  Name of a Volume Group which should be used to create a given Logical Volume.

``size``
  Size of the Logical Volume, use the same format as these supported by
  ``lvol`` Ansible module.

List of optional LVM parameters:

``state``
  Specifies if a Logical Volume should exist (``present``) or not (``absent``).

``force``
  Boolean. If present and ``True`` allows ``lvol`` module to shrink or remove
  Logical Volumes.

List of optional filesystem parameters:

``fs``
  Boolean. Enables or disables creation of a filesystem in the new Logical Volume
  (existing Logical Volumes are not affected).

  By default, a filesystem specified in ``lvm_default_fs_type`` variable is
  created in all new Logical Volumes if ``item.mount`` is specified.

``fs_type``
  Specify filesystem type to use instead of the default. The same type will be
  used to mount the filesystem.

``fs_opts``
  Additional options passed to :command:`mkfs`.

``fs_force``
  Boolean. If present and ``True``, allows Ansible to reformat already existing
  filesystem. Use with caution.

``fs_resizefs``
  Boolean. If present and ``True``, and if the block device and filesystem size
  differ, grow the filesystem into the space. Note, XFS Will only grow if mounted.
  Use with caution especially if you shrink the volume.

List of optional mount parameters:

``mount``
  Path to a directory where a given Logical Volume should be mounted.
  If specified, a filesystem will be created automatically if needed.

``mount_state``
  Specify mount state of a given Logical Volume, either ``mounted`` (default),
  ``present``, ``unmounted`` or ``absent``. See ``mount`` Ansible module for
  explanation of the possible states.

``mount_opts``
  String with mount options added in :file:`/etc/fstab`. If not specified, options
  set in ``lvm__default_mount_options`` will be used instead.

``mount_fstab``
  Alternative path to :file:`/etc/fstab`.

``mount_dump``
  Filesystem :man:`dump(8)` backup frequency. See :man:`fstab(5)` for more details.

``mount_passno``
  Filesystem :command:`fsck` pass order. See :man:`fstab(5)` for more details.

Examples
~~~~~~~~

Create a Logical Volume::

    lvm__logical_volumes:

      - lv: 'not_formatted_volume'
        vg: 'vg_alpha'
        size: '2G'

Create a Logical Volume, format it and mount in a given path::

    lvm__logical_volumes:

      - lv: 'data'
        vg: 'vg_multi'
        size: '10G'
        mount: '/srv/data'

Remove a mounted Logical Volume (destroys the data)::

    lvm__logical_volumes:

      - lv: 'to_be_removed'
        vg: 'vg_multi'
        size: '5G'
        mount: '/srv/trash'
        state: 'absent'
        force: True

Resize a mounted Logical Volume::

    lvm__logical_volumes:

      - lv: 'data'
        vg: 'vg_multi'
        size: '15G'
        mount: '/srv/data'
        state: 'present'
        force: True
        fs_type: 'ext4'
        fs_resizefs: True

