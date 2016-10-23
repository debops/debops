Guides and examples
===================

.. include:: includes/all.rst

.. contents::
   :local:
   :depth: 2

Be sure that you :ref:`installed <cryptsetup__ref_installation>` the role and
setup your Ansible project to use the role
(:ref:`cryptsetup__ref_getting_started`).
There is also the `Getting Started with DebOps`_ guide to learn the basics.

.. _cryptsetup__ref_guide_setup_loop_device:

Setup a encrypted loop device
-----------------------------

For testing purposes `loop devices`_ can be used to get started with this role.
So lets create a loop device:

.. code-block:: shell

   truncate --size=42M /tmp/ciphertext_guide_loop_file.raw
   losetup "$(losetup --find)" /tmp/ciphertext_guide_loop_file.raw
   losetup --all

:command:`losetup --all` tells you which loop device the empty
:file:`/tmp/ciphertext_guide_loop_file.raw` file is mapped to.
That loop device will be our `ciphertext block device`
(:ref:`cryptsetup__ref_overview_terminology`).
:file:`/dev/loop0` is assumed from now on.

Now you can use one of the :ref:`cryptsetup__devices` variables as listed in
the :ref:`cryptsetup__ref_default_variables` documentation.
We are going to use :envvar:`cryptsetup__host_devices` which is intended to go
into the Ansible inventory file of one host that enabled this role for as
documented under :ref:`cryptsetup__ref_example_inventory`. So you can use
something like this:

.. code-block:: jinja

   cryptsetup__devices:

     - name: 'ciphertext_guide'
       ciphertext_block_device: '/dev/loop0'

Then run the playbook of the role:

.. code-block:: shell

   debops service/cryptsetup -l hostname

which should have the following effects:

* Create a random keyfile on the Ansible controller under :file:`./ansible/secret/cryptsetup/clouddrive.template/ciphertext_guide/keyfile.raw`
* Copy the keyfile to the remote host under :file:`/var/local/keyfiles/ciphertext_guide_keyfile.raw`
* Initialize LUKS on the :file:`/dev/loop0` using the keyfile
* Make a backup of the LUKS header on the remote host under :file:`/var/backups/luks_header_backup/ciphertext_guide_header_backup.raw`
* Copy the LUKS header backup to the Ansible controller under :file:`./ansible/secret/cryptsetup/clouddrive.template/ciphertext_guide/header_backup.raw`
* Open/map :file:`/dev/loop0` to :file:`/dev/mapper/ciphertext_guide` (`Plaintext device mapper target`)
* Make the opening/mapping permanent in :file:`/etc/crypttab`
  (either for automatic opening on system start or manually using
  :command:`cryptdisks_start` which can be chosen by additional role
  configuration options)
* Create a file system on :file:`/dev/mapper/ciphertext_guide`
* Create the mount point for the file system under :file:`/media/ciphertext_guide`
* Mount :file:`/dev/mapper/ciphertext_guide` under :file:`/media/ciphertext_guide` (`Plaintext mount point of the filesystem`)
* Remember the file system information and mount point in :file:`/etc/fstab`

All of those tasks are idempotent so you can run the role repetitively against
the host and the role will not reformat the file system nor reinitialize LUKS
on the device. If the LUKS header has been changed between role runs, the role
should pick up the changed header and update the two backups of it.

You can check that the `plaintext mount point of the filesystem` is mounted using:

.. code-block:: shell

   df -h | egrep '(^Filesystem|ciphertext_guide)'

which should show something like:

.. code-block:: none

   Filesystem                    Size  Used Avail Use% Mounted on
   /dev/mapper/ciphertext_guide   35M  491K   32M   2% /media/ciphertext_guide

You can now use :file:`/dev/mapper/ciphertext_guide` to store files which are transparently encrypted and saved on :file:`/dev/loop0` (respectively :file:`/tmp/ciphertext_guide_loop_file.raw`).

.. _cryptsetup__ref_guide_teardown_device:

Teardown a encrypted device on a remote system
----------------------------------------------

One nice part of using a encrypted file system is that access to the plaintext files can quickly be denied.
This is supported by the role. You just need to change the inventory
configuration of the device configured in
:ref:`cryptsetup__ref_guide_setup_loop_device` into this:

.. code-block:: jinja

   cryptsetup__devices:

     - name: 'ciphertext_guide'
       ciphertext_block_device: '/dev/loop0'
       state: 'absent'

Then run the playbook of the role:

.. code-block:: shell

   debops service/cryptsetup -l hostname

which should have the following effects:

* Unmount :file:`/dev/mapper/ciphertext_guide`
* Remove the file system information and mount point from :file:`/etc/fstab`
* Remove the mount point directory :file:`/media/ciphertext_guide`
* Close/unmap :file:`/dev/mapper/ciphertext_guide`
* Remove the `ciphertext block device` information from :file:`/etc/crypttab`
* Shredder keyfile on the remote host under :file:`/var/local/keyfiles/ciphertext_guide_keyfile.raw`
* Shredder the header backup on the remote host under :file:`/var/backups/luks_header_backup/ciphertext_guide_header_backup.raw`
  (This is technically not needed as the LUKS header is still present and
  left intact on the `ciphertext block device`, but ``absent`` is designed to
  remove all files/traces previously created by the role. Note that one copy of
  the LUKS header is still present on the Ansible controller)

Note that shredder means that to overwrite the file 42 times before removing
it. Depending on where those files where stored that might not have the desired
effect.

After the role run terminated, no access to plaintext files should be possible.
If you want to access the plaintext files again, just change the ``state`` and
rerun the role.
