.. _cryptsetup__ref_default_variable_details:

Default variable details
========================

.. include:: ../../../includes/global.rst
.. include:: includes/role.rst

.. contents::
   :local:
   :depth: 2


Some of ``debops.cryptsetup`` variables have more extensive configuration.
Here you can find documentation and examples for them.


.. _cryptsetup__devices:

cryptsetup__devices
-------------------

The :envvar:`cryptsetup__devices` and similar lists allow you to specify
device configuration. The order can be important because
:ref:`devices depend on each other <cryptsetup__ref_devices_chaining_multiple_ciphers>`
and this will determine the order in which the devices appear in :file:`/etc/crypttab`.

Note the following list only documents the common parameters. The role allows
you to use more specific parameters which are not documented below.

Each item of those lists is a dictionary with the following documented keys:

.. _cryptsetup__devices_name:

``name``
  Required, string. Name of the `plaintext device mapper target` and the mount point
  (unless overwritten by :ref:`item.mount <cryptsetup__devices_mount>`).
  Must be unique among all device mapper targets and should not be changed once
  it was used.

  If you want to change it, you can set :ref:`state <cryptsetup__devices_state>`
  to :ref:`absent <cryptsetup__devices_state_absent>`, execute the role, rename
  the secrets directory corresponding to the name, adapt your inventory
  accordingly and run the role again to configure the item with the new name.

.. _cryptsetup__devices_ciphertext_block_device:

``ciphertext_block_device``
  Required, string. File path to the `ciphertext block device`, either the block
  device itself e. g. :file:`/dev/sdb`, a partition on the block device e. g.
  :file:`/dev/sdb5` or a regular file e. g. :file:`/tmp/ciphertext_file.raw`.

  Refer to :ref:`item.use_uuid <cryptsetup__devices_use_uuid>` when you use a
  regular file.

.. _cryptsetup__devices_use_uuid:

``use_uuid``
  Optional, boolean.
  Use the UUID of the `ciphertext block device` in :file:`/etc/crypttab` instead
  of the file path given by
  :ref:`item.ciphertext_block_device <cryptsetup__devices_ciphertext_block_device>`.

  Note that this needs to be set to ``False`` if you are using a regular file
  as :ref:`item.ciphertext_block_device <cryptsetup__devices_ciphertext_block_device>`.

  Default to :envvar:`cryptsetup__use_uuid`.

.. _cryptsetup__devices_mode:

``mode``
  Optional, string. The mode in which :command:`cryptsetup` should operate.
  Supported modes/extensions:

  * ``plain``
  * ``luks``
  * ``tcrypt``
  * ``veracrypt``

  Defaults to ``luks``. There is no global variable to change this default.
  Refer to :man:`cryptsetup(8)` for more details.

.. _cryptsetup__devices_offset:

``offset``
  Optional, integer start offset of the `ciphertext block device` which will be
  mapped to block 0 of the `plaintext device mapper target`.
  This option only has an effect in ``plain`` :ref:`item.mode <cryptsetup__devices_mode>`.
  There is no offset by default.

.. _cryptsetup__devices_crypttab_options:

``crypttab_options``
  Optional, list of strings. Each string represents an option to configure for
  the device in :file:`/etc/crypttab`. See :man:`crypttab(5)` for details.
  Default to :envvar:`cryptsetup__crypttab_options`.

  Note that :command:`cryptsetup` options need to be specified using their corresponding
  parameters as documented in this section. If an option is not documented
  here, that is where you can use ``crypttab_options`` for.
  For example :ref:`item.hash <cryptsetup__devices_hash>` could also be
  specified using ``hash=sha256`` as value for ``crypttab_options`` but
  this is not supported.

.. _cryptsetup__devices_keyfile:

``keyfile``
  Optional, string. File path for the keyfile on the Ansible controller. Will
  be copied over to the remote system. If it does not exist yet it will be
  generated using the systems random number generator on the Ansible controller
  as it is expected that the entropy pool on the Ansible controller is better
  mixed.
  Defaults to:

  .. code:: jinja

     {{ cryptsetup__secret_path + "/" + item.name + "/keyfile.raw" }}

.. _cryptsetup__devices_remote_keyfile:

