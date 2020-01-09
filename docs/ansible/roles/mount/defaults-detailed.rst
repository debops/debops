Default variable details
========================

Some of ``debops.mount`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _mount__ref_devices:

mount__devices
--------------

The ``mount__*_devices`` variables define a list of YAML dictionaries that
configure local device mounts. They can be used to configure any mount type,
however remote devices should be avoided (the role is executed early in the
DebOps ``common.yml`` playbook, when network configuration might not be
finished), and bind mounts have their own set of variables and a separate task
to allow creation of source directories.

The role does not create new filesystems, the devices configured by it should
have their own filesystems configured and formatted beforehand.

Examples
~~~~~~~~

Create an :file:`/etc/fstab` entry for a disk drive that's not mounted on boot,
with specific filesystem type:

.. code-block:: yaml

   mount__devices:

     - name: '/media/backups'
       src: '/dev/sdb1'
       fstype: 'ext4'
       opts: 'defaults,noauto,nofail'

Create an automount entry for an USB drive using :command:`systemd` automount
functionality (you can find its UUID with :command:`lsblk -f` command):

.. code-block:: yaml

   mount__devices:

     - name: '/media/USB_Stick'
       src: 'UUID=aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
       opts: [ 'defaults', 'noauto', 'nofail', 'x-systemd.automount',
               'x-systemd.idle-timeout=2', 'x-systemd.device-timeout=2',
               'x-systemd.mount-timeout=2' ]

       # Without this, Ansible tries to mount the drive right away which
       # results in an error
       state: 'present'

Syntax
~~~~~~

Each ``mount__*_devices`` list entry is a YAML dictionary with specific
parameters. Most of the parameters are the same as the Ansible ``mount``
module:

``src``
  Required. A device name which will be mounted at a given path. It can be
  a block device file in :file:`/dev` directory, or a label, or device UUID.
  See :man:`fstab(5)` manual page, first field description for more details.

``path`` / ``dest`` / ``name``
  Required. Absolute path in the filesystem where a given device will be
  mounted.

``fstype``
  Optional. Specify the filesystem type to use with a given device. If not
  specified, ``auto`` will be used to perform autodetection.

``opts``
  Optional. String (comma-delimited) or YAML list of options for a given mount
  point. If not specified, ``defaults`` will be used instead.

``dump``
  Optional. This field determines which filesystems should be backed up by the
  :man:`dump(8)` command. If not specified, ``0`` is set by default.

``passno``
  Optional. This field determines the order of the filesystem checks on boot
  done by the :man:`fsck(8)` command. The root filesystem should be it set to
  ``1``, other filesystems should be set to ``2``. If not specified, it
  defaults to ``0``, which disables filesystem checks on boot.

``state``
  Optional. If not specified or ``mounted``, the device entry will be added to
  the :file:`/etc/fstab` database and it will be automatically mounted.
  Unmounted devices will be mounted again. If the mount point directory is not
  present, it will be automatically created.

  If ``present``, the device entry will be added to :file:`/etc/fstab`, but
  Ansible will not try to mount it right away (preferable for automounted
  devices). Already mounted devices will not be changed.

  If ``unmounted``, Ansible will try and unmount the already mounted device.
  The :file:`/etc/fstab` database will not be changed, however missing entries
  will be added.

  If ``absent``, the mounted device will be unmounted, and the
  :file:`/etc/fstab` database entry, along with the mount point directory, will
  be removed.

``fstab``
  Optional. Absolute path of the alternative :man:`fstab(5)` database to use
  instead of the default :file:`/etc/fstab` database.

Additional parameters control functions outside of the Ansible ``mount``
module:

``device``
  Optional. The role creates the required mount points by itself instead of
  letting the Ansible ``mount`` module do it; this allows for fine-grained
  control over initial mount point attributes. The task that creates the mount
  points is not executed when they are actually mounted - the role checks if
  the ``src`` parameter is present in the ``ansible_mounts`` fact entries as
  the ``device`` dictionary key.

  In case that the ``src`` parameter and the expected ``device`` dictionary key
  are different, you can set the ``device`` parameter to override the check.

``owner``
  Optional. Specify the UNIX account that will be the owner of the initial
  mount point, before the device is mounted. If not specified, ``root`` will be
  the owner.

``group``
  Optional. Specify the UNIX group that will be the group of the initial mount
  point, before the device is mounted. If not specified, the value of ``owner``
  is used, otherwise ``root`` will be the group.

``mode``
  Optional. Specify the UNIX permissions that will be applied to the initial
  mount point, before the device is mounted. If not specified, ``0755`` will be
  set by default.


.. _mount__ref_directories:

mount__directories
------------------

The ``mount__*_directories`` variables are list of YAML dictionaries, each
entry defining a directory in the filesystem, with optional attributes.  These
variables can be used to create, modify or remove directories in the
filesystems after they are mounted.

Examples
~~~~~~~~

Create a directory owned by root on the mounted filesystem:

.. code-block:: yaml

   mount__directories:

     - path: '/media/USB_Stick/Private'

Create directory for data sharing btween unprivileged LXC containers. This
assumes that the unprivileged LXC containers are started by ``root`` and use
subUID/subGID range defined by the :ref:`debops.root_account` Ansible role:

.. code-block:: yaml

   mount__directories:

     - path: '/srv/shared/lxc-opt'
       owner: '100000'
       group: '100000'
       mode: '0751'

Create directory with custom ACL permissions that allows the ``www-data``
UNIX group to write files:

.. code-block:: yaml

   mount__directories:

     - path: '/srv/www'

     - path: '/srv/www/data'
       owner: 'root'
       group: 'root'
       mode: '0750'
       acl:
         - entity: 'www-data'
           etype: 'group'
           permissions: 'rwx'

Syntax
~~~~~~

The ``mount__*_directories`` lists contain YAML dictionaries, each dictionary
can have specific parameters, that reflect the Ansible ``file`` module
parameters:

``path`` / ``dest`` / ``name``
  Required. Absolute path of the directory that is managed by the role.

``owner``
  Optional. Specify the UNIX account that should be the owner of the directory.
  If not specified, ``root`` is used by default.

``group``
  Optional. Specify the UNIX group that should be the main group of the given
  directory. If not specified, the value of ``owner`` is used by default,
  otherwise ``root`` is set.

``mode``
  Optional. Set the permissions of the managed directory. If not specified,
  ``0755`` will be used by default.

``recurse``
  Optional, boolean. If defined and ``True``, the role will set the specified
  permissions and ownership recursively to all subdirectories of the given
  directory as well as to the directory itself.

``state``
  Optional. If not specified or ``directory``, the given directory will be
  created or updated with the specified permissions and ownership. If
  ``absent``, the given directory will be removed. Other values of the
  ``state`` parameter are ignored in this role.

``acl``
  Optional. This parameter defines Access Control List entries for a given
  directory, each entry is a YAML dictionary with specific parameters:

  ``entity``
    Name of the ACL entity to manage, either UNIX account or UNIX group.

  ``etype``
    The entity type of a given ACL, check the :man:`setfacl(1)` manual page for
    more details. Choices: ``user``, ``group``, ``other``, ``mask``.

  ``permissions``
    Specify the permissions to set for a given ACL entry, they can be
    a combination of ``r`` (read), ``w`` (write) and ``x`` (execute).

  ``default``
    Optional, boolean. If defined and ``True``, a given ACL entry will be the
    default for all entities created inside of a given directory.

  ``follow``
    Optional, boolean. If set and ``True``, the Ansible module will follow the
    symlinked directory to the symlink target and change its attributes instead
    of the symlink attributes.

  ``recursive``
    Optional, boolean. If set and ``True``, the Ansible module will apply the
    specified ACL to all objects in a given path.

  ``state``
    Optional. If not set or ``present``, the ACL entry will be added to the
    current object. If ``absent``, the ACL entry will be removed from the
    current path.


.. _mount__ref_binds:

mount__binds
------------

The ``mount__*_binds`` variables can be used to create bind mounted directories
in the filesystem. Bind mounts are similar to symlinks, where a given directory
is mounted at a different place in the filesystem. This can be used to give
access to parts of the filesystem in a different namespace, for example in
a LXC container.

The task that manages the bind mounts are separate from the "normal" mounts to
allow the system to mount devices that could have parts of their filesystem
bind-mounted later on.

Examples
~~~~~~~~

Bind mount the USB drive at a different point in the filesystem:

.. code-block:: yaml

   mount__binds:

     - src: '/media/USB_Stick'
       dest: '/srv/removable/data'

Syntax
~~~~~~

Each ``mount__*_binds`` list entry is a YAML dictionary with specific
parameters. The parameters are the same as the Ansible ``mount`` module:

``src``
  Required. A directory name which will be bind mounted at a given path. The
  directory should already exist. You can use the :ref:`mount__ref_directories`
  variables to create the directories beforehand.

``path`` / ``dest`` / ``name``
  Required. Absolute path in the filesystem where a given directory will be
  bind mounted.

``fstype``
  Optional. Specify the filesystem type to use with a given device. If not
  specified, ``none`` will be used, which is required for bind mounts.

``opts``
  Optional. String (comma-delimited) or YAML list of options for a given mount
  point. If not specified, ``bind`` will be used instead.

``dump``
  Optional. This field determines which filesystems should be backeed up by the
  :man:`dump(8)` command. If not specified, ``0`` is set by default.

``passno``
  Optional. This field determines the order of the filesystem checks on boot
  done by the :man:`fsck(8)` command. The root filesystem should be it set to
  ``1``, other filesystems should be set to ``2``. If not specified, it
  defaults to ``0``, which disables filesystem checks on boot.

``state``
  Optional. If not specified or ``mounted``, the bind mount entry will be added
  to the :file:`/etc/fstab` database and it will be automatically mounted.
  Unmounted bind directories will be mounted again. If the mount point
  directory is not present, it will be automatically created.

  If ``present``, the bind mount entry will be added to :file:`/etc/fstab`, but
  Ansible will not try to mount it right away (preferable for automounted
  devices). Already mounted bind directories will not be changed.

  If ``unmounted``, Ansible will try and unmount the already bind mounted
  directories.  The :file:`/etc/fstab` database will not be changed, however
  missing entries will be added.

  If ``absent``, the bind mounted directory will be unmounted, and the
  :file:`/etc/fstab` database entry, along with the mount point directory, will
  be removed.

``fstab``
  Optional. Absolute path of the alternative :man:`fstab(5)` database to use
  instead of the default :file:`/etc/fstab` database.
