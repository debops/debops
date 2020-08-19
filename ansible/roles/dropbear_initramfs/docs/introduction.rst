Introduction
============

.. include:: includes/all.rst

The ``debops-contrib.dropbear_initramfs`` role allows you to setup SSH access
to the initramfs prior to the root filesystem being mounted using Dropbear_ as
SSH server.

This can be used to unlock a full disk encrypted host remotely via SSH.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.1.4``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops-contrib.dropbear_initramfs

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