``remote_keyfile``
  Optional, string. File path for the keyfile on the remote system.
  If this option is given it will be used directly and the
  :ref:`keyfile <cryptsetup__devices_state_unmounted>` will have no effect.
  It is expected that this file is already present on the remote system.
  Also note that the remote keyfile is not copied or backed up anywhere. The
  given file path is just used for opening/mapping the device.
  This option can also be a device path which will be used by dm-crypt to read
  the key like :file:`/dev/urandom`, note however that LUKS requires a
  persistent key and therefore does not support random data keys.
  If a :ref:`state <cryptsetup__devices_state>` is set which causes the device
  to become absent, the given remote keyfile will be made absent as well (but
  only if it is a regular file)!
  This option does not work with the
  :ref:`ansible_controller_mounted state <cryptsetup__devices_state_ansible_controller_mounted>`
  and the role will abort immediately if that combination is used.

.. _cryptsetup__devices_keyfile_gen_type:

``keyfile_gen_type``
  Optional, string. Type of keyfile to generate. This does not effect already
  generated keyfiles.
  Defaults to :envvar:`cryptsetup__keyfile_gen_type`.

  ``binary``
    A binary keyfile will be generated using :command:`dd` from the random
    source specified by :envvar:`cryptsetup__keyfile_source_dev`.
    This should ensure the maximum amount of entropy for keyfiles.

  ``text``
    The keyfile will be a random passphrase only consisting of printable
    characters suitable for automated or by-hand input.
    :ref:`item.keyfile_gen_command <cryptsetup__devices_keyfile_gen_command>`
    will be used to output the passphrase.

    Refer to the :ref:`example for adding another boot disk to a FDE system
    <cryptsetup__ref_devices_add_boot_disk_to_fde_system>` for how this can be
    used.

.. _cryptsetup__devices_keyfile_gen_command:

``keyfile_gen_command``
  Optional, string. The command which should be used to generate the keyfile
  when :ref:`item.keyfile_gen_type <cryptsetup__devices_keyfile_gen_type>` is set to
  ``text``. The command is expected to output one line to STDOUT.

  Note that all newline characters (``\n``) are removed using :command:`tr -d
  '\\n'` internally so that the generated text key can be entered as regular
  passphrase.
  This is required because most CLI programs properly end their output with a newline.
  But when :command:`cryptsetup` reads the key from a keyfile (which is what
  this role always uses internally), it does not terminate input when reading a
  newline. When reading from STDIN or from a terminal, it does however
  terminate on the first newline and uses the passphrase with the trailing
  newline stripped.  Refer to :man:`cryptsetup(8)` under :regexp:`Notes on
  passphrase processing for (plain mode|LUKS)`.

  Defaults to :envvar:`cryptsetup__keyfile_gen_command`.

.. _cryptsetup__devices_backup_header:

``backup_header``
  Optional, boolean. Should a header backup be created and stored
  on the remote system and the Ansible controller?

  .. note:: The LUKS header is only stored once in the first few kilobytes of
     a given block device.
     When the header gets corrupted, the plaintext data might be inaccessible!
     Thus it is recommended to have a header backup on hand.

     Debian buster and newer ship with Cryptsetup >2.0 which defaults to the LUKS2 format that provides redudancy of metadata.
     For security reasons, there is no redundancy in keyslots binary data
     (encrypted keys) but the format allows adding such a feature in future.
     Thus it is still recommended to have a header backup on hand.

  Set to ``False`` to disable header backup creation and to ensure that the
  header backup is absent on the remote system.
  This option only has an effect in ``luks`` :ref:`item.mode <cryptsetup__devices_mode>`.
  For TrueCrypt/VeraCrypt you will need to create header backups manually!
  Defaults to :envvar:`cryptsetup__header_backup`.

.. _cryptsetup__devices_swap:

``swap``
  Optional, boolean. Should the device be used as encrypted swap space?
  When set to ``True``, the option
  :ref:`item.manage_filesystem <cryptsetup__devices_manage_filesystem>`
  is ignored.
  Refer to :ref:`debops.sysctl` for paging and swapping related kernel settings.
  Defaults to ``False``.

  Refer to the :ref:`example for an encrypted swap partition using a random key
  <cryptsetup__ref_devices_swap_with_random_key>` for how this can be
  used.

.. _cryptsetup__devices_swap_priority:

``swap_priority``
  Optional, integer. Default swap device priority, from ``-1`` to ``32767``.
  Higher numbers indicate higher priority.
  Refer to :man:`swapon(8)` for details.
  Defaults to :envvar:`cryptsetup__swap_priority`.

.. _cryptsetup__devices_swap_options:

