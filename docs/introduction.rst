Introduction
============

This role allows you to configure a encrypted filesystem on top of any given
block device using `dm-crypt`_/`cryptsetup`_ and `LUKS`_.  A random keyfile generated on the Ansible
controller will be used for the encryption by default.  It is your
responsibility that the keyfile is kept secure for this to make sense.  For
example by storing the keyfile on an already encrypted filesystem (both on
the Ansible controller and the remote system).

.. _LUKS: https://en.wikipedia.org/wiki/Linux_Unified_Key_Setup
.. _dm-crypt: https://en.wikipedia.org/wiki/Dm-crypt
.. _cryptsetup: https://gitlab.com/cryptsetup/cryptsetup

* Create a random keyfile or use an already existing file.
* Manage :file:`/etc/crypttab` and :file:`/etc/fstab`.
* Create a LUKS header backup and store it on the Ansible controller.

The following layers are involved in configuring an encrypted filesystem using
block device encryption:

#. Ciphertext block device: This can be any block device or partition on a block device.
#. Plaintext device mapper target: Created by `dm-crypt`_ under :file:`/etc/mapper/`.
#. Plaintext mount point of the filesystem: Where the plaintext files can be accessed.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v1.9.0``. To install it, run::

    ansible-galaxy install debops.cryptsetup

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
