Examples
========

Add additional/custom options to smb.conf
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Not every option of upstream Samba's smb.conf is available as role variable in debops.samba.
So to specify these additional parameters you may add them to the hash `samba__global_custom`

example of host_vars for enabling Windows style ACLs:

    .. code:: shell

    samba__global_custom:
      vfs_objects: 'acl_xattr'
      map_acl_inherit: 'yes'
      store_dos_attributes: 'yes'

    # above vfs_objects setting needs additional vfs-modules pkg installed
    samba__base_packages:
      - 'samba'
      - 'samba-common'
      - 'samba-common-bin'
      - 'samba-vfs-modules'