``swap_options``
  Optional, list of strings. Additional swap "mount" options.
  Not :ref:`item.mount_options <cryptsetup__devices_mount_options>` nor any
  other global default value is being used for swap options.

.. _cryptsetup__devices_manage_filesystem:

``manage_filesystem``
  Optional, boolean. Should a filesystem be created on the plaintext device mapper
  target and configured in :file:`/etc/fstab`?
  Defaults to ``True``.

.. _cryptsetup__devices_create_filesystem:

``create_filesystem``
  Optional, boolean. Should a filesystem be created on the plaintext device mapper
  target? Allows to only disable the creation of the filesystems but still
  manage an existing filesystem in :file:`/etc/fstab` when
  :ref:`item.manage_filesystem <cryptsetup__devices_manage_filesystem>` is ``True``.
  Defaults to :ref:`item.manage_filesystem <cryptsetup__devices_manage_filesystem>`.

.. _cryptsetup__devices_fstype:

``fstype``
  Optional, string. Filesystem to create on the plaintext device mapper
  target and configure in :file:`/etc/fstab`.
  Defaults to :envvar:`cryptsetup__fstype`.

.. _cryptsetup__devices_mount:

``mount``
  Optional, string. `Plaintext mount point of the filesystem`.
  Defaults to:

  .. code:: jinja

    {{ cryptsetup__mountpoint_parent_directory + "/" + item.name }}

.. _cryptsetup__devices_mount_options:

``mount_options``
  Optional, list of strings. Mount options associated with the filesystem.
  For more details see :man:`mount(8)`.
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
    keyfile to the remote system and erases it again without checking before
    hand if the `plaintext device mapper target` is already present.

  .. _cryptsetup__devices_state_unmounted:

  ``unmounted``
    Ensure that the encryption and filesystem layer are in place on the block device and
    the filesystem is unmounted. Additionally ensures that the cryptsetup mapping
    is removed so that no direct access to the plain-text block device is possible.

  .. _cryptsetup__devices_state_present:

  ``present``
    Ensure that the encryption and filesystem layer are in place on the block device.
    The `plaintext device mapper target` will be created and opened as needed during the
    Ansible run to ensure the filesystem on it is present. When the `plaintext
    device mapper target` was not opened prior to the Ansible run, then it will
    be stopped at the end of the role run again.
    So basically, this option never changes the mounted/unmounted state of the
    `plaintext device mapper target` or the `plaintext mount point of the
    filesystem`.
    Note that this option will not fail when the `ciphertext block device` is not
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
  Optional, string.
  Specifies the passphrase hash.
  For the ``luks`` :ref:`item.mode <cryptsetup__devices_mode>` it
  specifies the hash used in the LUKS key setup scheme and
  volume key digest for :command:`cryptsetup luksFormat`.
  Defaults to :envvar:`cryptsetup__hash`.

.. _cryptsetup__devices_cipher:

``cipher``
  Optional, string. Cipher specification.
  Defaults to :envvar:`cryptsetup__cipher`.

.. _cryptsetup__devices_key_size:

``key_size``
  Optional, integer. Key size in bits.
  Defaults to :envvar:`cryptsetup__key_size`.

.. _cryptsetup__devices_iter_time:

``iter_time``
  Optional, int. The number of milliseconds to spend with PBKDF2 passphrase processing.
  This option only has an effect in ``luks`` :ref:`item.mode <cryptsetup__devices_mode>`.
  Defaults to :envvar:`cryptsetup__iter_time`.

Example for encrypting a partition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Setup an encrypted filesystem on top of :file:`/dev/sdb5` which will be mounted
after role execution under :file:`/media/sdb5_crypt` and will be automatically
mounted at boot:

.. code:: yaml

   cryptsetup__devices:

     - name: 'sdb5_crypt'
       ciphertext_block_device: '/dev/sdb5'

.. _cryptsetup__ref_devices_swap_with_random_key:

Example for an encrypted swap partition using a random key
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Setup an encrypted swap partition which uses a new random key picked at each boot.
Hibernation won’t work with that as the system won’t have access to the
cleartext swap data the next time it starts as a new random key is being used
to decrypt/encrypt the device on each boot.

.. code:: yaml

   cryptsetup__devices:

     - name: 'rand_key_swap0'
       mode: 'plain'
       swap: True
       remote_keyfile: '/dev/urandom'
       ciphertext_block_device: '/dev/disk/by-partuuid/a7a12244-a4aa-42b7-b605-997165b3fbac'


