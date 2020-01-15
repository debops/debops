Default variable details
========================

Some of ``debops.nfs`` default variables have more extensive configuration than
simple strings or lists, here you can find documentation and examples for them.

.. contents::
   :local:
   :depth: 1

.. _nfs__ref_shares:

nfs__shares
-----------

The :envvar:`nfs__shares`, :envvar:`nfs__group_shares` and
:envvar:`nfs__host_shares` are list of NFS shares to configure on a host. Each
list element is a YAML dictionary with specific parameters:

``path``
  Required. Absolute path of a directory where the given NFS share should be
  mounted. If the directory does not exist, it will be created by the role.

``src``
  Required. Mount point "source", usually in the form of:

  .. code-block:: none

     <hostname>:/<share_path>

  You can use either DNS names or IP addresses.

  NOTE: If you want to use NFSv4 mount points, you need to specify share paths
  relative to the NFS ``root`` directory configured on the nfs server.

``state``
  Optional. If not specified or ``mounted``, the given NFS share will be added
  to the :file:`/etc/fstab` configuration file and automatically mounted. If
  ``present``, the NFS mount will be added to the :file:`/etc/fstab` but its
  state will not be changed. If ``unmounted``, and the NFS share is mounted, it
  will be unmounted. If ``absent``, the NFS share will be unmounted and its
  entry will be removed from :file:`/etc/fstab` configuration file.

``options`` or ``opts``
  Optional. A comma-separated string or a YAML list of :command:`mount` options
  which should be used with a given NFS share. If not specified, the role will
  use a set of default options that configure the mount to be a network NFS4
  share.

``default_options``
  Optional, boolean. If present and ``False``, the role will not add the
  default options to the custom ones provided by the user, which will allow
  full control over the configuration. The ``_netdev`` option is always added
  to ensure that the :file:`/etc/fstab` configuration file remains valid.

``fstype``
  Optional. Specify the filesystem type to use for the mount point. By default
  it's ``nfs4``.

``passno``, ``dump``, ``fstab``
  Optional. Additional parameters passed to the Ansible ``mount`` module, by
  default omitted since they are not useful for NFS shares. See the module
  documentation page for more details.

``owner``, ``group``, ``mode``
  Optional. Specify UNIX account, group and directory permissions for the mount
  point of a given NFS share. They will be applied to the directories created
  by the role when the NFS share is not mounted immediately.

Examples
~~~~~~~~

Mount a NFS4 share with automatic configuration:

.. code-block:: yaml

   nfs__shares:
     - path: '/media/nfs/shared'
       src: 'nas.example.org:/shared'
