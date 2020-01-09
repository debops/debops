.. _nfs_server__ref_defaults_detailed:

Default variable details
========================

Some of ``debops.nfs_server`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1

.. _nfs_server__ref_exports:

nfs_server__exports
-------------------

This set of YAML lists can be used to define NFS exports. See the
:man:`exports(5)` for more information about possible configuration
options.

Each list entry is a YAML dictionary with specific parameters:

``path``
  Required. Absolute path of the directory which will be exported by NFS. With
  NFS4, this path should be a subdirectory of the NFS4 root pseudo-filesystem,
  which by default is defined as :file:`/srv/nfs`. Refer to the
  :envvar:`nfs_server__root_path` to see the current value.

  The role will create this directory if it doesn't exist. You can use the
  ``owner``, ``group`` and ``mode`` parameters to affect the directory
  ownership and attributes.

``options``
  A string or a YAML list of the parameters set for a given NFS export. If it's
  a string, each parameter needs to be delimited by a comma (``,``) for the
  role to properly recognize the parameters and convert to a YAML list for
  internal processing.

``bind``
  Optional. Absolute path of the directory on the remote host which will be
  bind-mounted to the specified ``path``. This is useful when you want to
  export directories that are outside of the NFS4 root pseudo-filesystem.

  ``src``
    A string acting the same way as if you assigned the value directly
    to the ``bind`` option.

  ``options``
    A list of extra option to add to the mount. Useful if you need special
    behavior like waiting for other services to be started before the mount.

``acl``
  Required. Access Control List of a given NFS export. This can be either
  a string (hostname, NIS netgroup, single IP address, single CIDR subnet), or
  a list of these elements. Alternatively, you can specify a list of YAML
  dictionaries, each dictionary with specific parameters:

  ``client`` or ``clients``
    A string or YAML list of valid NFS client definitions.

  ``options``
    A string or YAML list of NFS export parameters defined for these clients.

  ``state``
    Either ``present`` or ``absent``, enables or disables a given client entry.

``comment``
  Optional. A string or a YAML text block with a comment added to a given NFS
  export.

``state``
  Optional. If not specified or ``present``, the NFS export will be present in
  the configuration file. If ``absent``, the NFS export will not be present in
  the generated configuration file. This does not have any effect on any
  bind-mounted directories.

Examples
~~~~~~~~

Export NFS4 directories from the default :file:`/etc/exports` configuration
file. This is just an example, and the role provides the NFS4 root filesystem
automatically, in a different directory.

.. code-block:: yaml

   nfs_server__exports:

     - path: '/srv/nfs4'
       options: 'rw,sync,fsid=0,crossmnt,no_subtree_check'
       acl: 'gss/krb5i'

     - path: '/srv/nfs4/homes'
       options: 'rw,sync,no_subtree_check'
       acl: 'gss/krb5i'

Export the :file:`/usr` directory read-only, by bind-mounting it to the NFS4
root filesystem. Anyone can access it, barring any firewall configuration:

.. code-block:: yaml

   nfs_server__exports:
     - path: '/srv/nfs/usr'
       bind: '/usr'
       options: [ 'ro', 'no_subtree_check', 'async' ]
       acl: '*'

Export the :file:`/srv/media` directory for different clients on the two
networks, with different set of parameters:

.. code-block:: yaml

   nfs_server__exports:
     - path: '/srv/nfs/media'
       bind: '/srv/media'
       acl:

         - clients: '192.0.2.0/24'
           options: 'ro,no_subtree_check,async'

         - clients: [ '2001:db8:dead:beef::/64', '*.example.org' ]
           options: [ 'rw', 'no_subtree_check', 'no_root_squash' ]

Export the :file:`/usr` directory read-only, by bind-mounting it to the NFS4
root filesystem, but only after the ZFS service has started.
Anyone can access it, barring any firewall configuration:

.. code-block:: yaml

   nfs_server__exports:
     - path: '/srv/nfs/usr'
       bind:
         src: '/usr'
         options:

           - 'x-systemd.requires=zfs-mount.service'

       options: [ 'ro', 'no_subtree_check', 'async' ]
       acl: '*'