.. _cryptsetup__ref_devices_tmp_with_random_key:

Example for an encrypted /tmp using a random key
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Setup an encrypted :file:`/tmp` which uses a new random key picked at each boot.
A new filesystem will be created on each boot. By default ``ext4`` will be used.

.. code:: yaml

   cryptsetup__devices:

     - name: 'rand_key_tmp'
       mode: 'plain'
       mount: '/tmp'
       remote_keyfile: '/dev/urandom'
       ciphertext_block_device: '/dev/disk/by-partuuid/a7a12244-a4aa-42b7-b605-997165b3fbac'
       create_filesystem: False
       crypttab_options: '{{ ["tmp"] + (cryptsetup__crypttab_options|d([]) | list) }}'
       # crypttab_options: '{{ ["tmp=" + cryptsetup__fstype] + (cryptsetup__crypttab_options|d([]) | list) }}'
       ## This seems to not work with Debian jessie (results in systemd waiting forever for the cleartext target).
       ## Using "tmp" instead worked.


.. _cryptsetup__ref_devices_header_backup_of_fde_system:

Example for making a header backup of an existing FDE system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you installed the OS using FDE and thus the encrypted filesystem was created
by the installer you might still want to make a header backup.
This can be done by setting :ref:`remote_keyfile <cryptsetup__devices_remote_keyfile>`
to ``none`` so that you will
still be asked for the passphrase at boot and to avoid keyfile generation.
Additionally :ref:`manage_filesystem <cryptsetup__devices_manage_filesystem>`
should be set to ``False`` so that an existing filesystem is not checked
against :ref:`fstype <cryptsetup__devices_fstype>`.

.. code:: yaml

   cryptsetup__devices:

     - name: 'vdb3_crypt'
       ciphertext_block_device: '/dev/disk/by-partuuid/55d1da1d-e1b0-4022-b17a-3b73cdc89286'
       manage_filesystem: False
       remote_keyfile: 'none'


.. _cryptsetup__ref_devices_add_boot_disk_to_fde_system:

Example for adding another boot disk to a FDE system with a different passphrase for both
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In case you installed a FDE system on one disk and want to create a redundant
setup afterwards by adding another disk, encrypting it and re-balancing a SOTA_
filesystem (Btrfs or ZFS) or growing a legacy RAID setup to it you can follow
this example.

For this setup it is required that the added disk can be decrypted in the
initramfs to assemble the root filesystem. To make this easier a passphrase
will be used as keyfile instead of the default binary keyfile.

Using a passphrase also makes it easier to automate the key input at boot
using FDEunlock_ which is also described in this example. You can ignore/remove
the custom :ref:`keyfile <cryptsetup__devices_keyfile>` setting if you don’t
use FDEunlock_.

The :ref:`keyfile <cryptsetup__devices_keyfile>` is generated in the
:file:`keys` directory of the default ``FileVault`` implementation of FDEunlock_.
Refer to FDEunlock_ for details.

``inventory_hostname`` can be used to make the configuration of the ``keyfile``
option easier to copy/paste.
Note that ``inventory_hostname`` is used here because we don’t want to "to rely
on the discovered hostname ``ansible_hostname`` or for other mysterious reasons"
which the (ref: `Magic Variables, and How To Access Information About Other
Hosts`_). Seems we just found such a "mysterious reason".
It is hoped that ``inventory_hostname`` is not spoofable because if it where,
the role might hand out keys for others hosts to a host exploiting this
potential vulnerability. You can set the keyfile manually if you want.

However, there is one issue to note here. The role normally configures devices
to unlock them by keyfile or disable keyfile handling completely (when using
:ref:`remote_keyfile <cryptsetup__devices_remote_keyfile>`). In this example, a
combination of both would be nice so that the role creates the crypto layer
with the provided keyfile but does not configure it in :file:`/etc/crypttab`.
This is not directly supported and the role can not be extended easily to fully
support this because of the internal role design. Changing that is not intended
only to support this use case.

Also, this use case requires that the passphrase is never saved anywhere on
persistent storage on the remote host.

There is a workaround which meets these requirements by making use of the
:ref:`ansible_controller_mounted state <cryptsetup__devices_state_ansible_controller_mounted>`.

You will need two role runs with slightly changed configuration for this. For
the first run, use something like this to ensure that the crypto layer is present and opened:

