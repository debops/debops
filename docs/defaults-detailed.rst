.. _cryptsetup__ref_default_variable_details:

Default variable details
========================

.. include:: includes/all.rst


Some of ``debops.cryptsetup`` variables have more extensive configuration.
Here you can find documentation and examples for them.


.. _cryptsetup__devices:

cryptsetup__devices
-------------------

The :envvar:`cryptsetup__devices` and similar lists allow you to specify
device configuration. Each item of those lists is a dictionary with the following keys:

Note the following list only documents the common parameters. The role allows
you to use more specific parameters which are not documented below.

``name``
  Required, string. Name of the plaintext device mapper target and the mount point.
  Must be unique among all device mapper targets and should not be changed once
  it was used.

  If you want to change it, you can set :ref:`state <cryptsetup__devices_state>`
  to :ref:`absent <cryptsetup__devices_state_absent>`, execute the role, rename
  the secrets directory corresponding to the name name, adapt your inventory
  accordingly and run the role again to configure the item with the new name.

``ciphertext_block_device``
  Required, string. File path to the ciphertext block device, either the block
  device itself e. g. :file:`/dev/sdb` or a partition on the block device e. g.
  :file:`/dev/sdb5`.

.. _cryptsetup__devices_crypttab_options:

``crypttab_options``
  Optional, list of strings. Each string represents an option to configure for
  each device in :file:`/etc/crypttab`. See :manpage:`crypttab(5)` for details.
  Default to :envvar:`cryptsetup__crypttab_options`.

``keyfile``
  Optional, string. File path for the keyfile on the Ansible controller. Will
  be copied over to the remote system. If it does not exist yet it will be
  generated using the systems random number generator on the Ansible controller
  as it is expected that the entropy pool on the Ansible controller is better
  mixed.
  Defaults to:

  .. code:: jinja

     {{ cryptsetup__secret_path + "/" + item.name + "/keyfile.raw" }}

.. _cryptsetup__devices_backup_header:

``backup_header``
  Optional, boolean. Should a header backup be created and stored
  on the remote system and the Ansible controller?

  .. note:: The LUKS header is only stored once in the first few kilobytes of
     a given block device.
     When the header gets corrupted, the plaintext data might be inaccessible!
     Thus it is recommended to have a header backup on hand.

  Set to ``False`` to disable header backup creation and to ensure that the
  header backup is absent on the remote system.
  Defaults to :envvar:`cryptsetup__header_backup`.

.. _cryptsetup__devices_manage_filesystem:

``manage_filesystem``
  Optional, boolean. Should a filesystem be created on the plaintext device mapper
  target and configured in :file:`/etc/fstab`?
  Defaults ``True``.

.. _cryptsetup__devices_fstype:

``fstype``
  Optional, string. Filesystem to create on the plaintext device mapper
  target and configure in :file:`/etc/fstab`.
  Defaults to :envvar:`cryptsetup__fstype`.

.. _cryptsetup__devices_mount:

``mount``
  Optional, string. Plaintext mount point of the filesystem.
  Defaults to:

  .. code:: jinja

    {{ cryptsetup__mountpoint_parent_directory + "/" + item.name }}

.. _cryptsetup__devices_mount_options:

``mount_options``
  Optional, list of strings. Mount options associated with the filesystem.
  For more details see :manpage:`mount(8)`.
  Defaults to :envvar:`cryptsetup__mount_options`.

.. _cryptsetup__devices_state:

``state``
  Optional, string. There are four states which can be chosen for each
  encrypted filesystem.
  Defaults to :envvar:`cryptsetup__state`.

  .. _cryptsetup__devices_state_mounted:

  ``mounted``
    Ensure that the encryption and filesystem layer are in place on the block device and
    the filesystem is mounted.

  .. _cryptsetup__devices_state_ansible_controller_mounted:

  ``ansible_controller_mounted``
    Same as :ref:`mounted <cryptsetup__devices_state_mounted>` except that the
    keyfile is never stored on persistent storage of the remote system.
    Might be useful when you don’t have a secure place to store the keyfile on
    the remote system. With this option you will be required to run this role
    after each reboot to mount the filesystem again.

    Note that the implicit default for ``crypttab_options`` and
    ``mount_options`` is ``auto`` which means that your init system will try to
    mount the filesystem on boot and might drop you to a root shell if it
    can’t.

    To avoid this, you need to set the following options for the item::

      crypttab_options: '{{ ["noauto"] + (cryptsetup__crypttab_options|d([]) | list) }}'
      mount_options: '{{ ["noauto"] + (cryptsetup__mount_options|d([]) | list) }}'

    Note that this option is currently not idempotent because it copes the
    keyfile to the remote system and erases it again.

  .. _cryptsetup__devices_state_unmounted:

  ``unmounted``
    Ensure that the encryption and filesystem layer are in place on the block device and
    the filesystem is unmounted. Additionally ensures that the cryptsetup mapping
    is removed so that no direct access to the plain-text block device is possible.

  .. _cryptsetup__devices_state_present:

  ``present``
    Ensure that the encryption and filesystem layer are in place on the block device.
    The plaintext device mapper target will be created as needed during the
    Ansible run to ensure the filesystem on it is present. When it was not
    available prior to this Ansible run, it will be stopped at the end of the
    role run again.
    So basically, this option never changes the mounted/unmounted state of the
    plaintext device mapper target or the plaintext mount point of the
    filesystem.
    Note that this option will not fail when the ciphertext block device is not
    available during the Ansible run and the keyfile has not been generated by Ansible.
    This was done to allow to provision remote systems with keys for ciphertext block
    devices which have been setup previously and are not available during
    execution of this role.

    Note that if the encrypted filesystem is not mounted when this option is
    used then this role will not be idempotent because the crypto layer needs
    to be opened in order to check if the filesystem has been created on top of
    it.

  .. _cryptsetup__devices_state_absent:

  ``absent``
    Same as :ref:`unmounted <cryptsetup__devices_state_unmounted>` but
    additionally removes all configuration, the keyfile and the header backup
    from the remote system.

.. _cryptsetup__devices_hash:

``hash``
  Optional, string. Specifies the hash used in the LUKS key setup scheme and
  volume key digest for :command:`cryptsetup luksFormat`.
  Defaults to :envvar:`cryptsetup__hash`.

.. _cryptsetup__devices_cipher:

``cipher``
  Optional, string. Cipher specification.
  Defaults to :envvar:`cryptsetup__cipher`.

.. _cryptsetup__devices_key_size:

``key_size``
  Optional, int. Key size in bits.
  Defaults to :envvar:`cryptsetup__key_size`.

.. _cryptsetup__devices_iter_time:

``iter_time``
  Optional, int. The number of milliseconds to spend with PBKDF2 passphrase processing.
  Defaults to :envvar:`cryptsetup__iter_time`.

Examples
~~~~~~~~

Setup an encrypted filesystem on top of :file:`/dev/sdb5` which will be mounted
after role execution under :file:`/media/sdb5_crypt` and will be automatically
mounted at boot:

.. code:: yaml

   cryptsetup__devices:

     - name: 'sdb5_crypt'
       ciphertext_block_device: '/dev/sdb5'
