Introduction
============

.. include:: ../../../includes/global.rst

``debops.cryptsetup`` allows you to configure encrypted filesystems on top of
any given block device using `dm-crypt`_/`cryptsetup`_ and `LUKS`_.  A random
keyfile generated on the Ansible controller will be used for the encryption by
default.  It is your responsibility that the keyfile is kept secure for this to
make sense.  For example by storing the keyfile on an already encrypted
filesystem (both on the Ansible controller and the remote system).

Features
~~~~~~~~

* Create a random keyfile or use an already existing keyfile.
* Manage :file:`/etc/crypttab` and :file:`/etc/fstab` and mount point directories.
* Create a LUKS header backup and store it on the Ansible controller.
* Decrypt and mount an encrypted filesystem and never store any key material on
  persistent storage on the remote system. You might need to take care of your
  Swap space yourself for this!
* Setup an encrypted swap space (with random key or with persistent key).
* Setup filesystems using a random key on boot.
* :command:`cryptsetup` plain, LUKS, TrueCrypt and VeraCrypt mode.
* Multiple ciphers and corresponding keys chained to encrypt one filesystem.

.. _cryptsetup__ref_installation:

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.1.4``. To install it, run::

    ansible-galaxy install debops.cryptsetup

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