.. code:: yaml

   cryptsetup__devices:

     - name: 'sdb4_crypt'
       ciphertext_block_device: '/dev/disk/by-partuuid/3b014afe-1581-11e7-b65d-00163e5e6c0f'
       keyfile_gen_type: 'text'
       manage_filesystem: False
       keyfile: '/home/user/.config/fdeunlock/keys/{{ inventory_hostname }}-initramfs_dev_disk_by-partuuid_3b014afe-1581-11e7-b65d-00163e5e6c0f.key'

       ## Disable for initial setup else enable it:
       # remote_keyfile: 'none'

       ## Enable for initial setup else disable it:
       state: 'ansible_controller_mounted'

Now we will need the role to fix the entry in :file:`/etc/crypttab` so that the
passphrase is asked for on boot:

.. code:: yaml

   cryptsetup__devices:

     - name: 'sdb4_crypt'
       ciphertext_block_device: '/dev/disk/by-partuuid/3b014afe-1581-11e7-b65d-00163e5e6c0f'
       keyfile_gen_type: 'text'
       manage_filesystem: False
       keyfile: '/home/user/.config/fdeunlock/keys/{{ inventory_hostname }}-initramfs_dev_disk_by-partuuid_3b014afe-1581-11e7-b65d-00163e5e6c0f.key'

       ## Disable for initial setup else enable it:
       remote_keyfile: 'none'

       ## Enable for initial setup else disable it:
       # state: 'ansible_controller_mounted'

You should now be left with a decrypted ``sdb4_crypt`` `plaintext device mapper
target` for which the key only exists in
:file:`/home/user/.config/fdeunlock/keys/{{ inventory_hostname }}-initramfs_dev_disk_by-partuuid_3b014afe-1581-11e7-b65d-00163e5e6c0f.key`
on the Ansible controller.


Example for adding another boot disk to a FDE system with the same passphrase for both
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section is very similar to the previous example and you are expected to have understood it to not have to repeat everything here. Compared to the previous section which configured two disks for automated decryption using external network tools, this example configures multiple disks for manual passphrase entering by a human. The idea therefore is to use the same passphrase for the disks.

There are two options to provide the passphrase. Either :command:`cryptsetup luksFormat` the disks manually and then open the crypto layer with the expected name. Alternatively provide the passphrase on the Ansible controller in :file:`{{ cryptsetup__secret_path }}/sdX5_crypt_passphrase.txt` for example.

If you provided the passphrase on the Ansible controller, you will need the workaround as in the previous example by making use of the
:ref:`ansible_controller_mounted state <cryptsetup__devices_state_ansible_controller_mounted>`. The role will need to be run two times with slightly changed configuration. For
the first run, use something like this to ensure that the crypto layer is present and opened:

.. code:: yaml

   cryptsetup__devices:

     - name: 'sdb4_crypt'
       ciphertext_block_device: '/dev/disk/by-partuuid/6114134e-4796-11ea-8ec1-00163e5e6c00'
       manage_filesystem: False
       keyfile: '{{ cryptsetup__secret_path }}/sdX5_crypt_passphrase.txt'

       ## Disable for initial setup else enable it:
       # remote_keyfile: 'root_fs'
       # crypttab_options: '{{ ["keyscript=decrypt_keyctl"] + (cryptsetup__crypttab_options|d([]) | list) }}'

       ## Enable for initial setup else disable it:
       state: 'ansible_controller_mounted'

Now we will need the role to fix the entry in :file:`/etc/crypttab` so that the
passphrase is asked only once on boot.
The ``keyfile`` parameter does nothing at this point with ``remote_keyfile`` specified so if you don’t want to store the passphrase on the Ansible controller and did :command:`cryptsetup luksFormat` manually, then feel free to omit ``keyfile``.

.. code:: yaml

   cryptsetup__devices:

     - name: 'sdb4_crypt'
       ciphertext_block_device: '/dev/disk/by-partuuid/6114134e-4796-11ea-8ec1-00163e5e6c00'
       manage_filesystem: False
       keyfile: '{{ cryptsetup__secret_path }}/sdX5_crypt_passphrase.txt'

       ## Disable for initial setup else enable it:
       remote_keyfile: 'root_fs'
       crypttab_options: '{{ ["keyscript=decrypt_keyctl"] + (cryptsetup__crypttab_options|d([]) | list) }}'

       ## Enable for initial setup else disable it:
       # state: 'ansible_controller_mounted'


.. _cryptsetup__ref_devices_chaining_multiple_ciphers:

Example for chaining multiple ciphers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Setup a vault using three different ciphers and three different keys.
A similar feature is supported by TrueCrypt/VeraCrypt.

