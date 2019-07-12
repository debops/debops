.. _debops.ipxe:

debops.ipxe
===========

The `iPXE`__ project provides an open source network boot firmware. It can be
used to boot computers over the network using DHCP, PXE and TFTP protocols, and
hand off the boot process to other operating systems provided over HTTP, NFS or
iSCSI protocols.

.. __: https://ipxe.org/

The ``debops.ipxe`` Ansible role installs the ``ipxe`` APT package and prepares
a simple boot menu which can be used to either launch the Debian Installer over
the network, or switch to another publicly available network boot menu.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.ipxe/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
