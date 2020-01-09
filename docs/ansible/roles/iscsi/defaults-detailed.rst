Default variables: configuration
================================

some of ``debops.iscsi`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _iscsi__targets:

iscsi__targets
--------------

This is a list of iSCSI Targets, each one defined by a YAML dict. Dict
parameters are mapped to ``open_iscsi`` and ``lvg`` Ansible module options.

List of required parameters:

``target``
  iSCSI Qualified Name string which points to a specified iSCSI Target.

List of optional iSCSI parameters:

``auto``
  Bool. If present, lets you specify if a given iSCSI Target should be logged
  into on system boot. By default all iSCSI Targets are logged into
  automatically.

``login``
  Bool. If present, lets you specify if a given iSCSI Target should be
  connected (``True``) or disconnected (``False``).

``auth``
  Bool. Enable or disable iSCSI session authentication per iSCSI Target.

``auth_username``
  iSCSI session username used for this iSCSI Target, you can use this parameter
  to override global username set in ``iscsi_session_auth_username``.

``auth_password``
  iSCSI session password used for this iSCSI Target, you can use this parameter
  to override global password set in ``iscsi_session_auth_password``.

List of optional LVM parameters:

``lvm_vg``
  Name of a LVM Volume Group which should be created using all iSCSI LUNs
  presented by a given iSCSI Target. Should only have alphanumeric characters
  and underscores. Do not use hyphens (``-``) in the name.

``lvm_state``
  Specifies if a given Volume Group should exist (``present``) or not
  (``absent``). If not specified, defaults to ``present``.

``lvm_force``
  Bool. If present and set to ``True``, allows you to remove a Volume Group if
  it has any Logical Volumes present.

``lvm_pesize``
  Size of the physical extent, in megabytes, must be a power of 2. By default,
  4 MB extents are created. You cannot change the extent size of already
  existing Volume Groups.

``lvm_options``
  String with additional options passed to ``vgcreate``.

Examples
~~~~~~~~

Connect to an iSCSI Target using global session authentication settings::

    iscsi__targets:

      - target: 'iqn.1995-08.org.example:server:storage'

Connect to an iSCSI Target using ``iscsi__iqn`` value for IQN base string (must
be the same on the iSCSI Target) and custom session credentials::

    iscsi__targets:

      - target: '{{ iscsi__iqn + ":server:storage" }}'
        auth: True
        auth_username: 'custom_user'
        auth_password: 'custom_password'

Connect to an iSCSI Target and create a LVM Volume Group from all of the
presented iSCSI LUNs::

    iscsi__targets:

      - target: '{{ iscsi__iqn }}:server:storage'
        lvm_vg: 'vg_iscsi_target'


.. _iscsi__logical_volumes:

iscsi__logical_volumes
----------------------

This is a list of LVM Logical Volumes, each one defined as a YAML dict. Logical
Volumes are slices of a Volume Group which can then be formatted with
a filesystem and mounted, or used as a block device. Dict parameters are mapped
to ``lvol``, ``filesystem`` and ``mount`` Ansible module options.

For consistency reasons, you should only use iSCSI-backed Volume Groups to
configure Logical Volumes using this variable.

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
  Bool. If present and ``True`` allows ``lvol`` module to shrink or remove
  Logical Volumes.

List of optional filesystem parameters:

``fs``
  Bool. Enables or disables creation of a filesystem in the new Logical Volume
  (existing Logical Volumes are not affected).

  By default, a filesystem specified in ``iscsi__default_fs_type`` variable is
  created in all new Logical Volumes if ``item.mount`` is specified.

``fs_type``
  Specify filesystem type to use instead of the default. The same type will be
  used to mount the filesystem.

``fs_opts``
  Additional options passed to ``mkfs``.

``fs_force``
  Bool. If present and ``True``, allows Ansible to reformat an already existing
  filesystem. Use with caution.

List of optional mount parameters:

``mount``
  Path to a directory where a given Logical Volume should be mounted.
  If specified, a filesystem will be created automatically if needed.

``mount_state``
  Specify mount state of a given Logical Volume, either ``mounted`` (default),
  ``present``, ``unmounted`` or ``absent``. See ``mount`` Ansible module for
  explanation of the possible states.

``mount_opts``
  String with mount options added in ``/etc/fstab``. If not specified, options
  set in ``iscsi__default_mount_options`` will be used instead.

  Make sure that ``_netdev`` option is present in your mount options, to not
  block the system startup.

``mount_fstab``
  Alternative path to ``/etc/fstab``.

``mount_dump``
  Filesystem ``dump(8)`` backup frequency. See ``fstab(5)`` for more details.

``mount_passno``
  Filesystem ``fsck`` pass order. See ``fstab(5)`` for more details.

Examples
~~~~~~~~

Create a Logical Volume::

    iscsi__logical_volumes:

      - lv: 'not_formatted_volume'
        vg: 'vg_iscsi_target'
        size: '2G'

Create a Logical Volume, format it and mount in a given path::

    iscsi__logical_volumes:

      - lv: 'data'
        vg: 'vg_iscsi_target'
        size: '10G'
        mount: '/srv/data'

Remove a mounted Logical Volume (destroys the data)::

    iscsi__logical_volumes:

      - lv: 'to_be_removed'
        vg: 'vg_iscsi_target'
        size: '5G'
        mount: '/srv/trash'
        state: 'absent'
        force: True