Note that order is important here and that the
:envvar:`cryptsetup__devices_execution_strategy` option has to be set to ``serial``
when using such an example.

.. code:: yaml

   cryptsetup__devices_execution_strategy: 'serial'
   cryptsetup__devices:

     ## Use AES for the most outer layer to not rise suspicion just yet :)
     - name: 'vault_ciphertext0'
       ciphertext_block_device: '/tmp/ciphertext_vault_file.raw'
       manage_filesystem: False
       # Don’t try to use a UUID for a regular file.
       use_uuid: False

     - name: 'vault_ciphertext1'
       ciphertext_block_device: '/dev/mapper/vault_ciphertext0'
       manage_filesystem: False
       cipher: 'twofish-xts-plain64'
       key_size: 512

     - name: 'vault'
       ciphertext_block_device: '/dev/mapper/vault_ciphertext1'
       cipher: 'serpent-xts-plain64'
       key_size: 512

This will encrypt :file:`/tmp/ciphertext_vault_file.raw` using the default cipher
(:envvar:`cryptsetup__cipher` which defaults to AES) and make the "clear text" of
that outer layer available under :file:`/dev/mapper/vault_ciphertext0`.
:file:`/dev/mapper/vault_ciphertext0` is then en/decrypted using Twofish and the
"clear text" of that is mapped to :file:`/dev/mapper/vault_ciphertext1`.
:file:`/dev/mapper/vault_ciphertext1` is then en/decrypted using Serpent and
mapped to the real clear text block device
:file:`/dev/mapper/vault` on which a filesystem will be created
and which will be mounted as usual.

This is surely a more extreme example but it has been tested in a lab
environment and the setup seems to work just fine. Also automatic
mapping/mounting of all layers works seamlessly on system boot if configured to
do so (which is the default).

You can even boot from such a chained number of devices but you might need to
manually list the ``vault_ciphertext`` device(s) in
:file:`/etc/initramfs-tools/conf.d/cryptroot`. At least on Debian Stretch this
is required.
:command:`mkinitramfs -k -o /tmp/initramfs_tmp` and :command:`cat
/var/tmp/mkinitramfs_$XXXX/conf/conf.d/cryptroot` can help you to see if the
full chain is known to the initramfs. If so, regenerate the actual initramfs
and reboot to test it.

The list of cyphers and key sizes can be checked with :command:`cryptsetup benchmark`.
You can check that the ciphers are chained as expected using :command:`cryptsetup status
vault`, :command:`cryptsetup status vault_ciphertext1` and so on.

If you intend to do this then note that in most scenarios the used cipher(s)
will not be your weakest link. For example AES should be suitable on it’s own
to provide reasonable `Information Security`_. You must also think about other
areas of `Computer Security`_ and `Operations security`_ for this example to
make sense.


.. _cryptsetup__ref_devices_veracrypt:

Example for TrueCrypt/VeraCrypt encrypted devices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:command:`cryptsetup` supports to open TrueCrypt `ciphertext block devices` and
starting with :command:`cryptsetup` version 1.6.7 also VeraCrypt.
As TrueCrypt has been superseded by VeraCrypt, only the later one will be
mentioned in this section from now on.

Because VeraCrypt is uncommon in a purely GNU/Linux based environment
and is not packaged for Debian, this role does not interact
in any way with VeraCrypt. You don’t need to install it on hosts you run this role against.

You will need to use VeraCrypt for creation as :command:`cryptsetup` and this role do
not support this.
Note that currently only a passphrase is supported which can be passed in the
usual manner by writing it into the :ref:`keyfile
<cryptsetup__devices_keyfile>` on the Ansible controller.
The keyfile should not contain newline characters (``\n``), see
:ref:`item.keyfile_gen_command <cryptsetup__devices_keyfile_gen_command>`.
Note that you will need to create a header backup manually!

Because VeraCrypt is great for platform portability, you might choose a
different filesystem as done in this example:

.. code:: yaml

   cryptsetup__devices:
     - name: 'mydatadisk'
       ciphertext_block_device: '/dev/disk/by-partuuid/65ca7bc4-6cb7-11e7-b49b-00163e5e6c0f'
       mode: 'veracrypt'
       fstype: 'ntfs'
       create_filesystem: False
       mount_options: '{{ cryptsetup__mount_options + ["umask=027", "fmask=117", "uid=1000", "gid=1000"] }}'
