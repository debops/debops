Guides and examples
===================

.. include:: ../../../includes/global.rst

.. contents::
   :local:
   :depth: 2

Be sure that you :ref:`installed <cryptsetup__ref_installation>` the role and
setup your Ansible project to use the role
(:ref:`cryptsetup__ref_getting_started`).
There is also the :ref:`Getting Started guide <getting-started>` to learn the basics.

.. _cryptsetup__ref_guide_setup_loop_device:

Setup an encrypted loop device
------------------------------

For testing purposes `loop devices`_ can be used to get started with this role. Note that loop devices are not required, regular files also work.
So lets create a loop device:

.. code-block:: shell

   truncate --size=42M /tmp/example1_loop_file.raw
   losetup --show --find /tmp/example1_loop_file.raw

The printed loop device will be our `ciphertext block device`
(:ref:`cryptsetup__ref_overview_terminology`).
:file:`/dev/loop0` is assumed from now on.
Note that the role and cryptsetup can also use a regular file as `ciphertext block device`
directly.

Now you can use one of the :ref:`cryptsetup__devices` variables as listed in
the :ref:`cryptsetup__ref_defaults` documentation.
We are going to use :envvar:`cryptsetup__host_devices` which is intended to go
into the Ansible inventory file of a host (:file:`./ansible/inventory/host_vars/$hostname`).
You can use an entry like this:

.. code-block:: jinja

   cryptsetup__host_devices:

     - name: 'example1'
       ciphertext_block_device: '/dev/loop0'

The role should be "enabled" for this host as
shown in :ref:`cryptsetup__ref_example_inventory`.
Then run the playbook of the role:

.. code-block:: shell

   debops service/cryptsetup -l "$hostname"

which should have the following effects:

* Create a random keyfile on the Ansible controller under :file:`./ansible/secret/cryptsetup/$hostname/example1/keyfile.raw`
* Copy the keyfile to the remote host under :file:`/var/local/keyfiles/example1_keyfile.raw`
* Initialize LUKS by creating a LUKS header on :file:`/dev/loop0` using the keyfile
* Make a backup of the LUKS header on the remote host under :file:`/var/backups/luks_header_backup/example1_header_backup.raw`
* Copy the LUKS header backup to the Ansible controller under :file:`./ansible/secret/cryptsetup/$hostname/example1/header_backup.raw`
* Open/map :file:`/dev/loop0` to :file:`/dev/mapper/example1` (`Plaintext device mapper target`)
* Make the opening/mapping persistent in :file:`/etc/crypttab`
  (either for automatic opening on system start or manually using
  :command:`cryptdisks_start` which can be chosen by additional role
  configuration options)
* Create a filesystem on :file:`/dev/mapper/example1`
* Create the mount point directory for the filesystem under :file:`/media/example1`
* Mount :file:`/dev/mapper/example1` under :file:`/media/example1` (`Plaintext mount point of the filesystem`)
* Remember the filesystem information and mount point in :file:`/etc/fstab`

All of those tasks are idempotent so you can run the role repetitively against
the host and the role will not reformat the filesystem nor reinitialize LUKS
on the device.

If the LUKS header has been changed between role runs, the role
picks up the changed header and updates the two backups of it.
The task "Store the header backup in secret directory on to the Ansible
controller" will signal a changed header with the task state "changed".

You can check that the `plaintext mount point of the filesystem` is mounted using:

.. code-block:: shell

   df -h | egrep '(^Filesystem|example1)'

which should show something like:

.. code-block:: none

   Filesystem            Size  Used Avail Use% Mounted on
   /dev/mapper/example1   35M  491K   32M   2% /media/example1

You can now use :file:`/media/example1` to store files which are transparently encrypted and saved on :file:`/dev/loop0` (respectively :file:`/tmp/example1_loop_file.raw`).

.. _cryptsetup__ref_guide_teardown_device:

Teardown an encrypted device
----------------------------

One nice part of using an encrypted filesystem is that access to the plaintext
files can quickly be denied.  This is supported by the role. You just need to
change the inventory configuration of a configured device.
Using the example from :ref:`cryptsetup__ref_guide_setup_loop_device` this
could look like the following:

.. code-block:: jinja

   cryptsetup__host_devices:

     - name: 'example1'
       ciphertext_block_device: '/dev/loop0'
       state: 'absent'

Then run the playbook of the role:

.. code-block:: shell

   debops service/cryptsetup -l "$hostname"

which should have the following effects:

* Unmount :file:`/media/example1`
* Remove the filesystem information and mount point from :file:`/etc/fstab`
* Remove the mount point directory :file:`/media/example1`
* Close/unmap :file:`/dev/mapper/example1`
* Remove the `ciphertext block device` information from :file:`/etc/crypttab`
* Shredder the keyfile on the remote host under :file:`/var/local/keyfiles/example1_keyfile.raw`
* Shredder the header backup on the remote host under :file:`/var/backups/luks_header_backup/example1_header_backup.raw`

Note that shredder means to overwrite the file 42 times before removing
it. Depending on where those files where stored that might not have the desired
effect.

After the role run terminated, no access to plaintext files should be possible.
If you want to access the plaintext files again, just change the ``state`` and
rerun the role as all required information are still stored on the Ansible controller.
